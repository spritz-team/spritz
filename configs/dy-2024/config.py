# ruff: noqa: E501

import json

import awkward as ak
import hist
import numpy as np
from spritz.framework.framework import cmap_pastel, cmap_petroff, get_fw_path
from spritz.plugins.hard_pu_jets import hardPUJets
from spritz.plugins.remove_gen_photon import removeGenPhoton

year = "Full2024v15"

fw_path = get_fw_path()

with open(f"{fw_path}/data/common/lumi.json") as file:
    lumis = json.load(file)

with open(f"{fw_path}/data/{year}/cfg.json") as file:
    txt = file.read()
    txt = txt.replace("RPLME_PATH_FW", fw_path)
    cfg = json.loads(txt)

# get lumis for single era: brilcalc lumi --normtag /cvmfs/cms-bril.cern.ch/cms-lumi-pog/Normtags/normtag_BRIL.json -u /fb -i /eos/user/c/cmsdqm/www/CAF/certification/Collisions24/2024C_Golden.json
lumi = lumis[year]["G"] / 1000
plot_label = "VBF-Z-EFT"
year_label = "2024"
njobs = 300


blind = False

runner = f"{fw_path}/src/spritz/runners/runner_eft.py"

th_variations = False
skip_variations = True

# th_variations = True
# skip_variations = False

special_analysis_cfg = {
    "skip_all_variations": skip_variations,
}

datasets = {}

subsamples_dy = {
    "PU": "events.PU",
    "hard": "events.hard",
}

for key in ["E", "Mu", "Tau"]:
    datasets[f"DY_NLO_{key}"] = {
        "files": f"DYto2{key}-2Jets_MLL-50",
        "task_weight": 8,
        # "subsamples": subsamples_dy,
        # "plugins": [hardPUJets, removeGenPhoton],
        "max_chunks": 100,
    }

# top_datasets = ["TTTo2L2Nu", "TWplusto2L2Nu", "TWminusto2L2Nu"]  # noqa: E501
# top_datasets = ["TTTo2L2Nu", "TWminusto2L2Nu"]  # noqa: E501
top_datasets = ["TTTo2L2Nu"]  # noqa: E501
for ds in top_datasets:
    datasets[ds] = {
        "files": ds,
        "task_weight": 8,
        "max_chunks": 100,
    }

for dataset in datasets:
    datasets[dataset]["read_form"] = "mc"


DataRun = [
    # ["C", "Run2024C-ReReco-v1"],
    # ["D", "Run2024D-ReReco-v1"],
    # ["E", "Run2024E-ReReco-v1"],
    # ["F", "Run2024F-Prompt-v1"],
    ["G", "Run2024G-Prompt-v1"],
    # ["H", "Run2024H-Prompt-v1"],
    # ["I", "Run2024I-Prompt-v1"],
]

# # DataSets = ["MuonEG", "SingleMuon", "EGamma", "DoubleMuon"]
# # DataTrig = {
# #     "MuonEG": "events.EleMu",
# #     "DoubleMuon": "(~events.EleMu) & events.DoubleMu",
# #     "SingleMuon": "(~events.EleMu) & (~events.DoubleMu) & events.SingleMu",
# #     "EGamma": "(~events.EleMu) & (~events.DoubleMu) & (~events.SingleMu) & (events.SingleEle | events.DoubleEle)",
# # }

DataSets = ["MuonEG", "Muon0", "Muon1", "EGamma0", "EGamma1"]

DataTrig = {
    "MuonEG": "(events.EleMu)",
    "Muon0": "(~events.EleMu) & (events.SingleMu | events.DoubleMu)",
    "Muon1": "(~events.EleMu) & (events.SingleMu | events.DoubleMu)",
    "EGamma0": "(~events.EleMu) & (~(events.SingleMu | events.DoubleMu)) & (events.SingleEle | events.DoubleEle)",
    "EGamma1": "(~events.EleMu) & (~(events.SingleMu | events.DoubleMu)) & (events.SingleEle | events.DoubleEle)",
    # "JetMET0": "(~(events.SingleMu | events.DoubleMu)) & (~(events.SingleEle | events.DoubleEle))",
    # "JetMET1": "(~(events.SingleMu | events.DoubleMu)) & (~(events.SingleEle | events.DoubleEle))"
}

