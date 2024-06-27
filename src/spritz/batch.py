import json
import os
import subprocess
import sys  # noqa: F401

from framework import path_fw, read_chunks, write_chunks


def preprocess_chunks():
    with open("data/common/forms.json", "r") as file:
        forms = json.load(file)
    new_chunks = read_chunks("data/chunks.pkl")

    for i, chunk in enumerate(new_chunks):
        new_chunks[i]["data"]["read_form"] = forms[chunk["data"]["read_form"]]
        # dset = chunk["dataset"]
        # if chunk.get("is_data", False):
        #     new_chunks[i]["weight"] = 1
        # elif "Zjj" == dset:
        #     new_chunks[i]["weight"] = 8
        # elif "DY" in dset:
        #     new_chunks[i]["weight"] = 8
        # elif "top" in dset.lower() or "ttto" in dset.lower() or "st_s" in dset.lower():
        #     new_chunks[i]["weight"] = 3
        # else:
        #     print("No weight", dset)
        #     new_chunks[i]["weight"] = 1
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
        # # "pccms04.hcms.it",
        # # "pccms08.hcms.it",
        # "pccms11.hcms.it",
        # "pccms12.hcms.it",
        # # "pccms14.hcms.it",
    ]

    print("N chunks", len(new_chunks))
    print(sorted(list(set(list(map(lambda k: k["data"]["dataset"], new_chunks))))))

    jobs = split_chunks(new_chunks, njobs)
    print(len(jobs))
    # sys.exit()
    folders = []
    pathPython = os.path.abspath(".")
    pathResults = "/gwdata/users/gpizzati/condor_processor"

    if clean_up:
        proc = subprocess.Popen(
            f"rm -r condor_backup {pathResults}/results_backup; mv condor condor_backup; mv {pathResults}/results {pathResults}/results_backup",
            shell=True,
        )
        proc.wait()

    for i, job in enumerate(jobs):
        folder = f"condor/job_{start+i}"

        os.makedirs(folder, exist_ok=False)
        write_chunks(job, f"{folder}/chunks_job.pkl")
        write_chunks(job, f"{folder}/chunks_job_original.pkl")

        folders.append(folder.split("/")[-1])
    proc = subprocess.Popen(f"cp {script_name} condor/", shell=True)
    proc.wait()

    txtsh = "#!/bin/bash\n"
    # txtsh += "export X509_USER_PROXY=/gwpool/users/gpizzati/.proxy\n"

    # txtsh += "source /gwpool/users/gpizzati/mambaforge/etc/profile.d/conda.sh\n"
    # txtsh += "source /gwpool/users/gpizzati/mambaforge/etc/profile.d/mamba.sh\n"
    # txtsh += "mamba activate test_uproot\n"

    # txtsh += f"export PYTHONPATH={pathPython}:$PYTHONPATH\n"
    txtsh += f"source {path_fw}/setup.sh\n"
    # txtsh += "echo 'which python'\n"
    # txtsh += "which python\n"
    txtsh += f"time python {script_name}\n"
    # txtsh += f"cp results.pkl {pathResults}/results/results_$1.pkl\n"
    # txtsh += f"cp results.root {pathResults}/results/results_$1.root\n"
    # txtsh += f"ls {pathResults}/results/results_$1.pkl\n"
    # txtsh += f"ls {pathResults}/results/results_$1.root\n"

    with open("condor/run.sh", "w") as file:
        file.write(txtsh)

    txtjdl = "universe = vanilla \n"
    txtjdl += "executable = run.sh\n"
    txtjdl += "arguments = $(Folder)\n"

    txtjdl += "should_transfer_files = YES\n"
    txtjdl += f"transfer_input_files = $(Folder)/chunks_job.pkl, {script_name}, ../data/cfg.json\n"
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
        command = f"mkdir -p {pathResults}/results; cd condor/; chmod +x run.sh; cd -"
    else:
        command = f"mkdir -p {pathResults}/results; cd condor/; chmod +x run.sh; condor_submit submit.jdl; cd -"
    proc = subprocess.Popen(command, shell=True)
    proc.wait()


if __name__ == "__main__":
    start = 0
    chunks = preprocess_chunks()
    dryRun = False
    if len(sys.argv) > 1:
        dryRun = sys.argv[1] == "-dr"
    submit(
        chunks,
        njobs=500,
        clean_up=True,
        start=start,
        dryRun=dryRun,
        script_name="script_worker_dumper.py",
    )
