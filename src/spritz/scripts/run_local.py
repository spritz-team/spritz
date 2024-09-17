import subprocess

from spritz.framework.framework import get_analysis_dict, get_fw_path


def main():
    an_dict = get_analysis_dict()
    era = an_dict["year"]

    txt = """
    #!/bin/bash

    ERA=RPLME_ERA
    job_id=$1

    cd condor/job_${job_id}

    # configs/.../condor/job_0/tmp

    mkdir tmp
    cd tmp
    cp ../chunks_job.pkl .
    cp ../../run.sh .
    cp RPLME_FW_PATH/src/spritz/runners/script_worker_dumper.py .
    cp RPLME_FW_PATH/data/${ERA}/cfg.json .

    ./run.sh 2> err 1> out
    cp results.pkl ../chunks_job.pkl
    mv err ../err.txt
    mv out ../out.txt
    echo "Run locally" >> ../err.txt
    echo "Done ${job_id}"
    """
    with open("run_local.sh", "w") as file:
        file.write(
            txt.replace("RPLME_FW_PATH", get_fw_path()).replace("RPLME_ERA", era)
        )
    proc = subprocess.Popen("chmod +x run_local.sh", shell=True)
    proc.wait()
