# ruff: noqa: E501

import json

import awkward as ak
import hist
import numpy as np
from spritz.framework.framework import cmap_pastel, cmap_petroff, get_fw_path

year = "Full2017v9"

fw_path = get_fw_path()

with open(f"{fw_path}/data/common/lumi.json") as file:
    lumis = json.load(file)

with open(f"{fw_path}/data/{year}/cfg.json") as file:
    txt = file.read()
    txt = txt.replace("RPLME_PATH_FW", fw_path)
    cfg = json.loads(txt)

# lumi = lumis[year]["C"] / 1000  # ERA C of 2017
lumi = lumis[year]["tot"] / 1000  # All of 2017
plot_label = "VBF-Z"
year_label = "2017"
njobs = 400


dnn_path = "/gwpool/users/gpizzati/test_processor/my_processor/notebooks/output_model"
special_analysis_cfg = {
    "do_theory_variations": True,
    "dnn": {
        "model": f"{dnn_path}/model.onnx",
        "scaler": f"{dnn_path}/scaler.txt",
        "cumulative_signal": f"{dnn_path}/cumulative_signal.root",
        "arrays_type": "np.float64",
        "output_node": "dense_4",
    },
}

subsamples_dy = {
    "hard": "events.hard",
    "PU": "events.PU",
}

bins = {
    "ptll": np.linspace(0, 200, 5),
    # "dphill": np.linspace(0, 3.14, 10),
    # "dphijj": np.linspace(0, 3.14, 10),
    # "mjj": np.linspace(200, 3000, 5),
    # "detajj": np.linspace(0, 8, 8),
}

subsamples_sig = {}
for variable in bins:
    for i in range(len(bins[variable]) - 1):
        col = f"events.Gen_{variable}"
        common_cut = "events.fiducial_cut"
        if i == 0:
            subsamples_sig[f"{variable}_{i}"] = (
                f"{common_cut} & ({col} <= {bins[variable][i+1]})"
            )
        elif i == len(bins[variable]) - 2:
            subsamples_sig[f"{variable}_{i}"] = (
                f"{common_cut} & ({col} > {bins[variable][i]})"
            )
        else:
            subsamples_sig[f"{variable}_{i}"] = (
                f"{common_cut} & ({col} > {bins[variable][i]}) & ({col} <= {bins[variable][i+1]})"
            )

subsamples_sig["outfiducial"] = "~events.fiducial_cut"
print(subsamples_sig)

datasets = {}


datasets["Zjj"] = {
    "files": "EWK_LLJJ_MLL-50_MJJ-120",
    "task_weight": 8,
    "subsamples": subsamples_sig,
}

datasets["Int"] = {
    "files": "EWK_LLJJ_MLL-50_MJJ-120_QCD",
}

# datasets["DY_NLO"] = {
#     "files": "DYJetsToLL_M-50",
#     "task_weight": 8,
#     "weight": "0.5",
#     "subsamples": subsamples_dy,
# }

for njet in [0, 1, 2]:
    datasets[f"DY-{njet}J"] = {
        "files": f"DYJetsToLL_{njet}J",
        "task_weight": 8,
        # "weight": "0.5",
        "subsamples": subsamples_dy,
    }

# # FIXME limit DY chunks
# for dataset in datasets:
#     if "DY" in dataset:
#         datasets[dataset]["max_chunks"] = 1000


datasets["TT"] = {
    "files": "TTTo2L2Nu",
    "task_weight": 8,
    "top_pt_rwgt": True,
}

for i, sample in enumerate(
    [
        "ST_s-channel",
        "ST_t-channel_antitop",
        "ST_t-channel_top",
        "ST_tW_antitop",
        "ST_tW_top",
    ]
):
    datasets[f"single_top_{i}"] = {
        "files": sample,
        "task_weight": 8,
    }

for sample in ["WW", "WZ", "ZZ"]:
    datasets[sample] = {
        "files": f"{sample}_TuneCP5_13TeV-pythia8",
        "task_weight": 8,
    }
for dataset in datasets:
    datasets[dataset]["read_form"] = "mc"


DataRun = [
    ["B", "Run2017B-UL2017-v1"],
    ["C", "Run2017C-UL2017-v1"],
    ["D", "Run2017D-UL2017-v1"],
    ["E", "Run2017E-UL2017-v1"],
    ["F", "Run2017F-UL2017-v1"],
]

DataSets = ["SingleMuon", "SingleElectron", "DoubleEG", "DoubleMuon"]

