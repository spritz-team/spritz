import gc
import json
import sys
import traceback as tb
from copy import deepcopy

import awkward as ak
import correctionlib
import hist
import numpy as np
import onnxruntime as ort
import spritz.framework.variation as variation_module
import uproot
import vector
from spritz.framework.framework import (
    big_process,
    get_analysis_dict,
    get_fw_path,
    read_chunks,
    write_chunks,
)
from spritz.modules.basic_selections import (
    LumiMask,
    lumi_mask,
    pass_flags,
    pass_trigger,
)
from spritz.modules.btag_sf import btag_sf
from spritz.modules.dnn_evaluator import dnn_evaluator, dnn_transform
from spritz.modules.gen_analysis import gen_analysis
from spritz.modules.jet_sel import cleanJet, jetSel
from spritz.modules.jme import (
    correct_jets_data,
    correct_jets_mc,
    jet_veto,
    remove_jets_HEM_issue,
)
from spritz.modules.lepton_sel import createLepton, leptonSel
from spritz.modules.lepton_sf import lepton_sf
from spritz.modules.prompt_gen import prompt_gen_match_leptons
from spritz.modules.puid_sf import puid_sf
from spritz.modules.puweight import puweight_sf
from spritz.modules.rochester import correctRochester, getRochester
from spritz.modules.run_assign import assign_run_period
from spritz.modules.theory_unc import theory_unc
from spritz.modules.trigger_sf import trigger_sf

vector.register_awkward()

print("uproot version", uproot.__version__)
print("awkward version", ak.__version__)

path_fw = get_fw_path()
with open("cfg.json") as file:
    txt = file.read()
    txt = txt.replace("RPLME_PATH_FW", path_fw)
    cfg = json.loads(txt)

ceval_puid = correctionlib.CorrectionSet.from_file(cfg["puidSF"])
ceval_btag = correctionlib.CorrectionSet.from_file(cfg["btagSF"])
ceval_puWeight = correctionlib.CorrectionSet.from_file(cfg["puWeights"])
ceval_lepton_sf = correctionlib.CorrectionSet.from_file(cfg["leptonSF"])
ceval_assign_run = correctionlib.CorrectionSet.from_file(cfg["run_to_era"])

cset_trigger = correctionlib.CorrectionSet.from_file(cfg["triggerSF"])
# jec_stack = getJetCorrections(cfg)
rochester = getRochester(cfg)

analysis_path = sys.argv[1]
analysis_cfg = get_analysis_dict(analysis_path)
special_analysis_cfg = analysis_cfg["special_analysis_cfg"]
sess_opt = ort.SessionOptions()
sess_opt.intra_op_num_threads = 1
sess_opt.inter_op_num_threads = 1
dnn_cfg = special_analysis_cfg["dnn"]
onnx_session = ort.InferenceSession(dnn_cfg["model"], sess_opt)
dnn_t = dnn_transform(dnn_cfg["cumulative_signal"])


def ensure_not_none(arr):
    if ak.any(ak.is_none(arr)):
        raise Exception("There are some None in branch", arr[ak.is_none(arr)])
    return ak.fill_none(arr, -9999.9)


