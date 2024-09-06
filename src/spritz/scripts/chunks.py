import json
import random
from math import ceil

from spritz.framework.framework import get_analysis_dict, write_chunks


def split_chunks(num_entries):
    chunksize = 100_000
    nIterations = ceil(num_entries / chunksize)
    file_results = []
    for i in range(nIterations):
        start = min(num_entries, chunksize * i)
        stop = min(num_entries, chunksize * (i + 1))
        if start >= stop:
            break
        file_results.append([start, stop])
    return file_results


def get_files(datasets):
    with open("data/fileset.json", "r") as file:
        files = json.load(file)

    for dataset in datasets:
        datasets[dataset]["files"] = files[datasets[dataset]["files"]]["files"]
    return datasets


def create_chunks(datasets):
    chunks = []
    for dataset in datasets:
        is_data = datasets[dataset].get("is_data", False)
        max_chunks = datasets[dataset].get("max_chunks", None)
        files = datasets[dataset]["files"]
        dataset_dict = {
            k: v
            for k, v in datasets[dataset].items()
            if k != "files" and k != "task_weight"
        }
        chunks_dataset = []
        for file in files:
            steps = split_chunks(file["nevents"])
            for start, stop in steps:
                replicas = file["path"]
                random.shuffle(replicas)
                d = {
                    "data": {
                        "dataset": dataset,
                        "filenames": replicas,
                        "start": start,
                        "stop": stop,
                        **dataset_dict,
                    },
                    "error": "",
                    "result": {},
                    "priority": 0,  # used for merging
                    "weight": datasets[dataset].get("task_weight", 1),
                }

                chunks_dataset.append(d)
        if not is_data and max_chunks:
            chunks_dataset = chunks_dataset[:max_chunks]
        chunks.extend(chunks_dataset)
    return chunks


def main():
    datasets = get_analysis_dict()["datasets"]
    datasets = get_files(datasets)
    chunks = create_chunks(datasets)
    print("Now got", len(chunks), "chunks")
    write_chunks(chunks, "data/chunks.pkl")


if __name__ == "__main__":
    main()