DataTrig = {
    "SingleMuon": "events.SingleMu",
    "SingleElectron": "(~events.SingleMu) & events.SingleEle",
    "DoubleMuon": "(~events.SingleMu) & (~events.SingleEle) & events.DoubleMu",
    "DoubleEG": "(~events.SingleMu) & (~events.SingleEle) & (~events.DoubleMu) & events.DoubleEle",
}


samples_data = []
for era, sd in DataRun:
    for pd in DataSets:
        tag = pd + "_" + sd

        # # FIXME limit to only first era
        # if era != "C":
        #     continue

        datasets[f"{pd}_{era}"] = {
            "files": tag,
            "trigger_sel": DataTrig[pd],
            "read_form": "data",
            "is_data": True,
            "era": f"UL2017{era}",
        }
        samples_data.append(f"{pd}_{era}")

samples = {}
colors = {}

samples["Data"] = {
    "samples": samples_data,
    "is_data": True,
}


samples["Zjj_outfiducial"] = {
    "samples": ["Zjj_outfiducial"],
    "is_signal": False,
}
colors["Zjj_outfiducial"] = cmap_petroff[5]
samples["Top"] = {
    "samples": [
        "TT",
    ]
    + [f"single_top_{i}" for i in range(5)],
}
colors["Top"] = cmap_petroff[1]

samples["VV"] = {
    "samples": ["WW", "WZ", "ZZ"],
}
colors["VV"] = cmap_petroff[2]

samples["Int"] = {
    "samples": ["Int"],
}
colors["Int"] = cmap_petroff[4]

samples["DY_PU"] = {
    "samples": [f"DY-{j}J_PU" for j in range(3)],
    # "samples": ["DY_NLO_PU"] + [f"DY-{j}J_PU" for j in range(3)],
    # "samples": ["DY_NLO_PU"],
}
colors["DY_PU"] = cmap_petroff[3]
samples["DY_hard"] = {
    "samples": [f"DY-{j}J_hard" for j in range(3)],
    # "samples": ["DY_NLO_hard"] + [f"DY-{j}J_hard" for j in range(3)],
    # "samples": ["DY_NLO_hard"],
}

colors["DY_hard"] = cmap_petroff[0]

samples["Zjj_fiducial"] = {
    "samples": [f"Zjj_ptll_{i}" for i in range(len(bins["ptll"]) - 1)],
    "is_signal": True,
}
colors["Zjj_fiducial"] = cmap_pastel[0]

# variable_to_unfold = "detajj"
# for i in range(len(bins[variable_to_unfold]) - 1):
#     samples[f"Zjj_{variable_to_unfold}_{i}"] = {
#         "samples": [f"Zjj_{variable_to_unfold}_{i}"],
#         "is_signal": True,
#     }
#     colors[f"Zjj_{variable_to_unfold}_{i}"] = cmap_pastel[i]


# regions

regions = {}
preselections = (  # noqa E731
    lambda events: (events.mll > 50)
    & (events.njet >= 2)
    & (events.mjj > 200)
    & (events.ptj1 > 30)
    & (events.ptj2 > 30)
)

# regions["sr_jet_inc_ee"] = {
#     "func": lambda events: (abs(events.mll - 91) < 15) & events.bVeto & events.ee,
#     "mask": 0,
# }

regions["top_cr_ee"] = {
    "func": lambda events: preselections(events)
    & (abs(events.mll - 91) >= 15)
    & events.bTag
    & events.ee,
    "mask": 0,
}

regions["dypu_cr_ee"] = {
    "func": lambda events: preselections(events)
    & (abs(events.mll - 91) < 15)
    & ((events.ptj1 <= 50) | (events.ptj2 <= 50))
    & events.bVeto
    & events.ee,
    "mask": 0,
}

regions["sr_inc_ee"] = {
    "func": lambda events: preselections(events)
    & (abs(events.mll - 91) < 15)
    & (events.ptj1 > 50)
    & (events.ptj2 > 50)
    & events.bVeto
    & events.ee,
    "mask": 0,
}


# regions["sr_jet_inc_mm"] = {
#     "func": lambda events: (abs(events.mll - 91) < 15) & events.bVeto & events.mm,
#     "mask": 0,
# }

regions["top_cr_mm"] = {
    "func": lambda events: preselections(events)
    & (abs(events.mll - 91) >= 15)
    & events.bTag
    & events.mm,
    "mask": 0,
}

regions["dypu_cr_mm"] = {
    "func": lambda events: preselections(events)
    & (abs(events.mll - 91) < 15)
    & ((events.ptj1 <= 50) | (events.ptj2 <= 50))
    & events.bVeto
    & events.mm,
    "mask": 0,
}

