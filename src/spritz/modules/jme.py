import awkward as ak
import correctionlib
import numpy as np
import spritz.framework.variation as variation_module

# from coffea.jetmet_tools import CorrectedJetsFactory, JECStack
# from coffea.lookup_tools import extractor


# def getJetCorrections(cfg):
#     jec_stack_names = cfg["JME"]["jec_stack_names"]
#     jec_stack_paths = cfg["JME"]["jec_stack_paths"]
#     junc = cfg["JME"]["junc"]

#     ext = extractor()
#     for path in jec_stack_paths:
#         ext.add_weight_sets(["* * " + path])

#     ext.finalize()
#     evaluator = ext.make_evaluator()

#     jec_stack_names += list(filter(lambda k: junc in k, evaluator.keys()))
#     jec_stack_names = list(filter(lambda k: k != junc, jec_stack_names))
#     jec_inputs = {name: evaluator[name] for name in jec_stack_names}
#     jec_stack = JECStack(jec_inputs)
#     return jec_stack


# def correct_jets(events, variations, jec_stack, run_variations=True):
#     events[("Jet", "trueGenJetIdx")] = ak.mask(
#         events.Jet.genJetIdx,
#         (events.Jet.genJetIdx >= 0) & (events.Jet.genJetIdx < ak.num(events.GenJet)),
#     )
#     name_map = jec_stack.blank_name_map
#     name_map["JetPt"] = "pt"
#     name_map["JetMass"] = "mass"
#     name_map["JetEta"] = "eta"
#     name_map["JetA"] = "area"

#     jets = ak.with_name(
#         events.Jet, ""
#     )  # Remove Momentum4D methods because will add 'rho'

#     jets["pt_raw"] = (1 - jets["rawFactor"]) * jets["pt"]
#     jets["mass_raw"] = (1 - jets["rawFactor"]) * jets["mass"]
#     jets["pt_gen"] = ak.values_astype(
#         ak.fill_none(events.GenJet[events.Jet.trueGenJetIdx].pt, 0), np.float32
#     )
#     jets["rho"] = ak.broadcast_arrays(events.fixedGridRhoFastjetAll, jets.pt)[0]
#     name_map["ptGenJet"] = "pt_gen"
#     name_map["ptRaw"] = "pt_raw"
#     name_map["massRaw"] = "mass_raw"
#     name_map["Rho"] = "rho"
#     # jets["_rho"] = ak.broadcast_arrays(events.fixedGridRhoFastjetAll, jets.pt)[0]
#     # name_map["Rho"] = (
#     #     "_rho"  # very important! Cannot name it rho otherwise vector will skrew things up
#     # )

#     jet_factory = CorrectedJetsFactory(name_map, jec_stack)

#     corrected_jets = jet_factory.build(jets).compute()

#     corrected_jets_new = ak.zip({k: jets[k] for k in ["pt_raw", "mass_raw", "eta"]})
#     corrected_jets_new["jec"] = corrected_jets["jet_energy_correction"]

#     corrected_jets_new["pt"] = corrected_jets_new.pt_raw * corrected_jets_new.jec
#     corrected_jets_new["mass"] = corrected_jets_new.mass_raw * corrected_jets_new.jec

#     # # No JER anywhere
#     # no_jer_mask = corrected_jets_new.pt >= 0.0

#     # No JER in horn
#     no_jer_mask = (
#         (corrected_jets_new.pt < 50)
#         & (abs(corrected_jets_new.eta) >= 2.8)
#         & (abs(corrected_jets_new.eta) <= 3.0)
#     )

#     # # JER everywhere
#     # no_jer_mask = corrected_jets_new.pt < 0.0

#     corrected_jets_new["jer"] = ak.where(
#         no_jer_mask,
#         1.0,
#         corrected_jets["jet_energy_resolution_correction"],
#     )

#     for tag in ["up", "down"]:
#         corrected_jets_new[f"jer_{tag}"] = ak.where(
#             no_jer_mask,
#             1.0,
#             corrected_jets["JER"][tag]["jet_energy_resolution_correction"],
#         )

#     corrected_jets_new["pt"] = corrected_jets_new["pt"] * corrected_jets_new["jer"]
#     corrected_jets_new["mass"] = corrected_jets_new["mass"] * corrected_jets_new["jer"]

#     variation_names = []
#     for name in ["JER"]:
#         variation_names.append(name)
#         for tag in ["up", "down"]:
#             for variable in ["pt", "mass"]:
#                 corrected_jets_new[f"{variable}_JER_{tag}"] = (
#                     corrected_jets_new[variable]
#                     * corrected_jets_new[f"jer_{tag}"]
#                     / corrected_jets_new["jer"]
#                 )

#     juncs = jec_stack.junc.getUncertainty(
#         JetEta=corrected_jets_new.eta, JetPt=corrected_jets_new.pt
#     )

#     for name, func in juncs:
#         variation_names.append(f"JES_{name}")
#         for itag, tag in zip([0, 1], ["up", "down"]):
#             for variable in ["pt", "mass"]:
#                 corrected_jets_new[f"{variable}_JES_{name}_{tag}"] = (
#                     func[:, :, itag] * corrected_jets_new[variable]
#                 )

#     # print(variation_names)

#     events[("Jet", "pt")] = corrected_jets_new.pt
#     events[("Jet", "mass")] = corrected_jets_new.mass

#     if run_variations:
#         for variation in variation_names:
#             for tag in ["up", "down"]:
#                 for variable in ["pt", "mass"]:
#                     # new_branch_name = f"{variable}_{variation}_{tag}"
#                     variation_key = f"{variation}_{tag}"
#                     new_branch_name = variation_module.Variation.format_varied_column(
#                         ("Jet", variable), variation_key
#                     )
#                     # events[new_branch_name] = corrected_jets[(variation, tag, variable)]
#                     old_branch_name = f"{variable}_{variation}_{tag}"
#                     events[new_branch_name] = corrected_jets_new[old_branch_name]
#                     variations.add_columns_for_variation(
#                         variation_key, [("Jet", variable)]
#                     )

#     # events[("Jet", "pt")] = corrected_jets.pt
#     # events[("Jet", "mass")] = corrected_jets.mass

#     # events[('Jet', 'trueGenJetIdx')] = None
#     return events, variations


# def jme(events, cfg, era):
#     if era is not None:
#         print(era)
#         print(cfg["jme"]["jec_tag"]["data"][era])


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
    sf_jer = cset_jer.evaluate(jet_map["jet_eta"], tag)
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