def process(events, **kwargs):
    dataset = kwargs["dataset"]
    trigger_sel = kwargs.get("trigger_sel", "")
    isData = kwargs.get("is_data", False)
    era = kwargs.get("era", None)
    isData = kwargs.get("is_data", False)
    subsamples = kwargs.get("subsamples", {})
    special_weight = eval(kwargs.get("weight", "1.0"))

    # variations = {}
    # variations["nom"] = [()]
    variations = variation_module.Variation()
    variations.register_variation([], "nom")

    if isData:
        events["weight"] = ak.ones_like(events.run)
    else:
        events["weight"] = events.genWeight

    if "EFT" in dataset:
        neft_rwgts = 55
        events = events[ak.num(events.LHEReweightingWeight) == neft_rwgts]
        events["rwgt"] = ak.pad_none(
            events.LHEReweightingWeight, neft_rwgts, clip=True, axis=1
        )
        events["rwgt"] = ak.fill_none(events.rwgt, 0.0)

    if isData:
        lumimask = LumiMask(cfg["lumiMask"])
        events = lumi_mask(events, lumimask)

    sumw = ak.sum(events.weight)
    nevents = ak.num(events.weight, axis=0)

    # Add special weight for each dataset (not subsamples)
    if special_weight != 1.0:
        print(f"Using special weight for {dataset}: {special_weight}")

    events["weight"] = events.weight * special_weight

    # pass trigger and flags
    events = assign_run_period(events, isData, cfg, ceval_assign_run)
    events = pass_trigger(events, cfg["era"])
    events = pass_flags(events, cfg["flags"])

    events = events[events.pass_flags & events.pass_trigger]

    if isData:
        # each data DataSet has its own trigger_sel
        events = events[eval(trigger_sel)]

    # high pt muons
    events[("Muon", "pt")] = ak.where(
        events.Muon.pt > 200, events.Muon.pt * events.Muon.tunepRelPt, events.Muon.pt
    )

    events = jetSel(events, cfg)

    events = createLepton(events)

    events = leptonSel(events, cfg)
    # Latinos definitions, only consider loose leptons
    # remove events where ptl1 < 8
    events["Lepton"] = events.Lepton[events.Lepton.isLoose]
    # Apply a skim!
    events = events[ak.num(events.Lepton) >= 2]
    events = events[events.Lepton[:, 0].pt >= 8]

    if not isData:
        events = prompt_gen_match_leptons(events)

    # FIXME should clean from only tight / loose?
    events = cleanJet(events)

    # Require at least one good PV
    events = events[events.PV.npvsGood > 0]

    if kwargs.get("top_pt_rwgt", False):
        top_particle_mask = (events.GenPart.pdgId == 6) & ak.values_astype(
            (events.GenPart.statusFlags >> 13) & 1, bool
        )
        toppt = ak.fill_none(
            ak.mask(events, ak.num(events.GenPart[top_particle_mask]) >= 1)
            .GenPart[top_particle_mask][:, -1]
            .pt,
            0.0,
        )

        atop_particle_mask = (events.GenPart.pdgId == -6) & ak.values_astype(
            (events.GenPart.statusFlags >> 13) & 1, bool
        )
        atoppt = ak.fill_none(
            ak.mask(events, ak.num(events.GenPart[atop_particle_mask]) >= 1)
            .GenPart[atop_particle_mask][:, -1]
            .pt,
            0.0,
        )

        top_pt_rwgt = (toppt * atoppt > 0.0) * (
            np.sqrt(np.exp(0.0615 - 0.0005 * toppt) * np.exp(0.0615 - 0.0005 * atoppt))
        ) + (toppt * atoppt <= 0.0)
        events["weight"] = events.weight * top_pt_rwgt

    # Remove jets HEM issue
    events = remove_jets_HEM_issue(events, cfg)

    # # Jet veto maps
    events = jet_veto(events, cfg)

    # MCCorr
    # Should load SF and corrections here

    # # Correct Muons with rochester
    events = correctRochester(events, isData, rochester)

    if not isData:
        # puWeight
        events, variations = puweight_sf(events, variations, ceval_puWeight, cfg)

        # add trigger SF
        events, variations = trigger_sf(events, variations, cset_trigger, cfg)

        # add LeptonSF
        events, variations = lepton_sf(events, variations, ceval_lepton_sf, cfg)

        # FIXME add Electron Scale
        # FIXME add MET corrections?

        # Jets corrections

        # JEC + JER + JES
        events, variations = correct_jets_mc(
            events, variations, cfg, run_variations=False
        )

        # puId SF
        events, variations = puid_sf(events, variations, ceval_puid, cfg)

        # btag SF
        events, variations = btag_sf(events, variations, ceval_btag, cfg)

        # prefire

        if "L1PreFiringWeight" in ak.fields(events):
            events["prefireWeight"] = events.L1PreFiringWeight.Nom
            events["prefireWeight_up"] = events.L1PreFiringWeight.Up
            events["prefireWeight_down"] = events.L1PreFiringWeight.Dn

            variations.register_variation(
                columns=["prefireWeight"],
                variation_name="prefireWeight_up",
                format_rule=lambda _, var_name: var_name,
            )
            variations.register_variation(
                columns=["prefireWeight"],
                variation_name="prefireWeight_down",
                format_rule=lambda _, var_name: var_name,
            )
        else:
            events["prefireWeight"] = ak.ones_like(events.weight)

        # Theory unc.
        doTheoryVariations = special_analysis_cfg.get(
            "do_theory_variations", True
        ) and (dataset == "Zjj" or "DY" in dataset)
        if doTheoryVariations:
            events, variations = theory_unc(events, variations)
    else:
        events = correct_jets_data(events, cfg, era)

    regions = deepcopy(analysis_cfg["regions"])
    variables = deepcopy(analysis_cfg["variables"])

    # # FIXME removing all variations
    variations.variations_dict = {
        k: v for k, v in variations.variations_dict.items() if k == "nom"
    }

    default_axis = [
        hist.axis.StrCategory(
            [region for region in regions],
            name="category",
        ),
        hist.axis.StrCategory(
            sorted(list(variations.get_variations_all())), name="syst"
        ),
    ]

    results = {}
    results = {dataset: {"sumw": sumw, "nevents": nevents, "events": 0, "histos": 0}}
    if subsamples != {}:
        results = {}
        for subsample in subsamples:
            results[f"{dataset}_{subsample}"] = {
                "sumw": sumw,
                "nevents": nevents,
                "events": 0,
                "histos": 0,
            }

    for dataset_name in results:
        _events = {}
        histos = {}
        for variable in variables:
            _events[variable] = ak.Array([])

            if "axis" in variables[variable]:
                if isinstance(variables[variable]["axis"], list):
                    histos[variable] = hist.Hist(
                        *variables[variable]["axis"],
                        *default_axis,
                        hist.storage.Weight(),
                    )
                else:
                    histos[variable] = hist.Hist(
                        variables[variable]["axis"],
                        *default_axis,
                        hist.storage.Weight(),
                    )

        results[dataset_name]["histos"] = histos
        results[dataset_name]["events"] = _events

    originalEvents = ak.copy(events)
    jet_pt_backup = ak.copy(events.Jet.pt)

    # FIXME add FakeW

    print("Doing variations")
    # for variation in sorted(list(variations.keys())):
    # for variation in ["nom"]:
    for variation in sorted(variations.get_variations_all()):
        events = ak.copy(originalEvents)
        assert ak.all(events.Jet.pt == jet_pt_backup)

        print(variation)
        for switch in variations.get_variation_subs(variation):
            if len(switch) == 2:
                # print(switch)
                variation_dest, variation_source = switch
                events[variation_dest] = events[variation_source]

        # resort Leptons
        lepton_sort = ak.argsort(events[("Lepton", "pt")], ascending=False, axis=1)
        events["Lepton"] = events.Lepton[lepton_sort]

        # l2tight
        events = events[(ak.num(events.Lepton, axis=1) >= 2)]

        eleWP = cfg["leptonsWP"]["eleWP"]
        muWP = cfg["leptonsWP"]["muWP"]

        comb = ak.ones_like(events.run) == 1.0
        for ilep in range(2):
            comb = comb & (
                events.Lepton[:, ilep]["isTightElectron_" + eleWP]
                | events.Lepton[:, ilep]["isTightMuon_" + muWP]
            )
        events["l2Tight"] = ak.copy(comb)
        events = events[events.l2Tight]

        if len(events) == 0:
            continue

        # Jet real selections

        # resort Jets
        jet_sort = ak.argsort(events[("Jet", "pt")], ascending=False, axis=1)
        events["Jet"] = events.Jet[jet_sort]

        events["Jet"] = events.Jet[events.Jet.pt >= 30]
        # events = events[(ak.num(events.Jet[events.Jet.pt >= 30], axis=1) >= 2)]
        events["njet"] = ak.num(events.Jet, axis=1)
        events["njet_50"] = ak.num(events.Jet[events.Jet.pt >= 50], axis=1)
        # Define categories

        events["ee"] = (
            events.Lepton[:, 0].pdgId * events.Lepton[:, 1].pdgId
        ) == -11 * 11
        events["mm"] = (
            events.Lepton[:, 0].pdgId * events.Lepton[:, 1].pdgId
        ) == -13 * 13

        if not isData:
            events["prompt_gen_match_2l"] = (
                events.Lepton[:, 0].promptgenmatched
                & events.Lepton[:, 1].promptgenmatched
            )
            events = events[events.prompt_gen_match_2l]

        # Analysis level cuts
        leptoncut = events.ee | events.mm

        # third lepton veto
        leptoncut = leptoncut & (
            ak.fill_none(
                ak.mask(
                    ak.all(events.Lepton[:, 2:].pt < 10, axis=1),
                    ak.num(events.Lepton) >= 3,
                ),
                True,
                axis=0,
            )
        )

        # Cut on pt of two leading leptons
        leptoncut = (
            leptoncut & (events.Lepton[:, 0].pt > 25) & (events.Lepton[:, 1].pt > 13)
        )

        events = events[leptoncut]

        if len(events) == 0:
            continue

        # BTag

        btag_mask = (events.Jet.pt > 30) & (abs(events.Jet.eta) < 2.5)
        btag_cut = btag_mask & (events.Jet.btagDeepFlavB > cfg["bTag"]["btagMedium"])
        events["bVeto"] = ak.num(events.Jet[btag_cut]) == 0
        events["bTag"] = ak.num(events.Jet[btag_cut]) >= 1

        if not isData:
            # Load all SFs
            # FIXME should remove btagSF
            events["btagSF"] = ak.prod(
                events.Jet[btag_mask].btagSF_deepjet_shape, axis=1
            )
            events["PUID_SF"] = ak.prod(events.Jet.PUID_SF, axis=1)
            events["RecoSF"] = events.Lepton[:, 0].RecoSF * events.Lepton[:, 1].RecoSF
            events["TightSF"] = (
                events.Lepton[:, 0].TightSF * events.Lepton[:, 1].TightSF
            )

            events["weight"] = (
                events.weight
                * events.puWeight
                * events.PUID_SF
                * events.RecoSF
                * events.TightSF
                * events.btagSF
                * events.prefireWeight
                * events.TriggerSFweight_2l
                # * events.EMTFbug_veto
            )

        # Variable definitions
        events["jets"] = ak.pad_none(events.Jet, 2)
        for variable in variables:
            if "func" in variables[variable]:
                events[variable] = variables[variable]["func"](events)

        # Apply cuts

        # events = events[ak.fill_none(events.mll > 50, False)]
        # events = events[
        #     ak.fill_none(
        #         (events.njet >= 2)
        #         & (events.mjj >= 200)
        #         & (events.jets[:, 0].pt >= 30)
        #         & (events.jets[:, 1].pt >= 30)
        #         & (events.mll > 50),
        #         False,
        #     )
        # ]

        events = dnn_evaluator(
            onnx_session,
            events,
            dnn_t,
            dnn_cfg,
        )

        if dataset == "Zjj":
            events = gen_analysis(events, dataset)

        if "DY" in dataset and "J" in dataset:
            # DY jet binned has no mll > 50 cut
            # print("Should cut DY jet binned LHE mll", dataset)
            lhe_leptons_mask = (events.LHEPart.status == 1) & (
                (abs(events.LHEPart.pdgId) == 11)
                | (abs(events.LHEPart.pdgId) == 13)
                | (abs(events.LHEPart.pdgId) == 15)
            )
            lhe_leptons = events.LHEPart[lhe_leptons_mask]
            assert ak.all(ak.num(lhe_leptons) == 2)
            lhe_mll = (lhe_leptons[:, 0] + lhe_leptons[:, 1]).mass
            events = events[lhe_mll > 50]

        if "DY" in dataset:
            gen_photons = (
                (events.GenPart.pdgId == 22)
                & ak.values_astype(events.GenPart.statusFlags & 1, bool)
                & (events.GenPart.status == 1)
                & (events.GenPart.pt > 15)
                & (abs(events.GenPart.eta) < 2.6)
            )
            gen_mask = ak.num(events.GenPart[gen_photons]) == 0
            jet = events.Jet
            jet_genmatched = (jet.genJetIdx >= 0) & (
                jet.genJetIdx < ak.num(events.GenJet)
            )
            jet_genmatched = ak.pad_none(jet_genmatched, 2)
            both_jets_gen_matched = ak.fill_none(
                jet_genmatched[:, 0] & jet_genmatched[:, 1], False
            )
            events["hard"] = gen_mask & both_jets_gen_matched
            events["PU"] = gen_mask & ~both_jets_gen_matched

        events[f"mask_{dataset}"] = ak.ones_like(events.run) == 1.0
        events[f"weight_{dataset}"] = events.weight

        if subsamples != {}:
            for subsample in subsamples:
                subsample_val = subsamples[subsample]

                if isinstance(subsample_val, str):
                    subsample_mask = eval(subsample_val)
                    subsample_weight = 1.0
                elif (
                    isinstance(subsample_val, tuple) or isinstance(subsample_val, list)
                ) and len(subsample_val) == 2:
                    subsample_mask = eval(subsample_val[0])
                    subsample_weight = eval(subsample_val[1])
                else:
                    raise Exception(
                        "subsample value can either be a str (mask) or tuple/list of "
                        "len 2 (mask, weight)"
                    )

                events[f"mask_{dataset}_{subsample}"] = subsample_mask
                events[f"weight_{dataset}_{subsample}"] = (
                    events.weight * subsample_weight
                )

        for region in regions:
            regions[region]["mask"] = regions[region]["func"](events)

        # Fill histograms
        for dataset_name in results:
            for region in regions:
                # for category in categories:
                # Apply mask for specific region, category and dataset_name
                mask = regions[region]["mask"] & events[f"mask_{dataset_name}"]

                if len(events[mask]) == 0:
                    continue

                for variable in results[dataset_name]["histos"]:
                    if isinstance(variables[variable]["axis"], list):
                        var_names = [k.name for k in variables[variable]["axis"]]
                        vals = {
                            var_name: events[var_name][mask] for var_name in var_names
                        }
                        results[dataset_name]["histos"][variable].fill(
                            **vals,
                            category=region,
                            syst=variation,
                            weight=events[f"weight_{dataset_name}"][mask],
                        )
                    else:
                        var_name = variables[variable]["axis"].name
                        results[dataset_name]["histos"][variable].fill(
                            events[var_name][mask],
                            category=region,
                            syst=variation,
                            weight=events[f"weight_{dataset_name}"][mask],
                        )

                # # Snapshot
                # # print("Saving", len(events[mask]), "events for dataset", dataset_name)
                # for variable in results[dataset_name]["events"]:
                #     branch = ensure_not_none(events[variable][mask])
                #     # print(variable)
                #     # assert ak.any(ak.is_none(branch))
                #     # assert ak.all(ak.num(branch) == 1)
                #     results[dataset_name]["events"][variable] = ak.concatenate(
                #         [
                #             results[dataset_name]["events"][variable],
                #             ak.copy(branch),
                #         ]
                #     )
                #     # print("is ak", isinstance(branch, ak.highlevel.Array))
                #     # print("is np", isinstance(branch, np.ndarray))

    gc.collect()
    return results


