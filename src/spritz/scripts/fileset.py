import glob
import json
import os
import sys

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
                files[sampleName]["files"].append(
                    {"path": [found_file], "nevents": nevents}
                )

    return files


def main():
    an_dict = get_analysis_dict()
    era = an_dict["year"]
    datasets = [k["files"] for k in an_dict["datasets"].values()]
    files = get_files(era, datasets)
    print(files)
    rucio_client = rucio_utils.get_rucio_client()
    # DE|FR|IT|BE|CH|ES|UK
    good_sites = ["IT", "FR", "BE", "CH", "UK", "ES", "DE", "US"]
    for dname in files:
        if "query" not in files[dname]:
            continue
        dataset = files[dname]["query"]
        print("Checking", dname, "files with query", dataset)
        try:
            (
                outfiles,
                outsites,
                sites_counts,
            ) = rucio_utils.get_dataset_files_replicas(
                dataset,
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
            )
        except Exception as e:
            print(f"\n[red bold] Exception: {e}[/]")
            sys.exit(1)

        url = "https://cmsweb.cern.ch/dbs/prod/global/DBSReader"
        api = DbsApi(url=url)
        filelist = api.listFiles(dataset=dataset, detail=1)

        for replicas, _ in zip(outfiles, outsites):
            prefix = "/store/data"
            if prefix not in replicas[0]:
                prefix = "/store/mc"
            logical_name = prefix + replicas[0].split(prefix)[-1]

            right_file = list(
                filter(lambda k: k["logical_file_name"] == logical_name, filelist)
            )
            if len(right_file) == 0:
                raise Exception("File present in rucio but not dbs!", logical_name)
            if len(right_file) > 1:
                raise Exception(
                    "More files have the same logical_file_name, not support"
                )
            nevents = right_file[0]["event_count"]
            files[dname]["files"].append({"path": replicas, "nevents": nevents})

    os.makedirs("data", exist_ok=True)
    with open("data/fileset.json", "w") as file:
        json.dump(files, file, indent=2)


if __name__ == "__main__":
    main()