subsamples_data = {
    "prompt": "events.l2Tight",
    # "fake": ("ak.ones_like(events.run) == 1", "events.fakeWeight"),
    # "fake_weight1": "ak.ones_like(events.run) == 1",
}

samples_data = []
for era, sd in DataRun:
    for pd in DataSets:
        tag = pd + "_" + sd

        # # FIXME limit to only first era
        # if era != "B":
        #     continue

        datasets[f"{pd}_{era}"] = {
            "files": tag,
            "trigger_sel": DataTrig[pd],
            "read_form": "data",
            "is_data": True,
            "era": f"2024{era}",
            "subsamples": subsamples_data,
            # "max_chunks": 1,
        }
        samples_data.append(f"{pd}_{era}")


samples = {}
colors = {}

samples["Data"] = {
    "samples": [f"{k}_prompt" for k in samples_data],
    "is_data": True,
}

# for key in subsamples_dy:
#     samples[f"DY-{key}"] = {
#         "samples": [f"DY_NLO_{lep}_{key}" for lep in ["E", "Mu", "Tau"]],
#         # "is_signal": True,
#     }
#     colors[f"DY-{key}"] = cmap_petroff[0] if key == "hard" else cmap_petroff[3]

samples["DY"] = {
    "samples": [f"DY_NLO_{lep}" for lep in ["E", "Mu", "Tau"]],
    # "is_signal": True,
}
colors["DY"] = cmap_petroff[0] if key == "hard" else cmap_petroff[3]

samples["Top"] = {"samples": [ds for ds in top_datasets]}
colors["Top"] = cmap_petroff[1]

# regions

regions = {}
preselections = (  # noqa E731
    lambda events: (events.mll > 50)
    # & (events.njet >= 2)
    # & (events.mjj > 200)
    # & (events.ptj1 > 30)
    # & (events.ptj2 > 30)
)

top_mll_cut = lambda events: (abs(events.mll - 91) >= 15)  # noqa: E731
# top_mll_cut = lambda events: (abs(events.mll - 91) >= 10)  # noqa: E731

# regions["top_cr_ee"] = {
#     "func": lambda events: preselections(events)
#     & top_mll_cut(events)
#     & events.bTag
#     & events.ee,
#     "mask": 0,
# }

regions["cr_inc_ee"] = {
    "func": lambda events: preselections(events)
    & (abs(events.mll - 91) < 15)
    & events.ee,
    "mask": 0,
}

regions["cr_inc_mm"] = {
    "func": lambda events: preselections(events)
    & (abs(events.mll - 91) < 15)
    & events.mm,
    "mask": 0,
}

regions["cr_inc_em"] = {
    "func": lambda events: preselections(events)
    & (abs(events.mll - 91) < 15)
    & events.e_mu,
    "mask": 0,
}

# regions["dy_2j_mm"] = {
#     "func": lambda events: preselections(events)
#     & (abs(events.mll - 91) < 15)
#     & (events.njet >= 2)
#     & (events.mjj > 200)
#     & (events.ptj1 > 30)
#     & (events.ptj2 > 30)
#     & events.mm,
#     "mask": 0,
# }

variables = {}

variables["npvs"] = {
    "func": lambda events: events.PV.npvsGood,
    "axis": hist.axis.Regular(101, -0.5, 100.5, name="npvs"),
}


# def func_tightlep(events):
#     lep = ak.pad_none(events.Lepton, 2, clip=True)
#     return ak.num(lep[ak.fill_none(lep.is_tight_wp, False)])


# variables["Ntight_leptons"] = {
#     "func": func_tightlep,
#     "axis": hist.axis.Regular(3, -0.5, 2.5, name="Ntight_leptons"),
#     "skip_fill": True,
# }

# variables["njet"] = {
#     "func": lambda events: events.njet,
#     "axis": hist.axis.Regular(6, 0, 6, name="njet"),
# }

# Dijet
variables["mjj"] = {
    "func": lambda events: ak.fill_none(
        (events.jets[:, 0] + events.jets[:, 1]).mass, -9999
    ),
    "axis": hist.axis.Regular(30, 200, 1500, name="mjj"),
}
variables["ptjj"] = {
    "func": lambda events: ak.fill_none(
        (events.jets[:, 0] + events.jets[:, 1]).pt, -9999
    ),
    # "axis": hist.axis.Regular(30, 0, 300, name="ptjj"),
}
variables["detajj"] = {
    "func": lambda events: abs(
        ak.fill_none(events.jets[:, 0].deltaeta(events.jets[:, 1]), -9999)
    ),
    "axis": hist.axis.Regular(30, 0, 10, name="detajj"),
}


