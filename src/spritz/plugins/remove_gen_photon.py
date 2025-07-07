import awkward as ak


def removeGenPhoton(events):
    gen_photons = (
        (events.GenPart.pdgId == 22)
        & ak.values_astype(events.GenPart.statusFlags & 1, bool)
        & (events.GenPart.status == 1)
        & (events.GenPart.pt > 15)
        & (abs(events.GenPart.eta) < 2.6)
    )
    gen_mask = ak.num(events.GenPart[gen_photons]) == 0
    events = events[gen_mask]
    return events
