import awkward as ak
import numpy as np
from coffea.jetmet_tools import JECStack, CorrectedJetsFactory
from coffea.lookup_tools import extractor
import variation as variation_module


def getJetCorrections(cfg):

    jec_stack_names = cfg["JME"]["jec_stack_names"]
    jec_stack_paths = cfg["JME"]["jec_stack_paths"]
    junc = cfg["JME"]["junc"]

    ext = extractor()
    for path in jec_stack_paths:
        ext.add_weight_sets(["* * " + path])

    ext.finalize()
    evaluator = ext.make_evaluator()

    jec_stack_names += list(filter(lambda k: junc in k, evaluator.keys()))
    jec_stack_names = list(filter(lambda k: k != junc, jec_stack_names))
    jec_inputs = {name: evaluator[name] for name in jec_stack_names}
    jec_stack = JECStack(jec_inputs)
    return jec_stack


def correct_jets(events, variations, jec_stack, run_variations=True):
    events[("Jet", "trueGenJetIdx")] = ak.mask(
        events.Jet.genJetIdx,
        (events.Jet.genJetIdx >= 0) & (events.Jet.genJetIdx < ak.num(events.GenJet)),
    )
    name_map = jec_stack.blank_name_map
    name_map["JetPt"] = "pt"
    name_map["JetMass"] = "mass"
    name_map["JetEta"] = "eta"
    name_map["JetA"] = "area"

    jets = ak.with_name(
        events.Jet, ""
    )  # Remove Momentum4D methods because will add 'rho'

    jets["pt_raw"] = (1 - jets["rawFactor"]) * jets["pt"]
    jets["mass_raw"] = (1 - jets["rawFactor"]) * jets["mass"]
    jets["pt_gen"] = ak.values_astype(
        ak.fill_none(events.GenJet[events.Jet.trueGenJetIdx].pt, 0), np.float32
    )
    jets["rho"] = ak.broadcast_arrays(events.fixedGridRhoFastjetAll, jets.pt)[0]
    name_map["ptGenJet"] = "pt_gen"
    name_map["ptRaw"] = "pt_raw"
    name_map["massRaw"] = "mass_raw"
    name_map["Rho"] = "rho"
    # jets["_rho"] = ak.broadcast_arrays(events.fixedGridRhoFastjetAll, jets.pt)[0]
    # name_map["Rho"] = (
    #     "_rho"  # very important! Cannot name it rho otherwise vector will skrew things up
    # )

    jet_factory = CorrectedJetsFactory(name_map, jec_stack)

    corrected_jets = jet_factory.build(jets).compute()

    corrected_jets_new = ak.zip({k: jets[k] for k in ["pt_raw", "mass_raw", "eta"]})
    corrected_jets_new["jec"] = corrected_jets["jet_energy_correction"]

    corrected_jets_new["pt"] = corrected_jets_new.pt_raw * corrected_jets_new.jec
    corrected_jets_new["mass"] = corrected_jets_new.mass_raw * corrected_jets_new.jec

    # # No JER anywhere
    # no_jer_mask = corrected_jets_new.pt >= 0.0

    # No JER in horn
    no_jer_mask = (
        (corrected_jets_new.pt < 50)
        & (abs(corrected_jets_new.eta) >= 2.8)
        & (abs(corrected_jets_new.eta) <= 3.0)
    )

    # # JER everywhere
    # no_jer_mask = corrected_jets_new.pt < 0.0

    corrected_jets_new["jer"] = ak.where(
        no_jer_mask,
        1.0,
        corrected_jets["jet_energy_resolution_correction"],
    )

    for tag in ["up", "down"]:
        corrected_jets_new[f"jer_{tag}"] = ak.where(
            no_jer_mask,
            1.0,
            corrected_jets["JER"][tag]["jet_energy_resolution_correction"],
        )

    corrected_jets_new["pt"] = corrected_jets_new["pt"] * corrected_jets_new["jer"]
    corrected_jets_new["mass"] = corrected_jets_new["mass"] * corrected_jets_new["jer"]

    variation_names = []
    for name in ["JER"]:
        variation_names.append(name)
        for tag in ["up", "down"]:
            for variable in ["pt", "mass"]:
                corrected_jets_new[f"{variable}_JER_{tag}"] = (
                    corrected_jets_new[variable]
                    * corrected_jets_new[f"jer_{tag}"]
                    / corrected_jets_new["jer"]
                )

    juncs = jec_stack.junc.getUncertainty(
        JetEta=corrected_jets_new.eta, JetPt=corrected_jets_new.pt
    )

    for name, func in juncs:
        variation_names.append(f"JES_{name}")
        for itag, tag in zip([0, 1], ["up", "down"]):
            for variable in ["pt", "mass"]:
                corrected_jets_new[f"{variable}_JES_{name}_{tag}"] = (
                    func[:, :, itag] * corrected_jets_new[variable]
                )

    # print(variation_names)

    events[("Jet", "pt")] = corrected_jets_new.pt
    events[("Jet", "mass")] = corrected_jets_new.mass

    if run_variations:
        for variation in variation_names:
            for tag in ["up", "down"]:
                for variable in ["pt", "mass"]:
                    # new_branch_name = f"{variable}_{variation}_{tag}"
                    variation_key = f"{variation}_{tag}"
                    new_branch_name = variation_module.Variation.format_varied_column(
                        ("Jet", variable), variation_key
                    )
                    # events[new_branch_name] = corrected_jets[(variation, tag, variable)]
                    old_branch_name = f"{variable}_{variation}_{tag}"
                    events[new_branch_name] = corrected_jets_new[old_branch_name]
                    variations.add_columns_for_variation(variation_key, [("Jet", variable)])

    # events[("Jet", "pt")] = corrected_jets.pt
    # events[("Jet", "mass")] = corrected_jets.mass

    # events[('Jet', 'trueGenJetIdx')] = None
    return events, variations
