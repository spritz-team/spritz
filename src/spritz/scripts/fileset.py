import concurrent.futures
import glob
import json
import os
import sys
import time

import uproot
from dbs.apis.dbsClient import DbsApi
from spritz.framework.framework import get_analysis_dict, get_fw_path
from spritz.utils import rucio_utils

path_fw = get_fw_path()


def get_files(era, active_samples):
    Samples = {}

    with open(f"{path_fw}/data/{era}/samples/samples.json") as file:
        Samples = json.load(file)
        if active_samples == "ALL":
            Samples = {k: v for k, v in Samples["samples"].items()}
        else:
            Samples = {
                k: v for k, v in Samples["samples"].items() if k in active_samples
            }
    print(Samples)
    for sample in active_samples:
        if sample not in Samples:
            raise Exception(f"Sample {sample} not found in samples.json")

    files = {}
    for sampleName in Samples:
        if "nanoAOD" in Samples[sampleName]:
            files[sampleName] = {"query": Samples[sampleName]["nanoAOD"], "files": []}
        elif "path" in Samples[sampleName]:
            files[sampleName] = {"files": []}
            found_files = glob.glob(Samples[sampleName]["path"])
            print(found_files)
            for found_file in found_files:
                f = uproot.open(found_file)
                nevents = f["Events"].num_entries
                f.close()
                files[sampleName]["files"].append(
                    {"path": [found_file], "nevents": nevents}
                )

    return files


def rucio_calls(files):
    url = "https://cmsweb.cern.ch/dbs/prod/global/DBSReader"
    dbs_api = DbsApi(url=url)

    rucio_client = rucio_utils.get_rucio_client()
    xrootd_sites_map = rucio_utils.get_xrootd_sites_map()
    good_sites = ["IT", "FR", "BE", "CH", "UK", "ES", "DE", "US"]
    default_kwargs = dict(
        allowlist_sites=[],
        blocklist_sites=[
            # "T2_FR_IPHC",
            # "T2_ES_IFCA",
            # "T2_CH_CERN",
            "T3_IT_Trieste",
        ],
        # regex_sites=[],
        regex_sites=r"T[123]_(" + "|".join(good_sites) + ")_\w+",
        # regex_sites = r"T[123]_(DE|IT|BE|CH|ES|UK|US)_\w+",
        mode="full",  # full or first. "full"==all the available replicas
        client=rucio_client,
        xrootd_sites_map=xrootd_sites_map,
    )
    _files = {k: v for k, v in files.items() if "query" in v}
    with concurrent.futures.ProcessPoolExecutor(max_workers=20) as pool:
        tasks = []
        for dname in _files:
            dataset = _files[dname]["query"]
            tasks.append(
                pool.submit(
                    rucio_utils.get_dataset_files_replicas, dataset, **default_kwargs
                )
            )
        concurrent.futures.wait(tasks)

        for dname, task in zip(_files, tasks):
            dataset_query = _files[dname]["query"]
            outfiles, outsites, _ = task.result()

            filelist = dbs_api.listFiles(dataset=dataset_query, detail=1)
            event_count_map = {
                k["logical_file_name"]: k["event_count"] for k in filelist
            }
            print(event_count_map)

            result = []
            for replicas, _ in zip(outfiles, outsites):
                prefix = "/store/data"
                if prefix not in replicas[0]:
                    prefix = "/store/mc"
                logical_name = prefix + replicas[0].split(prefix)[-1]
                try:
                    nevents = event_count_map[logical_name]
                except KeyError:
                    continue

                result.append({"path": replicas, "nevents": nevents})
            files[dname]["files"] = result

    return files


def main():
    an_dict = get_analysis_dict()
    era = an_dict["year"]
    datasets = [k["files"] for k in an_dict["datasets"].values()]
    files = get_files(era, datasets)
    print(files)
    files = rucio_calls(files)

    os.makedirs("data", exist_ok=True)
    with open("data/fileset.json", "w") as file:
        json.dump(files, file, indent=2)


if __name__ == "__main__":
    main()
