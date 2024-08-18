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
import uproot
import vector
from coffea.lumi_tools import LumiMask

import spritz.framework.variation as variation_module
from spritz.framework.framework import (
    big_process,
    get_fw_path,
    read_chunks,
    write_chunks,
    get_analysis_dict,
)
from spritz.modules.basic_selections import lumi_mask, pass_flags, pass_trigger
from spritz.modules.btag_sf import btag_sf
from spritz.modules.dnn_evaluator import dnn_evaluator, dnn_transform
from spritz.modules.gen_analysis import gen_analysis
from spritz.modules.jet_sel import cleanJet, jetSel
from spritz.modules.jme import correct_jets, getJetCorrections
from spritz.modules.lepton_sel import createLepton, leptonSel
from spritz.modules.lepton_sf import lepton_sf
from spritz.modules.prompt_gen import prompt_gen_match_leptons
from spritz.modules.puid_sf import puid_sf
from spritz.modules.puweight import puweight_sf
from spritz.modules.rochester import correctRochester, getRochester
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
jec_stack = getJetCorrections(cfg)
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
    subsamples = kwargs.get("subsamples", {})
    special_weight = kwargs.get("weight", "1.0")

    # variations = {}
    # variations["nom"] = [()]
    variations = variation_module.Variation()
    variations.register_variation([], "nom")

    if isData:
        events["weight"] = ak.ones_like(events.run)
    else:
        events["weight"] = events.genWeight

    if isData:
        lumimask = LumiMask(cfg["lumiMask"])
        events = lumi_mask(events, lumimask)

    sumw = ak.sum(events.weight)
    nevents = ak.num(events.weight, axis=0)

    # pass trigger and flags
    events = pass_trigger(events, cfg["tgr_data"])
    events = pass_flags(events, cfg["flags"])

    events = events[events.pass_flags & events.pass_trigger]

    if isData:
        # each data DataSet has its own trigger_sel
        events = events[eval(trigger_sel)]

    events = jetSel(events)

    events = createLepton(events)

    events = leptonSel(events)
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

    # # Require at least two loose leptons and loose jets
    # events = events[
    #     (ak.num(events.Lepton, axis=1) >= 2) & (ak.num(events.Jet, axis=1) >= 2)
    # ]

    # MCCorr
    # Should load SF and corrections here

    # Correct Muons with rochester
    events = correctRochester(events, isData, rochester)

    if not isData:
        # puWeight
        events, variations = puweight_sf(events, variations, ceval_puWeight, cfg)

        # add trigger SF
        events, variations = trigger_sf(events, variations, cfg)

        # add LeptonSF
        events, variations = lepton_sf(events, variations, ceval_lepton_sf, cfg)

        # FIXME add Electron Scale
        # FIXME add MET corrections?

        # Jets corrections

        # JEC + JER + JES
        events, variations = correct_jets(
            events, variations, jec_stack, run_variations=False
        )

        # puId SF
        events, variations = puid_sf(events, variations, ceval_puid)

        # btag SF
        events, variations = btag_sf(events, variations, ceval_btag, cfg)

        # Theory unc.
        doTheoryVariations = (
            special_analysis_cfg.get("do_theory_variations", True) and dataset == "Zjj"
        )
        if doTheoryVariations:
            events, variations = theory_unc(events, variations)

    # regions = get_regions()
    # categories = ["ee", "mm"]
    # axis = get_axis()
    # variables = get_variables()
    #from analysis.config import regions, variables
    regions = deepcopy(analysis_cfg['regions'])
    variables = deepcopy(analysis_cfg['variables'])

    # FIXME removing all variations
    variations.variations_dict = {
        k: v for k, v in variations.variations_dict.items() if k == "nom"
    }

    default_axis = [
        hist.axis.StrCategory(
            # [f"{region}_{category}" for region in regions for category in categories],
            [region for region in regions],
            name="category",
        ),
        hist.axis.StrCategory(
            sorted(list(variations.get_variations_all())), name="syst"
        ),
    ]

    results = {}
    results = {dataset: {"sumw": sumw, "nevents": nevents, "events": 0, "histos": 0}}
    # if "DY" in dataset:
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

    # Add special weight for each dataset (not subsamples)
    events["weight"] = events.weight * eval(special_weight)

    print("Doing variations")
    # for variation in sorted(list(variations.keys())):
    # for variation in ["nom"]:
    for variation in sorted(variations.get_variations_all()):
        events = ak.copy(originalEvents)
        assert ak.all(events.Jet.pt == jet_pt_backup)

        # print(variation)
        # for switch in variations[variation]:
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

        eleWP = cfg["eleWP"]
        muWP = cfg["muWP"]

        comb = ak.ones_like(events.run) == 1.0
        for ilep in range(2):
            comb = comb & (
                events.Lepton[:, ilep]["isTightElectron_" + eleWP]
                | events.Lepton[:, ilep]["isTightMuon_" + muWP]
            )
        events = events[comb]

        # Jet real selections

        # resort Jets
        jet_sort = ak.argsort(events[("Jet", "pt")], ascending=False, axis=1)
        events["Jet"] = events.Jet[jet_sort]

        events["ptj1_check"] = ak.fill_none(ak.pad_none(events.Jet.pt, 1)[:, 0], -9999)

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
            # Require the two leading lepton to be prompt gen matched (!fakes)
            events = events[
                events.Lepton[:, 0].promptgenmatched
                & events.Lepton[:, 1].promptgenmatched
            ]

        # Analysis level cuts
        leptoncut = events.ee | events.mm

        # third lepton veto
        leptoncut = leptoncut & (
            ak.fill_none(
                ak.mask(
                    ak.all(events.Lepton[:, 2:].pt < 10, axis=-1),
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

        # BTag

        btag_cut = (
            (events.Jet.pt > 30)
            & (abs(events.Jet.eta) < 2.5)
            & (events.Jet.btagDeepFlavB > cfg["btagMedium"])
        )
        events["bVeto"] = ak.num(events.Jet[btag_cut]) == 0
        events["bTag"] = ak.num(events.Jet[btag_cut]) >= 1

        if not isData:
            # Load all SFs
            # FIXME should remove btagSF
            events["btagSF"] = ak.prod(
                events.Jet[events.Jet.pt >= 30].btagSF_deepjet_shape, axis=1
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
            )

        # Variable definitions
        events["jets"] = ak.pad_none(events.Jet, 2)
        for variable in variables:
            if "func" in variables[variable]:
                events[variable] = variables[variable]["func"](events)

        # events["dR_l1_jets"] = ak.fill_none(
        #     ak.min(events.Lepton[:, 0].deltaR(jets[:, :]), axis=1), -1
        # )
        # events["dR_l2_jets"] = ak.fill_none(
        #     ak.min(events.Lepton[:, 1].deltaR(jets[:, :]), axis=1), -1
        # )
        # events["dR_l1_l2"] = events.Lepton[:, 0].deltaR(events.Lepton[:, 1])

        # Apply cuts

        # Preselection

        # events = events[(events.mjj > 200)]
        # jets = jets[events.bVeto]
        # events = events[events.bVeto]

        events = events[
            ak.fill_none(
                (events.njet >= 2)
                & (events.mjj >= 200)
                & (events.jets[:, 0].pt >= 30)
                & (events.jets[:, 1].pt >= 30)
                & (events.mll > 50),
                False,
            )
        ]

        events = dnn_evaluator(
            onnx_session,
            events,
            dnn_t,
            dnn_cfg,
        )

        # print("DNN", ak.min(events.dnn), ak.max(events.dnn))

        events[dataset] = ak.ones_like(events.run) == 1.0

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
            jet_genmatched = (events.Jet.genJetIdx >= 0) & (
                events.Jet.genJetIdx < ak.num(events.GenJet)
            )
            both_jets_gen_matched = ak.fill_none(
                jet_genmatched[:, 0] & jet_genmatched[:, 1], False
            )
            events["hard"] = gen_mask & both_jets_gen_matched
            events["PU"] = gen_mask & ~both_jets_gen_matched

        if subsamples != {}:
            for subsample in subsamples:
                events[f"{dataset}_{subsample}"] = eval(subsamples[subsample])

        for region in regions:
            regions[region]["mask"] = regions[region]["func"](events)

        # weight_name = "weight"

        # Fill histograms
        for dataset_name in results:
            for region in regions:
                # for category in categories:
                # Apply mask for specific region, category and dataset_name
                mask = (
                    regions[region]["mask"]
                    # & (events[categories[0]] | events[categories[1]])
                    # & events[category]
                    & events[dataset_name]
                )

                # # Renorm for btag in region
                # if not isData:
                #     sumw_before_btagsf = ak.sum(events[mask].weight)
                #     events[weight_name] = events.weight * events.btagSF
                #     sumw_after_btagsf = ak.sum(events[mask].weight_btag)
                #     btag_norm = sumw_before_btagsf / sumw_after_btagsf
                #     # print(dataset_name, region, cat, 'btag norm', btag_norm)
                #     events[weight_name] = events.weight_btag * btag_norm
                # else:
                #     events[weight_name] = events.weight

                btag_cut = regions[region].get("btagging", dataset_name)
                mask = mask & events[btag_cut]
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
                            # category=f"{region}_{category}",
                            category=region,
                            syst=variation,
                            weight=events["weight"][mask],
                        )
                    else:
                        var_name = variables[variable]["axis"].name
                        results[dataset_name]["histos"][variable].fill(
                            events[var_name][mask],
                            # category=f"{region}_{category}",
                            category=region,
                            syst=variation,
                            weight=events["weight"][mask],
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
    # with open("chunks_job.pkl", "rb") as file:
    #     new_chunks = cloudpickle.loads(zlib.decompress(file.read()))
    chunks_readable = False
    new_chunks = read_chunks("chunks_job.pkl", readable=chunks_readable)
    print("N chunks to process", len(new_chunks))

    results = {}
    errors = []
    # for new_chunk in new_chunks:
    for i in range(len(new_chunks)):
        new_chunk = new_chunks[i]

        if new_chunk["result"] != {}:
            print(
                "Skip chunk",
                {k: v for k, v in new_chunk["data"].items() if k != "read_form"},
                "was already processed",
            )
            continue

        # if new_chunk["data"].get("is_data", False):
        #     continue
        # if new_chunk["dataset"] != "Zjj":
        #     continue
        print(new_chunk["data"]["dataset"])
        try:
            # result = big_process(process=process, **new_chunk["data"])
            new_chunks[i]["result"] = big_process(process=process, **new_chunk["data"])
            new_chunks[i]["error"] = ""
        except Exception as e:
            print("\n\nError for chunk", new_chunk, file=sys.stderr)
            nice_exception = "".join(tb.format_exception(None, e, e.__traceback__))
            print(nice_exception, file=sys.stderr)
            # errors.append(dict(**new_chunk, error=nice_exception))
            new_chunks[i]["result"] = {}
            new_chunks[i]["error"] = nice_exception
            # result = None

        # if i >= 2:
        #     break

    # print("Results", results)
    # print("Errors", errors)

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

    # with open("results.pkl", "wb") as file:
    #     file.write(zlib.compress(cloudpickle.dumps({"results": {}, "errors": errors})))
