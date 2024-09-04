import json
import sys

from spritz.framework.framework import add_dict, get_fw_path, read_events
from spritz.utils import rucio_utils

rucio_client = rucio_utils.get_rucio_client()

for era in ["Full2016v9HIPM", "Full2016v9noHIPM", "Full2017v9", "Full2018v9"]:
    dataset = "DYJetsToLL_2J"
    with open(f"../data/{era}/samples/samples.json") as file:
        samples = json.load(file)
    query = samples["samples"][dataset]["nanoAOD"]

    good_sites = ["IT", "FR", "BE", "CH", "UK", "ES", "DE", "US"]
    try:
        (
            outfiles,
            outsites,
            sites_counts,
        ) = rucio_utils.get_dataset_files_replicas(
            query,
            allowlist_sites=[],
            blocklist_sites=[
                # "T2_FR_IPHC",
                # "T2_ES_IFCA",
                # "T2_CH_CERN",
                "T3_IT_Trieste",
            ],
            regex_sites=r"T[123]_(" + "|".join(good_sites) + ")_\w+",
            mode="full",  # full or first. "full"==all the available replicas
            client=rucio_client,
        )
    except Exception as e:
        print(f"\n[red bold] Exception: {e}[/]")
        sys.exit(1)
    outfiles = list(filter(lambda k: len(k) > 0, outfiles))
    rootfile = outfiles[0][0]
    # sys.exit(0)

    with open(f"{get_fw_path()}/data/common/forms.json", "r") as file:
        forms_common = json.load(file)
    with open(f"{get_fw_path()}/data/{era}/forms.json", "r") as file:
        forms_era = json.load(file)
    forms = add_dict(forms_common, forms_era)

    print(rootfile)
    events = read_events(rootfile, 0, 100, forms["mc"])
    print(events.fields)
