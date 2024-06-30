import glob
import sys
import traceback as tb

from framework import add_dict, read_chunks, write_chunks

files = glob.glob("condor/job_*/chunks_job.pkl")
err = glob.glob("condor/job_*/err.txt")

jobs = list(map(lambda k: k.split("/")[-2], files))
# jobs_err = list(map(lambda k: k.split("/")[-2], err))
# jobs = list(set(jobs).intersection(jobs_err))
# jobs = list(set(jobs).intersection(jobs_err))


chunks = []
results = {}


def check_job(job_id):
    print("Checking", job_id)
    file = f"condor/{job_id}/chunks_job.pkl"
    file_backup = f"condor/{job_id}/chunks_job_original.pkl"
    try:
        chunks_backup = read_chunks(file_backup)
    except Exception as e:
        print(
            f"Could not open the backup file of {job_id}, won't work with this job",
            file=sys.stderr,
        )
        error = "".join(tb.format_exception(None, e, e.__traceback__))
        print(error, file=sys.stderr)
        return job_id
    chunks_total = 0
    chunks_err = 0
    results_chunk = {}
    try:
        chunks = read_chunks(file)
        assert isinstance(chunks, list)
        for i in range(len(chunks_backup)):
            chunks_total += 1
            if chunks[i]["result"] == {} and chunks[i]["error"] != "":
                chunks_err += 1
                break
            # else:
            #     results_chunk = add_dict(results_chunk, chunks[i]["result"])
        if chunks_total > 0 and chunks_err == 0:
            print("job is done")
            # results = add_dict(results, results_chunk)
        else:
            print("skipping job, should be retried")
            return job_id
    except Exception as e:
        return job_id


# write_chunks(results, "tmp.pkl")
import concurrent.futures

with concurrent.futures.ProcessPoolExecutor(max_workers=6) as pool:
    tasks = []
    for job_id in jobs:
        tasks.append(pool.submit(check_job, job_id))
    concurrent.futures.wait(tasks)
    failed = []
    for task in tasks:
        res = task.result()
        if res:
            failed.append(res)
    print(sorted(failed))
    print("queue 1 Folder in " + " ".join(sorted(failed)))
    print("Failed", len(failed))
    print("Total", len(failed))