if __name__ == "__main__":
    chunks_readable = False
    new_chunks = read_chunks("chunks_job.pkl", readable=chunks_readable)
    print("N chunks to process", len(new_chunks))

    results = {}
    errors = []
    processed = []

    for i in range(len(new_chunks)):
        new_chunk = new_chunks[i]

        if new_chunk["result"] != {}:
            print(
                "Skip chunk",
                {k: v for k, v in new_chunk["data"].items() if k != "read_form"},
                "was already processed",
            )
            continue

        print(new_chunk["data"]["dataset"])

        # # # FIXME run only on Zjj and DY
        # if new_chunk["data"]["dataset"] not in ["Zjj"]:
        #     continue

        # # FIXME run only on data
        # if not new_chunk["data"].get("is_data", False):
        #     continue

        # # FIXME process only one chunk per dataset
        # if new_chunk["data"]["dataset"] in processed:
        #     continue
        # processed.append(new_chunk["data"]["dataset"])

        # if "EFT" not in new_chunk["data"]["dataset"]:
        #     continue

        try:
            new_chunks[i]["result"] = big_process(process=process, **new_chunk["data"])
            new_chunks[i]["error"] = ""
        except Exception as e:
            print("\n\nError for chunk", new_chunk, file=sys.stderr)
            nice_exception = "".join(tb.format_exception(None, e, e.__traceback__))
            print(nice_exception, file=sys.stderr)
            new_chunks[i]["result"] = {}
            new_chunks[i]["error"] = nice_exception

        print(f"Done {i+1}/{len(new_chunks)}")

        # # FIXME run only on first chunk
        # if i >= 1:
        #     break

    # file = uproot.recreate("results.root")
    datasets = list(filter(lambda k: "root:/" not in k, results.keys()))
    # for dataset in datasets:
    #     print("Done", results[dataset]["nevents"], "events for dataset", dataset)
    #     file[dataset] = results[dataset]["events"]
    # file.close()

    # clean the events dictionary (too heavy and already saved in the root file)
    # for dataset in datasets:
    #     results[dataset]["events"] = {}

    write_chunks(new_chunks, "results.pkl", readable=chunks_readable)
