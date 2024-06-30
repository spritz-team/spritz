import json
import os
import random
import sys

import dask
import uproot
from coffea.dataset_tools import rucio_utils
from dbs.apis.dbsClient import DbsApi
from spritz.framework import path_fw


def get_files(year):
    Samples = {}

    path = os.path.abspath(f"{path_fw}/data/{year}/samples/")
    print("Working in analysis path:", path)
    sys.path.insert(0, path)
    exec(
        "from active_samples import active_samples",
        globals(),
        globals(),
    )

    with open(f"{path_fw}/data/{year}/samples/samples.json") as file:
        Samples = json.load(file)
        Samples = {k: v for k, v in Samples["samples"].items() if k in active_samples}  # noqa: F821

    files = {}
    for sampleName in Samples:
        files[sampleName] = {"query": Samples[sampleName]["nanoAOD"], "files": []}

    return files


if __name__ == "__main__":
    kwargs = {
        "bad_sites": [
            # "ts.infn",
        ],
    }
    year = "2018"
    files = get_files(year)
    print(files)
    rucio_client = rucio_utils.get_rucio_client()
    # DE|FR|IT|BE|CH|ES|UK
    good_sites = ["IT", "FR", "BE", "CH", "UK", "ES", "DE", "US"]
    for dname in files:
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

        # files[dname]["files"] = list(map(lambda k: k[0], outfiles))
        url = "https://cmsweb.cern.ch/dbs/prod/global/DBSReader"
        api = DbsApi(url=url)
        filelist = api.listFiles(dataset=dataset, detail=1)

        for replicas, site in zip(outfiles, outsites):
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

    with open("data/files_all3.json", "w") as file:
        json.dump(files, file, indent=2)