variables["dphijj"] = {
    "func": lambda events: abs(
        ak.fill_none(events.jets[:, 0].deltaphi(events.jets[:, 1]), -9999)
    ),
    "axis": hist.axis.Regular(30, 0, np.pi, name="dphijj"),
}
# variables["dphijj_noabs"] = {
#     "func": lambda events: abs(
#         ak.fill_none(events.jets[:, 0].deltaphi(events.jets[:, 1]), -9999)
#     ),
#     "axis": hist.axis.Regular(30, -2 * np.pi, 2 * np.pi, name="dphijj"),
# }

# Single jet
variables["ptj1"] = {
    "func": lambda events: ak.fill_none(events.jets[:, 0].pt, -9999),
    "axis": hist.axis.Regular(30, 30, 500, name="ptj1"),
}
variables["ptj2"] = {
    "func": lambda events: ak.fill_none(events.jets[:, 1].pt, -9999),
    "axis": hist.axis.Regular(30, 30, 500, name="ptj2"),
}
variables["etaj1"] = {
    "func": lambda events: ak.fill_none(events.jets[:, 0].eta, -9999),
    "axis": hist.axis.Regular(30, -5, 5, name="etaj1"),
    # "skip_fill": True,
}
variables["etaj2"] = {
    "func": lambda events: ak.fill_none(events.jets[:, 1].eta, -9999),
    "axis": hist.axis.Regular(30, -5, 5, name="etaj2"),
    # "skip_fill": True,
}
variables["phij1"] = {
    "func": lambda events: ak.fill_none(events.jets[:, 0].phi, -9999),
    "axis": hist.axis.Regular(30, -np.pi, np.pi, name="phij1"),
    # "skip_fill": True,
}
variables["phij2"] = {
    "func": lambda events: ak.fill_none(events.jets[:, 1].phi, -9999),
    "axis": hist.axis.Regular(30, -np.pi, np.pi, name="phij2"),
    # "skip_fill": True,
}


# Dilepton
variables["mll"] = {
    "func": lambda events: (events.Lepton[:, 0] + events.Lepton[:, 1]).mass,
    "axis": hist.axis.Regular(50, 91 - 15, 91 + 15, name="mll"),
}

variables["ptll"] = {
    "func": lambda events: (events.Lepton[:, 0] + events.Lepton[:, 1]).pt,
    "axis": hist.axis.Regular(30, 0, 500, name="ptll"),
}
variables["detall"] = {
    "func": lambda events: abs(events.Lepton[:, 0].deltaeta(events.Lepton[:, 1])),
    "axis": hist.axis.Regular(20, 0, 10, name="detall"),
}
variables["dphill"] = {
    "func": lambda events: abs(events.Lepton[:, 0].deltaphi(events.Lepton[:, 1])),
    "axis": hist.axis.Regular(30, 0, np.pi, name="dphill"),
}
# variables["dphill_noabs"] = {
#     "func": lambda events: (events.Lepton[:, 0].deltaphi(events.Lepton[:, 1])),
#     "axis": hist.axis.Regular(30, -2 * np.pi, 2 * np.pi, name="dphill"),
# }

# Single lepton
variables["ptl1"] = {
    "func": lambda events: events.Lepton[:, 0].pt,
    "axis": hist.axis.Regular(30, 15, 150, name="ptl1"),
}
variables["ptl2"] = {
    "func": lambda events: events.Lepton[:, 1].pt,
    "axis": hist.axis.Regular(30, 15, 150, name="ptl2"),
}
variables["etal1"] = {
    "func": lambda events: events.Lepton[:, 0].eta,
    "axis": hist.axis.Regular(30, -2.5, 2.5, name="etal1"),
    # "skip_fill": True,
}
variables["etal2"] = {
    "func": lambda events: events.Lepton[:, 1].eta,
    "axis": hist.axis.Regular(30, -2.5, 2.5, name="etal2"),
    # "skip_fill": True,
}
variables["phil1"] = {
    "func": lambda events: events.Lepton[:, 0].phi,
    "axis": hist.axis.Regular(30, -np.pi, np.pi, name="phil1"),
    # "skip_fill": True,
}
variables["phil2"] = {
    "func": lambda events: events.Lepton[:, 1].phi,
    "axis": hist.axis.Regular(30, -np.pi, np.pi, name="phil2"),
    # "skip_fill": True,
}

