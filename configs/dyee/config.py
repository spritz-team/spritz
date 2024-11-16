# ruff: noqa: E501

import json

import awkward as ak
import hist
import numpy as np
from spritz.framework.framework import cmap_pastel, cmap_petroff, get_fw_path

fw_path = get_fw_path()

year = "Full2018v9"
runner = f"{fw_path}/src/spritz/runners/runner_DYee.py"

with open(f"{fw_path}/data/common/lumi.json") as file:
    lumis = json.load(file)

lumi = lumis[year]["B"] / 1000  # ERA B of 2018
#lumi = lumis[year]["tot"] / 1000  # All of 2018
plot_label = "DYee"
year_label = "2018B"
njobs = 500

special_analysis_cfg = {
    "do_theory_variations": False,
}

bins = {
    "mll": np.linspace(60, 180, 50),
}

datasets = {
    "DYmm": {
        "files": "DYJetsToMuMu_M-50",
        "task_weight": 8,
    },
    "DYee": {
        "files": "DYJetsToEE_M-50",
        "task_weight": 8,
    },
    "DYtt": {
        "files": "DYJetsToTauTau_M-50_AtLeastOneEorMuDecay",
        "task_weight": 8,
    },
    "TTJets": {
        "files": "TTJets",
        "task_weight": 8,
    },
    "ST_s-channel": {
        "files": "ST_s-channel",
        "task_weight": 8,
    },
    "ST_t-channel_top_5f": {
        "files": "ST_t-channel_top_5f",
        "task_weight": 8,
    },
    "ST_t-channel_antitop_5f": {
        "files": "ST_t-channel_antitop_5f",
        "task_weight": 8,
    },
    "ST_tW_top_noHad": {
        "files": "ST_tW_top_noHad",
        "task_weight": 8,
    },
    "ST_tW_antitop_noHad": {
        "files": "ST_tW_antitop_noHad",
        "task_weight": 8,
    },
    "WW": {
        "files": "WW_TuneCP5_13TeV-pythia8",
        "task_weight": 8,
    },
    "WZ": {
        "files": "WZ_TuneCP5_13TeV-pythia8",
        "task_weight": 8,
    },
    "ZZ": {
        "files": "ZZ_TuneCP5_13TeV-pythia8",
        "task_weight": 8,
    },
    #"WJetsToLNu": {
    #    "files": "WJetsToLNu-LO",
    #    "task_weight": 8,
    #},
    "WJetsToLNu_0J": {
        "files": "WJetsToLNu_0J",
        "task_weight": 8,
    },
    "WJetsToLNu_1J": {
        "files": "WJetsToLNu_1J",
        "task_weight": 8,
    },
    "WJetsToLNu_2J": {
        "files": "WJetsToLNu_2J",
        "task_weight": 8,
    },
    "GGToLL": {
        "files": "GGToLL_M50",
        "task_weight": 8,
    }
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


samples = {
    "Data": {
        "samples": samples_data,
        "is_data": True,
    },
    "WJets": {
        #"samples": ["WJetsToLNu"]
        "samples": [
            "WJetsToLNu_0J",
            "WJetsToLNu_1J",
            "WJetsToLNu_2J"
        ]
    },
    "GGToLL": { 
        "samples": ["GGToLL"] 
    },
    "Top": {
        "samples": [
            "TTJets",
            "ST_s-channel",
            "ST_t-channel_top_5f",
            "ST_t-channel_antitop_5f",
            "ST_tW_top_noHad",
            "ST_tW_antitop_noHad"
        ]
    },
    "VV": {
        "samples": [
            "WW",
            "WZ",
            "ZZ"
        ]
    },
    "DYtt": {
        "samples": ["DYtt"]
    },
    "DYll": {
        "samples": [
            "DYmm",
            "DYee"
        ],
        "is_signal": True
    }
}

colors = {}

colors["WJets"] = cmap_petroff[0]
colors["GGToLL"] = cmap_petroff[1]
colors["Top"] = cmap_petroff[2]
colors["VV"] = cmap_petroff[3]
colors["DYtt"] = cmap_petroff[4]
colors["DYll"] = cmap_petroff[5]


# regions

preselections = (  # noqa E731
    lambda events: (events.mll > 60) & (events.mll < 180)
)

regions = {
    "inc_ee": {
        "func": lambda events: preselections(events) & events["ee"],
        "mask": 0
    },
    "inc_mm": {
        "func": lambda events: preselections(events) & events["mm"],
        "mask": 0
    }
}

variables = {
    # Dilepton
    "mll": {
        "func": lambda events: (events.Lepton[:, 0] + events.Lepton[:, 1]).mass,
        "axis": hist.axis.Regular(50, 60, 180, name="mll")
    },
    "ptll": {
        "func": lambda events: (events.Lepton[:, 0] + events.Lepton[:, 1]).pt,
        "axis": hist.axis.Regular(50, 0, 150, name="ptll"),
    },
    "etall": {
        "func": lambda events: (events.Lepton[:, 0] + events.Lepton[:, 1]).eta,
        "axis": hist.axis.Regular(50, -5, 5, name="etall"),
    },
    "phill": {
        "func": lambda events: (events.Lepton[:, 0] + events.Lepton[:, 1]).phi,
        "axis": hist.axis.Regular(50, -np.pi, np.pi, name="phill"),
    },
    "detall": {
        "func": lambda events: abs(events.Lepton[:, 0].deltaeta(events.Lepton[:, 1])),
        "axis": hist.axis.Regular(50, 0, 5, name="detall")
    },
    "dphill": {
        "func": lambda events: abs(events.Lepton[:, 0].deltaphi(events.Lepton[:, 1])),
        "axis": hist.axis.Regular(50, 0, np.pi, name="dphill")
    },
    # Single lepton
    "ptl1": {
        "func": lambda events: events.Lepton[:, 0].pt,
        "axis": hist.axis.Regular(50, 15, 150, name="ptl1")
    },
    "ptl2": {
        "func": lambda events: events.Lepton[:, 1].pt,
        "axis": hist.axis.Regular(50, 15, 150, name="ptl2")
    },
    "etal1": {
        "func": lambda events: events.Lepton[:, 0].eta,
        "axis": hist.axis.Regular(50, -2.5, 2.5, name="etal1")
    },
    "etal2": {
        "func": lambda events: events.Lepton[:, 1].eta,
        "axis": hist.axis.Regular(50, -2.5, 2.5, name="etal2")
    },
    "phil1": {
        "func": lambda events: events.Lepton[:, 0].phi,
        "axis": hist.axis.Regular(50, -np.pi, np.pi, name="phil1")
    },
    "phil2": {
        "func": lambda events: events.Lepton[:, 1].phi,
        "axis": hist.axis.Regular(50, -np.pi, np.pi, name="phil2")
    }
}

nuisances = {
    "lumi": {
        "name": "lumi",
        "type": "lnN",
        "samples": dict((skey, "1.02") for skey in samples)
    },
    ## Use the following if you want to apply the automatic combine MC stat nuisances
    "stat": {
        "type": "auto",
        "maxPoiss": "10",
        "includeSignal": "0",
        "samples": {}
    }
}

