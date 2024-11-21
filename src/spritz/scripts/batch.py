import json
import os
import subprocess
import sys  # noqa: F401

from spritz.framework.framework import (
    add_dict,
    get_analysis_dict,
    get_fw_path,
    read_chunks,
    write_chunks,
)


def preprocess_chunks(year):
    with open(f"{get_fw_path()}/data/common/forms.json", "r") as file:
        forms_common = json.load(file)
        print(forms_common)
    with open(f"{get_fw_path()}/data/{year}/forms.json", "r") as file:
        forms_era = json.load(file)
    forms = add_dict(forms_common, forms_era)
    new_chunks = read_chunks("data/chunks.pkl")

    for i, chunk in enumerate(new_chunks):
        new_chunks[i]["data"]["read_form"] = forms[chunk["data"]["read_form"]]
    return new_chunks


def split_chunks(chunks, n):
    """
    Splits list l of chunks into n jobs with approximately equals sum of values
    see  http://stackoverflow.com/questions/6855394/splitting-list-in-chunks-of-balanced-weight
    """
    jobs = [[] for i in range(n)]
    sums = {i: 0 for i in range(n)}
    c = 0
    for chunk in chunks:
        for i in sums:
            if c == sums[i]:
                jobs[i].append(chunk)
                break
        sums[i] += chunk["weight"]
        c = min(sums.values())
    return jobs


def submit(
    new_chunks,
    path_an,
    an_dict,
    njobs=500,
    clean_up=True,
    start=0,
    dryRun=False,
    script_name="script_worker.py",
):
    machines = [
        # # "clipper.hcms.it",
        # "pccms01.hcms.it",
        # "pccms02.hcms.it",
        "pccms04.hcms.it",
        # # "pccms08.hcms.it",
        # "pccms11.hcms.it",
        # "clipper.hcms.it",
        # "empire.hcms.it",
        "pccms12.hcms.it",
        "pccms13.hcms.it",
        "pccms14.hcms.it",
        # "hercules02.hcms.it",
    ]

    print("N chunks", len(new_chunks))
    print(sorted(list(set(list(map(lambda k: k["data"]["dataset"], new_chunks))))))

    jobs = split_chunks(new_chunks, njobs)
    print(len(jobs))

    folders = []

    if clean_up:
        proc = subprocess.Popen(
            "rm -r condor_backup; mv condor condor_backup",
            shell=True,
        )
        proc.wait()

    for i, job in enumerate(jobs):
        folder = f"condor/job_{start+i}"

        os.makedirs(folder, exist_ok=False)
        write_chunks(job, f"{folder}/chunks_job.pkl")
        write_chunks(job, f"{folder}/chunks_job_original.pkl")

        folders.append(folder.split("/")[-1])
    proc = subprocess.Popen(f"cp {script_name} condor/runner.py", shell=True)
    proc.wait()

    txtsh = "#!/bin/bash\n"
    txtsh += f"source {get_fw_path()}/start.sh\n"
    txtsh += f"time python runner.py {path_an}\n"

    with open("condor/run.sh", "w") as file:
        file.write(txtsh)

    txtjdl = "universe = vanilla \n"
    txtjdl += "executable = run.sh\n"
    txtjdl += "arguments = $(Folder)\n"

    txtjdl += "should_transfer_files = YES\n"
    txtjdl += "transfer_input_files = $(Folder)/chunks_job.pkl, "
    txtjdl += f"runner.py, {get_fw_path()}/data/{an_dict['year']}/cfg.json\n"
    txtjdl += 'transfer_output_remaps = "results.pkl = $(Folder)/chunks_job.pkl"\n'
    txtjdl += "output = $(Folder)/out.txt\n"
    txtjdl += "error  = $(Folder)/err.txt\n"
    txtjdl += "log    = $(Folder)/log.txt\n"
    txtjdl += "request_cpus=1\n"
    txtjdl += "request_memory=2000\n"
    if len(machines) > 0:
        txtjdl += (
            "Requirements = "
            + " || ".join([f'(machine == "{machine}")' for machine in machines])
            + "\n"
        )
    queue = "workday"
    txtjdl += f'+JobFlavour = "{queue}"\n'

    txtjdl += f'queue 1 Folder in {", ".join(folders)}\n'
    with open("condor/submit.jdl", "w") as file:
        file.write(txtjdl)

    if dryRun:
        command = "cd condor/; chmod +x run.sh; cd -"
    else:
        command = "cd condor/; chmod +x run.sh; condor_submit submit.jdl; cd -"
    proc = subprocess.Popen(command, shell=True)
    proc.wait()


def main():
    start = 0
    path_an = os.path.abspath(".")
    an_dict = get_analysis_dict()
    chunks = preprocess_chunks(an_dict["year"])
    runner_default = f"{get_fw_path()}/src/spritz/runners/runner_default.py"
    runner = an_dict.get("runner", runner_default)
    dryRun = False

    if len(sys.argv) > 1:
        dryRun = sys.argv[1] == "-dr"

    submit(
        chunks,
        path_an,
        an_dict,
        njobs=an_dict["njobs"],
        clean_up=True,
        start=start,
        dryRun=dryRun,
        script_name=runner,
    )


if __name__ == "__main__":
    main()
