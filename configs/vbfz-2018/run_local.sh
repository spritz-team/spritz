#!/bin/bash


cd condor/job_16

# configs/.../condor/job_0/tmp

mkdir tmp
cd tmp
cp ../chunks_job.pkl .
cp ../../run.sh .
cp ../../../script_worker_dumper.py .
cp ../../../../../data/Full2018v9/cfg.json .

./run.sh

