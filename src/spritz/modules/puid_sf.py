from typing import NewType

import awkward as ak
import spritz.framework.variation as variation
from spritz.framework.framework import correctionlib_wrapper

correctionlib_evaluator = NewType("correctionlib_evaluator", any)




def format_rule(column, variation_name):
    tag = variation_name.split("_")[-1]
    if isinstance(column, str):
        return f"{column}_{tag}"
    elif isinstance(column, tuple):
        _list = list(column[:-1])
        _list.append(f"{column[-1]}_{tag}")
        return tuple(_list)
    else:
        print("Cannot format varied column", column, "for variation", variation_name)
        raise Exception


@variation.vary(reads_columns=[("Jet", "pt"), ("Jet", "puId"), ("Jet", "genJetIdx")])
def func(
    events: ak.Array,
    variations: variation.Variation,
    ceval_puid: correctionlib_evaluator,
    cfg,
    doVariations: bool = False,
):
    wrap_c = correctionlib_wrapper(ceval_puid["PUJetID_eff"])
    if "2016" not in cfg["era"]:
        puId_shift = 1 << 2
    else:
        puId_shift = 1 << 0
    pass_puId = ak.values_astype(events.Jet.puId & puId_shift, bool)

    jet_genmatched = (events.Jet.genJetIdx >= 0) & (
        events.Jet.genJetIdx < ak.num(events.GenJet)
    )
    mask = jet_genmatched & pass_puId & (15.0 < events.Jet.pt) & (events.Jet.pt < 50.0)
    jets = ak.mask(events.Jet, mask)

    if not doVariations:
        sf = wrap_c(jets.eta, jets.pt, "nom", "L")
        sf = ak.fill_none(sf, 1.0)
        events[("Jet", "PUID_SF")] = sf
    else:
        sf_up = wrap_c(jets.eta, jets.pt, "up", "L")
        sf_down = wrap_c(jets.eta, jets.pt, "down", "L")

        sf_up = ak.fill_none(sf_up, 1.0)
        sf_down = ak.fill_none(sf_down, 1.0)

        events[("Jet", "PUID_SF_up")] = sf_up
        events[("Jet", "PUID_SF_down")] = sf_down

        variations.register_variation(
            columns=[("Jet", "PUID_SF")],
            variation_name="PUID_SF_up",
            format_rule=format_rule,
        )
        variations.register_variation(
            columns=[("Jet", "PUID_SF")],
            variation_name="PUID_SF_down",
            format_rule=format_rule,
        )

    return events, variations


def puid_sf(events, variations, ceval_puid, cfg):
    events, variations = func(events, variations, ceval_puid, cfg, doVariations=False)
    # now doing variations

    events, variations = func(events, variations, ceval_puid, cfg, doVariations=True)

    return events, variations
