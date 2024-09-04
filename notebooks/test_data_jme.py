import json

import awkward as ak
import correctionlib
import hist
import mplhep as hep
import numpy as np
from matplotlib import pyplot as plt
from spritz.framework.framework import get_fw_path, read_events
from spritz.scripts.post_process import hist_fold

fw_path = get_fw_path()
era = "Full2018v9"
cset_jerc = correctionlib.CorrectionSet.from_file(
    f"{fw_path}/data/{era}/clib/jet_jerc.json.gz"
)

with open(f"{fw_path}/data/{era}/cfg.json") as file:
    cfg = json.load(file)
jme_cfg = cfg["jme"]
d = jme_cfg["jec_tag"]["data"]
jec_tag = d[list(d.keys())[0]]  # first era
key = "{}_{}_{}".format(jec_tag, jme_cfg["lvl_compound"], jme_cfg["jet_algo"])
sf_cset = cset_jerc.compound[key]
print(sf_cset)

print([k.name for k in sf_cset.inputs])


chunk = {
    "data": {
        "dataset": "DoubleMuon_B",
        "filenames": [
            "root://grid-cms-xrootd.physik.rwth-aachen.de:1094//store/data/Run2018B/DoubleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9-v1/270000/0505F2F0-6F6D-0240-946A-9C2B65BFFA02.root",
            "root://maite.iihe.ac.be:1095//store/data/Run2018B/DoubleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9-v1/270000/0505F2F0-6F6D-0240-946A-9C2B65BFFA02.root",
            "root://cmsdcadisk.fnal.gov//dcache/uscmsdisk/store/data/Run2018B/DoubleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9-v1/270000/0505F2F0-6F6D-0240-946A-9C2B65BFFA02.root",
            "root://eos.cms.rcac.purdue.edu//store/data/Run2018B/DoubleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9-v1/270000/0505F2F0-6F6D-0240-946A-9C2B65BFFA02.root",
            "root://hactar01.crc.nd.edu//store/data/Run2018B/DoubleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9-v1/270000/0505F2F0-6F6D-0240-946A-9C2B65BFFA02.root",
            "root://dcache-cms-xrootd.desy.de:1094//store/data/Run2018B/DoubleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9-v1/270000/0505F2F0-6F6D-0240-946A-9C2B65BFFA02.root",
        ],
        "start": 0,
        "stop": 300000,
        "trigger_sel": "events.DoubleMu",
        "read_form": "data",
        "is_data": True,
    }
}

with open(f"{fw_path}/data/{era}/forms.json") as file:
    forms = json.load(file)

chunk["data"]["read_form"] = forms[chunk["data"]["read_form"]]

events = read_events(
    chunk["data"]["filenames"][-1],
    chunk["data"]["start"],
    chunk["data"]["stop"],
    chunk["data"]["read_form"],
)

events["weight"] = ak.ones_like(events.Jet.pt)

h = hist.Hist(
    hist.axis.Regular(30, 15, 100, name="pt"),
    hist.axis.StrCategory([], name="category", growth=True),
    hist.storage.Weight(),
)

h.fill(
    pt=ak.flatten(events.Jet.pt),
    category="original",
    weight=ak.flatten(events.weight),
)

jet_map = {
    "jet_pt": events.Jet.pt,
    "jet_pt_raw": events.Jet.pt * (1.0 - events.Jet.rawFactor),
    "jet_eta": events.Jet.eta,
    "jet_phi": events.Jet.phi,
    "jet_area": events.Jet.area,
    "rho": ak.broadcast_arrays(events.fixedGridRhoFastjetAll, events.Jet.pt)[0],
    # "systematic": "nom",
    # "gen_pt": events.pt_gen,
    # "EventID": ak.broadcast_arrays(event_random_seed, events.Jet.pt)[0],
}


sf = sf_cset.evaluate(
    jet_map["jet_area"],
    jet_map["jet_eta"],
    jet_map["jet_pt_raw"],
    jet_map["rho"],
)


jet_map["jet_pt"] = jet_map["jet_pt_raw"] * sf


h.fill(
    pt=ak.flatten(jet_map["jet_pt"]),
    category="jec",
    weight=ak.flatten(events.weight),
)

# h = hist_fold(h, 3)
h_orig = h[:, hist.loc("original")]
h_jec = h[:, hist.loc("jec")]
hist_fold(h_orig, 3)
hist_fold(h_jec, 3)

fig, ax = plt.subplots(2, 1, sharex=True, figsize=(10, 10))
hep.cms.label("JME Clib", ax=ax[0])

from itertools import cycle

color_cycle = cycle(["red", "green", "blue"])


def hist_plot(axis, h_vals, h_errs, edges, **kwargs):
    kwargs_stairs = kwargs.pop("stairs", {})
    kwargs_errorbar = kwargs.pop("errorbar", {})
    label = kwargs.pop("label", "")
    color = kwargs.pop("color", next(color_cycle))
    axis.stairs(h_vals, edges, color=color, label=label, **kwargs, **kwargs_stairs)
    centers = (edges[1:] + edges[:-1]) / 2
    axis.errorbar(
        centers, h_vals, yerr=h_errs, color=color, fmt="o", **kwargs, **kwargs_errorbar
    )


edges = h_orig.axes[0].edges
hist_plot(
    ax[0],
    h_orig.values(),
    np.sqrt(h_orig.variances()),
    edges,
    **{"stairs": {"baseline": 0.0}, "label": "Original"},
)
hist_plot(
    ax[0],
    h_jec.values(),
    np.sqrt(h_jec.variances()),
    edges,
    **{"stairs": {"baseline": 0.0}, "label": "JEC"},
)
# ax[0].stairs(
#     h_orig.values(),
#     h.axes[0].edges,
#     baseline=1.0,
#     label="Original",
# )
# ax[0].stairs(
#     h_jec.values(),
#     h.axes[0].edges,
#     baseline=1.0,
#     label="JEC",
# )
ax[0].legend()
ax[0].set_yscale("log")


def ratio_hist(h1, h2):
    v1 = h1.values()
    err1 = np.sqrt(h1.variances())
    v2 = h2.values()
    err2 = np.sqrt(h2.variances())
    h_vals = v1 / v2
    h_errs = v1 / v2 * np.sqrt(np.power(err1 / v1, 2) + np.power(err2 / v2, 2))
    return h_vals, h_errs


h_vals, h_errs = ratio_hist(h_jec, h_orig)

hist_plot(
    ax[1],
    h_vals,
    h_errs,
    edges,
    **{"stairs": {"baseline": 1.0}, "label": "JEC / Orig."},
)

# ax[1].stairs(
#     h_jec.values() / h_orig.values(),
#     h.axes[0].edges,
#     baseline=1.0,
#     label="JER / JEC",
# )
ax[1].plot(
    edges,
    np.ones_like(edges),
    color="black",
)
ax[1].legend()
plt.savefig("img_test_data_jme.png")
