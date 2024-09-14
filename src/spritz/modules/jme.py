import awkward as ak
import correctionlib
import numpy as np
import spritz.framework.variation as variation_module


def correct_jets_mc(events, variations, cfg, run_variations=False):
    cset_jerc = correctionlib.CorrectionSet.from_file(cfg["jet_jerc"])
    cset_jersmear = correctionlib.CorrectionSet.from_file(cfg["jer_smear"])
    jme_cfg = cfg["jme"]

    jec_tag = jme_cfg["jec_tag"]["mc"]
    key = "{}_{}_{}".format(jec_tag, jme_cfg["lvl_compound"], jme_cfg["jet_algo"])
    cset_jec = cset_jerc.compound[key]

    jer_tag = jme_cfg["jer_tag"]
    key = "{}_{}_{}".format(jer_tag, "ScaleFactor", jme_cfg["jet_algo"])
    cset_jer = cset_jerc[key]

    key = "{}_{}_{}".format(jer_tag, "PtResolution", jme_cfg["jet_algo"])
    cset_jer_ptres = cset_jerc[key]

    key = "JERSmear"
    cset_jersmear = cset_jersmear[key]

    events_jme = ak.copy(events)

    # Many operatorions to get event seed
    runnum = events_jme.run << 20
    luminum = events_jme.luminosityBlock << 10
    evtnum = events_jme.event
    event_random_seed = 1 + runnum + evtnum + luminum
    jet0eta = ak.pad_none(events_jme.Jet.eta / 0.01, 1, clip=True)
    jet0eta = ak.fill_none(jet0eta, 0.0)[:, 0]
    jet0eta = ak.values_astype(jet0eta, int)
    event_random_seed = 1 + runnum + evtnum + luminum + jet0eta

    # Gen Jet
    events_jme[("Jet", "trueGenJetIdx")] = ak.mask(
        events_jme.Jet.genJetIdx,
        (events_jme.Jet.genJetIdx >= 0)
        & (events_jme.Jet.genJetIdx < ak.num(events_jme.GenJet)),
    )
    events_jme["pt_gen"] = ak.values_astype(
        ak.fill_none(events_jme.GenJet[events_jme.Jet.trueGenJetIdx].pt, -1), np.float32
    )

    jet_map = {
        "jet_pt": events_jme.Jet.pt,
        "jet_mass": events_jme.Jet.mass,
        "jet_pt_raw": events_jme.Jet.pt * (1.0 - events_jme.Jet.rawFactor),
        "jet_mass_raw": events_jme.Jet.mass * (1.0 - events_jme.Jet.rawFactor),
        "jet_eta": events_jme.Jet.eta,
        "jet_phi": events_jme.Jet.phi,
        "jet_area": events_jme.Jet.area,
        "rho": ak.broadcast_arrays(
            events_jme.fixedGridRhoFastjetAll, events_jme.Jet.pt
        )[0],
        "systematic": "nom",
        "gen_pt": events_jme.pt_gen,
        "EventID": ak.broadcast_arrays(event_random_seed, events_jme.Jet.pt)[0],
    }

    sf_jec = cset_jec.evaluate(
        jet_map["jet_area"],
        jet_map["jet_eta"],
        jet_map["jet_pt_raw"],
        jet_map["rho"],
    )

    jet_map["jet_pt"] = jet_map["jet_pt_raw"] * sf_jec
    jet_map["jet_mass"] = jet_map["jet_mass_raw"] * sf_jec

    tag, variation_name, jet_pt_name = "nom", "nom", "jet_pt"
    new_jet_pt_name = jet_pt_name

    sf_jer = cset_jer.evaluate(
        jet_map["jet_eta"],
        tag,
    )
    sf_jer_ptres = cset_jer_ptres.evaluate(
        jet_map["jet_eta"],
        jet_map[jet_pt_name],
        jet_map["rho"],
    )
    sf_jersmear = cset_jersmear.evaluate(
        jet_map[jet_pt_name],
        jet_map["jet_eta"],
        jet_map["gen_pt"],
        jet_map["rho"],
        jet_map["EventID"],
        sf_jer_ptres,
        sf_jer,
    )

    # # Latinos recipe
    # no_jer_mask = (
    #     (jet_map[jet_pt_name] < 50)
    #     & (abs(jet_map["jet_eta"]) >= 2.8)
    #     & (abs(jet_map["jet_eta"]) <= 3.0)
    # )

    # Latinos recipe
    no_jer_mask = abs(jet_map["jet_eta"]) >= 2.5

    if tag != "nom":
        new_jet_pt_name = jet_pt_name + "_" + variation_name
    jet_map[new_jet_pt_name] = (
        ak.where(no_jer_mask, 1.0, sf_jersmear) * jet_map[jet_pt_name]
    )

    jet_map[new_jet_pt_name.replace("pt", "mass")] = (
        ak.where(no_jer_mask, 1.0, sf_jersmear)
        * jet_map[jet_pt_name.replace("pt", "mass")]
    )

    events[("Jet", "pt")] = jet_map[new_jet_pt_name]
    events[("Jet", "mass")] = jet_map[new_jet_pt_name.replace("pt", "mass")]
    return events, variations


def correct_jets_data(events, cfg, era):
    cset_jerc = correctionlib.CorrectionSet.from_file(cfg["jet_jerc"])
    jme_cfg = cfg["jme"]

    jec_tag = jme_cfg["jec_tag"]["data"][era]
    key = "{}_{}_{}".format(jec_tag, jme_cfg["lvl_compound"], jme_cfg["jet_algo"])
    cset_jec = cset_jerc.compound[key]

    events_jme = ak.copy(events)

    jet_map = {
        "jet_pt": events_jme.Jet.pt,
        "jet_mass": events_jme.Jet.mass,
        "jet_pt_raw": events_jme.Jet.pt * (1.0 - events_jme.Jet.rawFactor),
        "jet_mass_raw": events_jme.Jet.mass * (1.0 - events_jme.Jet.rawFactor),
        "jet_eta": events_jme.Jet.eta,
        "jet_phi": events_jme.Jet.phi,
        "jet_area": events_jme.Jet.area,
        "rho": ak.broadcast_arrays(
            events_jme.fixedGridRhoFastjetAll, events_jme.Jet.pt
        )[0],
    }

    sf_jec = cset_jec.evaluate(
        jet_map["jet_area"],
        jet_map["jet_eta"],
        jet_map["jet_pt_raw"],
        jet_map["rho"],
    )

    jet_map["jet_pt"] = jet_map["jet_pt_raw"] * sf_jec
    jet_map["jet_mass"] = jet_map["jet_mass_raw"] * sf_jec

    events[("Jet", "pt")] = jet_map["jet_pt"]
    events[("Jet", "mass")] = jet_map["jet_mass"]
    return events
