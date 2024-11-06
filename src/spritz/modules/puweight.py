from spritz.framework.variation import Variation


def puweight_sf(events, variations: Variation, ceval_puWeight, cfg):
    events["puWeight"] = ceval_puWeight[cfg["puWeightsKey"]].evaluate(
        events.Pileup.nTrueInt, "nominal"
    )

    events["puWeight_PU_up"] = ceval_puWeight[cfg["puWeightsKey"]].evaluate(
        events.Pileup.nTrueInt, "up"
    )
    events["puWeight_PU_down"] = ceval_puWeight[cfg["puWeightsKey"]].evaluate(
        events.Pileup.nTrueInt, "down"
    )
    variations.register_variation(['puWeight'], 'PU_up')
    variations.register_variation(['puWeight'], 'PU_down')

    return events, variations
