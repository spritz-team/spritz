import os
import time

import awkward as ak
import correctionlib
import hist
import matplotlib as mpl
import numpy as np
from data.common import chunk, jec_tag, jer_tag, jes_uncs, jet_algo, lvl_compound

from utils import correctionlib_wrapper, fold, read_events, set_plot_style

mpl.use("Agg")
import matplotlib.pyplot as plt
import mplhep as hep

if __name__ == "__main__":
    set_plot_style()

    h = hist.Hist(
        hist.axis.Regular(30, 15, 100, name="pt"),
        hist.axis.StrCategory([], name="category", growth=True),
        hist.storage.Weight(),
    )

    events = read_events(
        chunk["data"]["filenames"][-1],
        chunk["data"]["start"],
        chunk["data"]["stop"],
        chunk["data"]["read_form"],
    )

    events["weight"] = ak.broadcast_arrays(events.genWeight, events.Jet.pt)[0]
    h.fill(
        pt=ak.flatten(events.Jet.pt),
        category="original",
        weight=ak.flatten(events.weight),
    )

    print(events)

    runnum = events.run << 20
    luminum = events.luminosityBlock << 10
    evtnum = events.event
    event_random_seed = 1 + runnum + evtnum + luminum
    jet0eta = ak.pad_none(events.Jet.eta / 0.01, 1, clip=True)
    jet0eta = ak.fill_none(jet0eta, 0.0)[:, 0]
    jet0eta = ak.values_astype(jet0eta, int)
    event_random_seed = 1 + runnum + evtnum + luminum + jet0eta
    events[("Jet", "trueGenJetIdx")] = ak.mask(
        events.Jet.genJetIdx,
        (events.Jet.genJetIdx >= 0) & (events.Jet.genJetIdx < ak.num(events.GenJet)),
    )
    events["pt_gen"] = ak.values_astype(
        ak.fill_none(events.GenJet[events.Jet.trueGenJetIdx].pt, -1), np.float32
    )

    example_value_dict = {
        "JetPt": events.Jet.pt,
        "JetEta": events.Jet.eta,
        "JetPhi": events.Jet.phi,
        "JetA": events.Jet.area,
        "Rho": ak.broadcast_arrays(events.fixedGridRhoFastjetAll, events.Jet.pt)[0],
        "systematic": "nom",
        "GenPt": events.pt_gen,
        "EventID": event_random_seed,
    }

    # load JSON files using correctionlib

    # AK4
    fname = os.path.abspath("data/clib/jet_jerc.json.gz")
    print("\nLoading JSON file: {}".format(fname))
    cset_jerc = correctionlib.CorrectionSet.from_file(fname)

    # tool for JER smearing
    fname_jersmear = os.path.abspath("data/clib/jer_smear.json.gz")
    print("\nLoading JSON file: {}".format(fname_jersmear))
    cset_jersmear = correctionlib.CorrectionSet.from_file(fname_jersmear)

    start = time.perf_counter()

    key = "{}_{}_{}".format(jec_tag, lvl_compound, jet_algo)
    sf_cset = cset_jerc.compound[key]
    jet_map = {
        "jet_pt": events.Jet.pt,
        "jet_pt_raw": events.Jet.pt * (1.0 - events.Jet.rawFactor),
        "jet_eta": events.Jet.eta,
        "jet_phi": events.Jet.phi,
        "jet_area": events.Jet.area,
        "rho": ak.broadcast_arrays(events.fixedGridRhoFastjetAll, events.Jet.pt)[0],
        "systematic": "nom",
        "gen_pt": events.pt_gen,
        "EventID": ak.broadcast_arrays(event_random_seed, events.Jet.pt)[0],
    }

    sf = correctionlib_wrapper(sf_cset)(
        jet_map["jet_area"],
        jet_map["jet_eta"],
        jet_map["jet_pt_raw"],
        jet_map["rho"],
    )

    jet_map["jet_pt"] = jet_map["jet_pt_raw"] * sf

    for unc in jes_uncs:
        key = f"{jec_tag}_Regrouped_{unc}_{jet_algo}"
        sf_unc_cset = cset_jerc[key]
        sf_unc = correctionlib_wrapper(sf_unc_cset)(
            jet_map["jet_eta"],
            jet_map["jet_pt_raw"],
        )
        jet_map[f"jet_pt_{unc}_up"] = (sf + sf_unc) * jet_map["jet_pt_raw"]
        jet_map[f"jet_pt_{unc}_down"] = (sf - sf_unc) * jet_map["jet_pt_raw"]

    h.fill(
        pt=ak.flatten(jet_map["jet_pt"]),
        category="jec",
        weight=ak.flatten(events.weight),
    )

    key = "{}_{}_{}".format(jer_tag, "ScaleFactor", jet_algo)
    sf_cset_jer = correctionlib_wrapper(cset_jerc[key])

    key = "{}_{}_{}".format(jer_tag, "PtResolution", jet_algo)
    ptres_jer_cset = correctionlib_wrapper(cset_jerc[key])

    key_jersmear = "JERSmear"
    sf_jersmear_cset = correctionlib_wrapper(cset_jersmear[key_jersmear])

    for tag, variation_name, jet_pt_name in [
        ["up", "JER_up", "jet_pt"],
        ["down", "JER_down", "jet_pt"],
        ["nom", "nom", "jet_pt"],
    ] + [
        ["nom", f"{unc}_{tag}", f"jet_pt_{unc}_{tag}"]
        for unc in jes_uncs
        for tag in ["up", "down"]
    ]:
        sf_jer = sf_cset_jer(
            jet_map["jet_eta"],
            tag,
        )

        ptres_jer = ptres_jer_cset(
            jet_map["jet_eta"],
            jet_map[jet_pt_name],
            jet_map["rho"],
        )

        # add previously obtained JER/JERSF values to inputs

        sf_jersmear = sf_jersmear_cset(
            jet_map[jet_pt_name],
            jet_map["jet_eta"],
            jet_map["gen_pt"],
            jet_map["rho"],
            jet_map["EventID"],
            ptres_jer,
            sf_jer,
        )

        # Latinos recipe
        no_jer_mask = (
            (jet_map[jet_pt_name] < 50)
            & (abs(jet_map["jet_eta"]) >= 2.8)
            & (abs(jet_map["jet_eta"]) <= 3.0)
        )

        new_jet_pt_name = jet_pt_name
        if tag != "nom":
            new_jet_pt_name = jet_pt_name + "_" + variation_name
        jet_map[new_jet_pt_name] = (
            ak.where(no_jer_mask, 1.0, sf_jersmear) * jet_map[jet_pt_name]
        )

    h.fill(
        pt=ak.flatten(jet_map["jet_pt_Absolute_up"]),
        category="Absolute_up",
        weight=ak.flatten(events.weight),
    )

    h.fill(
        pt=ak.flatten(jet_map["jet_pt"]),
        category="jer",
        weight=ak.flatten(events.weight),
    )

    h.fill(
        pt=ak.flatten(jet_map["jet_pt_JER_up"]),
        category="jer_up",
        weight=ak.flatten(events.weight),
    )

    print("finished", time.perf_counter() - start)

    h = fold(h)
    fig, ax = plt.subplots(4, 1, sharex=True, figsize=(10, 10))
    hep.cms.label("JME Clib", ax=ax[0])
    ax[0].stairs(
        h[:, hist.loc("jer")].values() / h[:, hist.loc("jec")].values(),
        h.axes[0].edges,
        baseline=1.0,
        label="JER / JEC",
    )
    ax[0].plot(
        h.axes[0].edges,
        np.ones_like(h.axes[0].edges),
        color="black",
    )
    ax[0].legend()

    ax[1].stairs(
        h[:, hist.loc("Absolute_up")].values() / h[:, hist.loc("jec")].values(),
        h.axes[0].edges,
        baseline=1.0,
        label="JES / JEC",
    )

    ax[1].plot(
        h.axes[0].edges,
        np.ones_like(h.axes[0].edges),
        color="black",
    )
    ax[1].legend()

    ax[2].stairs(
        h[:, hist.loc("Absolute_up")].values() / h[:, hist.loc("jer")].values(),
        h.axes[0].edges,
        baseline=1.0,
        label="JES / JER",
    )

    ax[2].plot(
        h.axes[0].edges,
        np.ones_like(h.axes[0].edges),
        color="black",
    )
    ax[2].legend()

    ax[3].stairs(
        h[:, hist.loc("jer_up")].values() / h[:, hist.loc("jer")].values(),
        h.axes[0].edges,
        baseline=1.0,
        label="JER up / JER",
    )

    ax[3].plot(
        h.axes[0].edges,
        np.ones_like(h.axes[0].edges),
        color="black",
    )
    ax[3].legend()
    ax[3].set_xlabel("$p^T_j$")

    plt.legend()

    plt.savefig("test.png")