regions["sr_inc_mm"] = {
    "func": lambda events: preselections(events)
    & (abs(events.mll - 91) < 15)
    & (events.ptj1 > 50)
    & (events.ptj2 > 50)
    & events.bVeto
    & events.mm,
    "mask": 0,
}


variables = {}

variables["njet"] = {
    "func": lambda events: events.njet,
    "axis": hist.axis.Regular(6, 0, 6, name="njet"),
}

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
}
variables["etaj2"] = {
    "func": lambda events: ak.fill_none(events.jets[:, 1].eta, -9999),
    "axis": hist.axis.Regular(30, -5, 5, name="etaj2"),
}
variables["phij1"] = {
    "func": lambda events: ak.fill_none(events.jets[:, 0].phi, -9999),
    "axis": hist.axis.Regular(30, -np.pi, np.pi, name="phij1"),
}
variables["phij2"] = {
    "func": lambda events: ak.fill_none(events.jets[:, 1].phi, -9999),
    "axis": hist.axis.Regular(30, -np.pi, np.pi, name="phij2"),
}

# Dilepton
variables["mll"] = {
    "func": lambda events: (events.Lepton[:, 0] + events.Lepton[:, 1]).mass,
    "axis": hist.axis.Regular(50, 91 - 18, 91 + 18, name="mll"),
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
}
variables["etal2"] = {
    "func": lambda events: events.Lepton[:, 1].eta,
    "axis": hist.axis.Regular(30, -2.5, 2.5, name="etal2"),
}
variables["phil1"] = {
    "func": lambda events: events.Lepton[:, 0].phi,
    "axis": hist.axis.Regular(30, -np.pi, np.pi, name="phil1"),
}
variables["phil2"] = {
    "func": lambda events: events.Lepton[:, 1].phi,
    "axis": hist.axis.Regular(30, -np.pi, np.pi, name="phil2"),
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
}

# variables["Zeppenfeld_Z"] = {
#     "func": lambda events: ak.fill_none(
#         0.5
#         * (
#             (events.Lepton[:, 0].eta + events.Lepton[:, 1].eta)
#             - (events.jets[:, 0].eta + events.jets[:, 1].eta)
#         )
#         / events.detajj,
#         -9999.0,
#     ),
# }

# variables["Zeppenfeld_l1"] = {
#     "func": lambda events: ak.fill_none(
#         (
#             (events.Lepton[:, 0].eta)
#             - 0.5 * (events.jets[:, 0].eta + events.jets[:, 1].eta)
#         )
#         / events.detajj,
#         -9999.0,
#     ),
# }

variables["MET"] = {
    "func": lambda events: events.PuppiMET.pt,
    "axis": hist.axis.Regular(30, 0, 150, name="MET"),
}

# variables["weight"] = {
#     "func": lambda events: events["weight"],
# }

variables["dnn"] = {
    # "axis": hist.axis.Variable(
    #     [-1.0, -0.5, -0.1, 0.0] + list(np.linspace(1e-10, 1, 30)) + [1.1, 1.2],
    #     name="dnn",
    # )
    "axis": hist.axis.Regular(
        40,
        0.0,
        1.0,
        name="dnn",
    )
}

variables["run_period"] = {
    "func": lambda events: events.run_period,
    "axis": hist.axis.Regular(30, -1, 10, name="run_period"),
}

# fits
variables["dnn_fits"] = {
    "axis": hist.axis.Regular(
        20,
        0.0,
        1.0,
        name="dnn",
    ),
}
variables["detajj_fits"] = {
    "func": lambda events: abs(
        ak.fill_none(events.jets[:, 0].deltaeta(events.jets[:, 1]), -9999)
    ),
    "axis": hist.axis.Regular(6, 0, 8.5, name="detajj_fits"),
}

variables["MET_fits"] = {
    "func": lambda events: events.PuppiMET.pt,
    "axis": hist.axis.Regular(8, 0, 150, name="MET_fits"),
}

# for variable_to_unfold in bins:
#     variables[f"dnn_{variable_to_unfold}"] = {
#         "axis": [
#             hist.axis.Regular(10, 0, 1, name="dnn"),
#             hist.axis.Variable(bins[variable_to_unfold], name=variable_to_unfold),
#         ]
#     }

# variables["dnn_mjj"] = {
#     "axis": [
#         hist.axis.Regular(10, 0, 1, name="dnn"),
#         hist.axis.Variable(bins["mjj"], name="mjj"),
#     ]
# }
# variables["dnn_ptll"] = {
#     "axis": [
#         hist.axis.Regular(10, 0, 1, name="dnn"),
#         hist.axis.Variable(bins["ptll"], name="ptll"),
#     ]
# }

