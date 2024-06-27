import awkward as ak


def pass_trigger(events, tgr_data):
    events["pass_trigger"] = ak.ones_like(events.weight) == 0.0  # all False
    for key, values in tgr_data.items():
        events[key] = ak.ones_like(events.weight) == 0.0  # all False
        for val in values:
            events[key] = events[key] | events.HLT[val]
        events["pass_trigger"] = events["pass_trigger"] | events[key]
    return events


def pass_flags(events, flags):
    events["pass_flags"] = ak.ones_like(events.weight) == 1.0  # all True
    for flag in flags:
        events["pass_flags"] = events["pass_flags"] & events.Flag[flag]
    return events


def lumi_mask(events, lumimask):
    return events[lumimask(events.run, events.luminosityBlock)]
