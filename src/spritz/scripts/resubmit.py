import os
import sys  # noqa: F401
import subprocess

from spritz.scripts.batch import (
    preprocess_chunks,
    submit
)

from spritz.framework.framework import (
    get_analysis_dict,
    get_fw_path,
)

def resubmit(
    job_idx_list=[],
    dryRun=False,
):
    print(f"resubmitting {len(job_idx_list)} jobs")
    print(sorted(job_idx_list))

    folders = []
    for idx in job_idx_list:
        folder_path = f"condor/job_{idx}"
        folders.append(folder_path.split('/')[-1])
        proc = subprocess.Popen(f"rm {folder_path}/*.txt", shell=True)
        proc.wait()

    with open("condor/submit.jdl", "r") as file:
        txtjdl = file.readlines()
    for i,line in enumerate(txtjdl):
        if line.startswith("queue 1 Folder in"):
            txtjdl[i] = f'queue 1 Folder in {", ".join(folders)}\n'

    with open("condor/resubmit.jdl", "w") as file:
        file.writelines(txtjdl)

    if dryRun:
        command = "cd condor/; chmod +x run.sh; cd -"
    else:
        command = "cd condor/; chmod +x run.sh; condor_submit resubmit.jdl; cd -"
    proc = subprocess.Popen(command, shell=True)
    proc.wait()

def main():
    start = 0
    path_an = os.path.abspath(".")
    an_dict = get_analysis_dict()
    chunks = preprocess_chunks(an_dict["year"])
    dryRun = False
    runner_name = an_dict["runner"] if "runner" in an_dict else f"{get_fw_path()}/src/spritz/runners/runner_default.py" 


    if len(sys.argv) > 1:
        dryRun = sys.argv[1] == "-dr"
        jobs = [i for i in sys.argv[1:] if not i == '-dr']
        
    resubmit(
        job_idx_list=jobs,
        dryRun=dryRun,
    )


if __name__ == "__main__":
    main()