# variables["dnn_dphill"] = {
#     "axis": [
#         hist.axis.Regular(10, 0, 1, name="dnn"),
#         hist.axis.Variable(bins["dphill"], name="dphill"),
#     ]
# }


nuisances = {}
mcs = [sample for sample in samples if not samples[sample].get("is_data", False)]


nuisances["lumi"] = {
    "name": "lumi",
    "type": "lnN",
    "samples": dict((skey, "1.02") for skey in mcs),
}


for shift in [
    "lf",
    "hf",
    "hfstats1",
    "hfstats2",
    "lfstats1",
    "lfstats2",
    "cferr1",
    "cferr2",
    "jes",
]:
    nuisances[f"btag_{shift}"] = {
        "name": "CMS_btag_SF_" + shift,
        "kind": "suffix",
        "type": "shape",
        "samples": dict((skey, ["1", "1"]) for skey in mcs),
    }


for js in cfg["jme"]["jes"]:
    nuisances[f"JES_{js}"] = {
        "name": "CMS_jet_scale_" + js,
        "kind": "suffix",
        "type": "shape",
        "samples": dict((skey, ["1", "1"]) for skey in mcs),
    }

nuisances["JER"] = {
    "name": "CMS_jet_res",
    "kind": "suffix",
    "type": "shape",
    "samples": dict((skey, ["1", "1"]) for skey in mcs),
}

nuisances["prefireWeight"] = {
    "name": "CMS_prefireWeight",
    "kind": "suffix",
    "type": "shape",
    "samples": dict((skey, ["1", "1"]) for skey in mcs),
}

nuisances["PU"] = {
    "name": "CMS_PU",
    "kind": "suffix",
    "type": "shape",
    "samples": dict((skey, ["1", "1"]) for skey in mcs),
}

nuisances["PUID_SF"] = {
    "name": "CMS_PUID_SF",
    "kind": "suffix",
    "type": "shape",
    "samples": dict((skey, ["1", "1"]) for skey in mcs),
}

nuisances["ele_reco"] = {
    "name": "CMS_ele_reco",
    "kind": "suffix",
    "type": "shape",
    "samples": dict((skey, ["1", "1"]) for skey in mcs),
}

nuisances["ele_idiso"] = {
    "name": "CMS_ele_idiso",
    "kind": "suffix",
    "type": "shape",
    "samples": dict((skey, ["1", "1"]) for skey in mcs),
}

nuisances["mu_idiso"] = {
    "name": "CMS_mu_idiso",
    "kind": "suffix",
    "type": "shape",
    "samples": dict((skey, ["1", "1"]) for skey in mcs),
}

for sname in ["Zjj", "DY"]:
    mcs_theory_unc = [
        sample
        for sample in samples
        if not samples[sample].get("is_data", False) and (sname in sample)
    ]

    nuisances[f"PDFWeight_{sname}"] = {
        "name": f"PDF_{sname}",
        "kind": "weight_square",
        "type": "shape",
        "samples": {
            skey: [f"PDFWeight_{i}" for i in range(100)] for skey in mcs_theory_unc
        },
    }

    nuisances[f"QCDScale_{sname}"] = {
        "name": f"QCDScale_{sname}",
        "kind": "weight_envelope",
        "type": "shape",
        "samples": {
            skey: [f"QCDScale_{i}" for i in range(6)] for skey in mcs_theory_unc
        },
    }

# nuisances["VV_norm"] = {
#     "name": "CMS_VV_norm",
#     "samples": {
#         "VV": "1.00",
#     },
#     "type": "rateParam",
#     "cuts": [k for k in regions],
# }

nuisances["Top_norm"] = {
    "name": "CMS_Top_norm",
    "samples": {
        "Top": "1.00",
    },
    "type": "rateParam",
    "cuts": [k for k in regions],
}

nuisances["DY_hard_norm"] = {
    "name": "CMS_DY_hard_norm",
    "samples": {
        "DY_hard": "1.00",
    },
    "type": "rateParam",
    "cuts": [k for k in regions],
}

nuisances["DY_PU_norm"] = {
    "name": "CMS_DY_PU_17_norm",
    "samples": {
        "DY_PU": "1.00",
    },
    "type": "rateParam",
    "cuts": [k for k in regions],
}

## Use the following if you want to apply the automatic combine MC stat nuisances.
nuisances["stat"] = {
    "type": "auto",
    "maxPoiss": "10",
    "includeSignal": "0",
    #  nuisance ['maxPoiss'] =  Number of threshold events for Poisson modelling
    #  nuisance ['includeSignal'] =  Include MC stat nuisances on signal processes (1=True, 0=False)
    "samples": {},
}
