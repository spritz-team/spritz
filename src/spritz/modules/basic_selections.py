import awkward as ak
from data.common.TrigMaker_cfg import Trigger


def pass_trigger(events, ERA):
    keys = ["EleMu", "SingleEle", "DoubleEle", "SingleMu", "DoubleMu"]
    for key in keys:
        events[key] = ak.ones_like(events.weight) == 0.0  # all False

    for era in Trigger[ERA]:
        for key in keys:
            tmp = ak.ones_like(events.weight) == 0.0  # all False
            for val in Trigger[ERA][era]["MC"][key]:
                tmp = tmp | events.HLT[val]
            events[key] = events[key] | (events.run_period == era) & tmp

    pass_trigger = ak.ones_like(events.weight) == 0.0  # all False
    for key in keys:
        pass_trigger = pass_trigger | events[key]
    events["pass_trigger"] = pass_trigger
    return events


def pass_flags(events, flags):
    events["pass_flags"] = ak.ones_like(events.weight) == 1.0  # all True
    for flag in flags:
        events["pass_flags"] = events["pass_flags"] & events.Flag[flag]
    return events


def lumi_mask(events, lumimask):
    return events[lumimask(events.run, events.luminosityBlock)]
