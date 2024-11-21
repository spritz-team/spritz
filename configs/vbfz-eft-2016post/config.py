# ruff: noqa: E501

import json
from itertools import cycle

import awkward as ak
import hist
import numpy as np
from spritz.framework.framework import cmap_pastel, cmap_petroff, get_fw_path

year = "Full2016v9noHIPM"

fw_path = get_fw_path()

with open(f"{fw_path}/data/common/lumi.json") as file:
    lumis = json.load(file)

with open(f"{fw_path}/data/{year}/cfg.json") as file:
    cfg = json.load(file)

lumi = lumis[year]["tot"] / 1000
plot_label = "VBF-Z"
year_label = "2016-noHIPM"
njobs = 30


plot_op_mode = "validate_sm"

runner = f"{fw_path}/src/spritz/runners/runner_eft.py"

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

datasets = {}

all_events_mask = "ak.ones_like(events.run) == 1"
ops = ["cW", "cHbox", "cHDD", "cHW", "cHWB", "cHj1", "cHj3", "cHl1", "cHl3"]
rwgt_col = "events.rwgt"

subsamples_eft = {
    "SM": (
        "ak.ones_like(events.run) == 1",
        f"{rwgt_col}[:, 0]",
    ),
}

for i in range(len(ops)):
    op = ops[i]
    pos_rwgt = 2 * i + 2
    neg_rwgt = 2 * i + 1

    lin = f"0.5 * ({rwgt_col}[:, {pos_rwgt}] - {rwgt_col}[:, {neg_rwgt}])"
    quad = f"0.5 * ({rwgt_col}[:, {pos_rwgt}] + {rwgt_col}[:, {neg_rwgt}] - 2 * {rwgt_col}[:, 0])"

    subsamples_eft[f"{op}_lin"] = (all_events_mask, lin)
    subsamples_eft[f"{op}_quad"] = (all_events_mask, quad)


datasets["Zjj"] = {
    "files": "EWK_LLJJ_MLL-50_MJJ-120",
    "task_weight": 8,
}

datasets["Zjj_EFT"] = {
    "files": "EWK_LLJJ_MLL-50_MJJ-120_EFT",
    "subsamples": subsamples_eft,
    "task_weight": 8,
}

for dataset in datasets:
    datasets[dataset]["read_form"] = "mc"

samples = {}
colors = {}


samples["Zjj_EFT_sm"] = {
    "samples": ["Zjj_EFT_SM"],
}
colors["Zjj_EFT_sm"] = cmap_petroff[0]

cmap_signal = cycle(cmap_pastel)
for op in ["cW"]:
    samples[f"Zjj_EFT_{op}_lin"] = {
        "samples": [f"Zjj_EFT_{op}_lin"],
    }
    colors[f"Zjj_EFT_{op}_lin"] = next(cmap_signal)

    samples[f"Zjj_EFT_{op}_quad"] = {
        "samples": [f"Zjj_EFT_{op}_quad"],
    }
    colors[f"Zjj_EFT_{op}_quad"] = next(cmap_signal)

samples["Zjj_sm"] = {
    "samples": ["Zjj"],
}
colors["Zjj_sm"] = cmap_pastel[0]

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

nuisances = {}
mcs = [sample for sample in samples if not samples[sample].get("is_data", False)]


nuisances["lumi"] = {
    "name": "lumi",
    "type": "lnN",
    "samples": dict((skey, "1.02") for skey in mcs),
}

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
    "name": "CMS_DY_PU_18_norm",
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