# variables["Zeppenfeld_l1"] = {
#     "func": lambda events: ak.fill_none(
#         (events.Lepton[:, 0].eta) - (events.jets[:, 0].eta - events.jets[:, 1].eta) / 2,
#         -9999.0,
#     ),
# }
# variables["Zeppenfeld_l2"] = {
#     "func": lambda events: ak.fill_none(
#         (events.Lepton[:, 1].eta) - (events.jets[:, 0].eta - events.jets[:, 1].eta) / 2,
#         -9999.0,
#     ),
# }
variables["Zeppenfeld_Z"] = {
    "func": lambda events: ak.fill_none(
        0.5
        * abs(
            (events.Lepton[:, 0].eta + events.Lepton[:, 1].eta)
            - (events.jets[:, 0].eta + events.jets[:, 1].eta)
        ),
        -9999.0,
    ),
    "axis": hist.axis.Regular(30, 0, 3, name="Zeppenfeld_Z"),
    # "skip_fill": True,
}

variables["MET"] = {
    "func": lambda events: events.PuppiMET.pt,
    "axis": hist.axis.Regular(30, 0, 150, name="MET"),
    # "skip_fill": True,
}

# variables["weight"] = {
#     "func": lambda events: events["weight"],
# }
variables["events"] = {
    "func": lambda events: ak.ones_like(events.run),
    "axis": hist.axis.Regular(1, 0, 1.0, name="events"),
    "label": "Events",
}

variables["dr_jj"] = {
    "func": lambda events: ak.fill_none(
        events.jets[:, 0].deltaR(events.jets[:, 1]), -9999
    ),
    "axis": hist.axis.Regular(30, 0, 5, name="dr_jj"),
    # "skip_fill": True,
}

# variables["dr_j1l1"] = {
#     "func": lambda events: ak.fill_none(
#         events.jets[:, 0].deltaR(events.Lepton[:, 0]), -9999
#     ),
#     "axis": hist.axis.Regular(30, 0, 5, name="dr_j1l1"),
#     "skip_fill": True,
# }

# variables["dr_j1l2"] = {
#     "func": lambda events: ak.fill_none(
#         events.jets[:, 0].deltaR(events.Lepton[:, 1]), -9999
#     ),
#     "axis": hist.axis.Regular(30, 0, 5, name="dr_j1l2"),
#     "skip_fill": True,
# }

# variables["dr_j2l1"] = {
#     "func": lambda events: ak.fill_none(
#         events.jets[:, 1].deltaR(events.Lepton[:, 0]), -9999
#     ),
#     "axis": hist.axis.Regular(30, 0, 5, name="dr_j2l1"),
#     "skip_fill": True,
# }

# variables["dr_j2l2"] = {
#     "func": lambda events: ak.fill_none(
#         events.jets[:, 1].deltaR(events.Lepton[:, 1]), -9999
#     ),
#     "axis": hist.axis.Regular(30, 0, 5, name="dr_j2l2"),
#     "skip_fill": True,
# }


nuisances = {}
mcs = [sample for sample in samples if not samples[sample].get("is_data", False)]


nuisances["lumi_Uncorrelated"] = {
    "name": "lumi_13TeV_2018",
    "type": "lnN",
    "samples": dict((skey, "1.015") for skey in ["VV", "Int"]),
}

nuisances["lumi_Correlated"] = {
    "name": "lumi_13TeV_correlated",
    "type": "lnN",
    "samples": dict((skey, "1.020") for skey in ["VV", "Int"]),
}

nuisances["lumi_1718"] = {
    "name": "lumi_13TeV_1718",
    "type": "lnN",
    "samples": dict((skey, "1.002") for skey in ["VV", "Int"]),
}


## Use the following if you want to apply the automatic combine MC stat nuisances.
nuisances["stat"] = {
    "type": "auto",
    # "maxPoiss": "0",
    # "includeSignal": "1",
    "maxPoiss": "50",
    "includeSignal": "0",
    #  nuisance ['maxPoiss'] =  Number of threshold events for Poisson modelling
    #  nuisance ['includeSignal'] =  Include MC stat nuisances on signal processes (1=True, 0=False)
    "samples": {},
}
