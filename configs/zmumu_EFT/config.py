# ruff: noqa: E501

import json

import awkward as ak
import hist
import numpy as np
from spritz.framework.framework import cmap_pastel, cmap_petroff, get_fw_path


fw_path = get_fw_path()
with open(f"{fw_path}/data/common/lumi.json") as file:
    lumis = json.load(file)

year = "Full2018v9"
lumi = lumis[year]["B"] / 1000  # ERA C of 2017
# lumi = lumis[year]["tot"] / 1000  # All of 2017
plot_label = "ZmumuEFT"
year_label = "2018B"
njobs = 200

runner = f"{fw_path}/src/spritz/runners/runner_3DY.py"

special_analysis_cfg = {
    "do_theory_variations": False
}

bins = {
    "ptll": np.linspace(0, 200, 5),
    "mll": np.linspace(60, 200, 50)
}


datasets = {}

datasets["DYmm"] = {
    "files": "DYJetsToMuMu_M-50",
    "task_weight": 8
}

datasets["DYee"] = {
    "files": "DYJetsToEE_M-50",
    "task_weight": 8
}


datasets["DYtt"] = {
    "files": "DYJetsToTauTau_M-50_AtLeastOneEorMuDecay",
    "task_weight": 8
}


datasets["TTJets"] = {
    "files": "TTJets",
    "task_weight": 8
}

top_samples = [
        "ST_s-channel",
        "ST_t-channel_antitop_5f",
        "ST_t-channel_top_5f",
        "ST_tW_antitop_noHad",
        "ST_tW_top_noHad",
    ]

for i, sample in enumerate(
    top_samples
):
    datasets[sample] = {
        "files": sample,
        "task_weight": 8
    }

for sample in ["WW", "WZ", "ZZ"]:
    datasets[sample] = {
        "files": f"{sample}_TuneCP5_13TeV-pythia8",
        "task_weight": 8
    }

datasets["WJetsToLNu"] = {
    "files": "WJetsToLNu-LO",
    "task_weight": 8
}

datasets["GGToLL"] = {
    "files": "GGToLL_M50",
    "task_weight": 8
}


for dataset in datasets:
    datasets[dataset]["read_form"] = "mc"


DataRun = [
    #["A", "Run2018A-UL2018-v1"],
    ["B", "Run2018B-UL2018-v1"],
    #["C", "Run2018C-UL2018-v1"],
    #["D", "Run2018D-UL2018-v1"],
]

DataSets = ["SingleMuon", "EGamma", "DoubleMuon"]

DataTrig = {
    "DoubleMuon": "events.DoubleMu",
    "SingleMuon": "(~events.DoubleMu) & events.SingleMu",
    "EGamma": "(~events.DoubleMu) & (~events.SingleMu) & (events.SingleEle | events.DoubleEle)",
}


samples_data = []
for era, sd in DataRun:
    for pd in DataSets:
        tag = pd + "_" + sd

        # # FIXME limit to only first era
        # if era != "B":
        #     continue

        if (
            ("DoubleMuon" in pd and "Run2018B" in sd)
            or ("DoubleMuon" in pd and "Run2018D" in sd)
            or ("SingleMuon" in pd and "Run2018A" in sd)
            or ("SingleMuon" in pd and "Run2018B" in sd)
            or ("SingleMuon" in pd and "Run2018C" in sd)
        ):
            tag = tag.replace("v1", "v2")

        datasets[f"{pd}_{era}"] = {
            "files": tag,
            "trigger_sel": DataTrig[pd],
            "read_form": "data",
            "is_data": True,
            "era": f"UL2018{era}",
        }
        samples_data.append(f"{pd}_{era}")


samples = {}
colors = {}

samples["Data"] = {
    "samples": samples_data,
    "is_data": True,
}
#####
samples["WJetsToLNu"] = {
    "samples": ["WJetsToLNu"],
}
colors["WJetsToLNu"] = cmap_pastel[5]
#####
samples["GGToLL"] = {
    "samples": ["GGToLL"],
}
colors["GGToLL"] = cmap_pastel[6]
#####
samples["VV"] = {
    "samples": ["WW", "WZ", "ZZ"],
}
colors["VV"] = cmap_pastel[4]
#####
samples["Top"] = {
    "samples": [
        "TTJets",
    ]
    + top_samples,
}
colors["Top"] = cmap_pastel[3]
#####
samples["DYtt"] = {
    "samples": ["DYtt"],
}
colors["DYtt"] = cmap_pastel[2]
#####
samples["DYee"] = {
    "samples": ["DYee"],
}
colors["DYee"] = cmap_pastel[0]
#####
samples["DYmm"] = {
    "samples": ["DYmm"],
}
colors["DYmm"] = cmap_pastel[1]
#####




# regions
preselections = lambda events: (events.mll > 60) & (events.mll < 180)  # noqa E731

regions = {}

regions["inc_ee"] = {
    "func": lambda events: events["ee"],
    "mask": 0,
}

regions["inc_mm"] = {
    "func": lambda events: events["mm"],
    "mask": 0,
}

variables = {}

variables["mll"] = {
    "func": lambda events: (events.Lepton[:, 0] + events.Lepton[:, 1]).mass,
    "axis": hist.axis.Regular(50, 60, 180, name="mll"),
}

variables["ptll"] = {
    "func": lambda events: (events.Lepton[:, 0] + events.Lepton[:, 1]).pt,
    "axis": hist.axis.Regular(50, 0, 150, name="ptll"),
}

variables["etal1"] = {
    "func": lambda events: events.Lepton[:, 0].eta,
    "axis": hist.axis.Regular(50, -2.5, 2.5, name="etal1"),
}



nuisances = {
    "lumi": {
        "name": "lumi",
        "type": "lnN",
        "samples": dict((skey, "1.02") for skey in samples),
    },
}

## Use the following if you want to apply the automatic combine MC stat nuisances.
nuisances["stat"] = {
    "type": "auto",
    "maxPoiss": "10",
    "includeSignal": "0",
    "samples": {},
}
