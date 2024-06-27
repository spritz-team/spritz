from coffea.lookup_tools.correctionlib_wrapper import correctionlib_wrapper
import awkward as ak
import variation as variation_module

btag_base_var = [
    "lf",
    "hf",
    "hfstats1",
    "hfstats2",
    "lfstats1",
    "lfstats2",
    "cferr1",
    "cferr2",
]
btag_jes_var = [
    "jes",
    # "jesAbsolute",
    # "jesAbsolute_RPLME_YEAR",
    # "jesBBEC1",
    # "jesBBEC1_RPLME_YEAR",
    # "jesEC2",
    # "jesEC2_RPLME_YEAR",
    # "jesFlavorQCD",
    # "jesHF",
    # "jesHF_RPLME_YEAR",
    # "jesRelativeBal",
    # "jesRelativeSample_RPLME_YEAR",
]


@variation_module.vary(reads_columns=[("Jet", "pt"), ("Jet", "eta")])
def func(events, variations, ceval_btag, cfg, doVariations: bool = False):
    wrap_c = correctionlib_wrapper(ceval_btag["deepJet_shape"])
    nominal_branch_name = "btagSF_deepjet_shape"
    if not doVariations:
        variation = "central"
        branch_name = nominal_branch_name
        mask = (abs(events.Jet.eta) < 2.5) & (events.Jet.pt > 15.0)
        mask = mask & (
            (events.Jet.hadronFlavour == 0) | (events.Jet.hadronFlavour == 5)
        )
        jets_btag = ak.mask(events.Jet, mask)
        btags = wrap_c(
            variation,
            jets_btag.hadronFlavour,
            abs(jets_btag.eta),
            jets_btag.pt,
            jets_btag.btagDeepFlavB,
        )
        btags = ak.fill_none(btags, 1.0)
        events[("Jet", branch_name)] = btags
    else:
        branch_names = []
        clib_variation_names = []
        variation_names = []
        branch_name = nominal_branch_name
        for variation in btag_base_var + btag_jes_var:
            variation = variation.replace("RPLME_YEAR", cfg["year"])
            for tag in ["up", "down"]:
                # used to access correctionlib
                clib_variation_names.append(tag + "_" + variation)

                # the name that will be registered for the variation
                # FIXME cannot see tag
                variation_name_nice = f"btag_{variation}_{tag}"
                variation_names.append(variation_name_nice)
                varied_branch_name = variation_module.Variation.format_varied_column(
                    ("Jet", branch_name), variation_names[-1]
                )
                branch_names.append(varied_branch_name)

        for branch_name, clib_name, variation_name in zip(
            branch_names, clib_variation_names, variation_names
        ):
            mask = (abs(events.Jet.eta) < 2.5) & (events.Jet.pt > 15.0)
            if "cferr" in variation_name:
                mask = mask & (events.Jet.hadronFlavour == 4)
            else:
                mask = mask & (
                    (events.Jet.hadronFlavour == 0) | (events.Jet.hadronFlavour == 5)
                )
            jets_btag = ak.mask(events.Jet, mask)
            btags = wrap_c(
                clib_name,
                jets_btag.hadronFlavour,
                abs(jets_btag.eta),
                jets_btag.pt,
                jets_btag.btagDeepFlavB,
            )
            btags = ak.fill_none(btags, 1.0)
            events[branch_name] = btags
            variations.register_variation([('Jet', nominal_branch_name)], variation_name)
    return events, variations


def btag_sf(events, variations, ceval_btag, cfg):
    events, variations = func(events, variations, ceval_btag, cfg, doVariations=False)
    events, variations = func(events, variations, ceval_btag, cfg, doVariations=True)
    return events, variations
