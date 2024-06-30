def puweight_sf(events, variations, ceval_puWeight, cfg):

    events["puWeight"] = ceval_puWeight[cfg["puWeightsKey"]].evaluate(
        events.Pileup.nTrueInt, "nominal"
    )

    # FIXME should add all the variations

    return events, variations
