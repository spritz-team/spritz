#!/bin/bash

ERA="Full2016v9HIPM"
job_id=0

cd condor/job_${job_id}

# configs/.../condor/job_0/tmp

mkdir tmp
cd tmp
cp ../chunks_job.pkl .
cp ../../run.sh .
cp ../../../script_worker_dumper.py .
cp ../../../../../data/${ERA}/cfg.json .

./run.sh 
cp results.pkl ../chunks_job.pkl
echo "Run locally" > ../err.txt

