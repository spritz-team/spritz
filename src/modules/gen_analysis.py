import awkward as ak

from modules.jet_sel import goodJet_func


def cuts(events):
    events["GenLep"] = ak.pad_none(events.GenLep, 3, clip=True)
    events["GenJet"] = ak.pad_none(events.GenJet, 2, clip=False)

    events["Gen_mll"] = ak.fill_none(
        (events.GenLep[:, 0] + events.GenLep[:, 1]).mass, -10
    )
    events["Gen_ptll"] = ak.fill_none(
        (events.GenLep[:, 0] + events.GenLep[:, 1]).pt, -10
    )

    events["Gen_dphill"] = ak.fill_none(
        abs(events.GenLep[:, 0].deltaphi(events.GenLep[:, 1])), -10
    )
    events["Gen_dphijj"] = ak.fill_none(
        abs(events.GenJet[:, 0].deltaphi(events.GenJet[:, 1])), -10
    )

    events["Gen_detajj"] = ak.fill_none(
        abs(events.GenJet[:, 0].deltaeta(events.GenJet[:, 1])), -10
    )

    events["Gen_mjj"] = ak.fill_none(
        (events.GenJet[:, 0] + events.GenJet[:, 1]).mass, -10
    )

    events["fiducial_cut"] = ak.fill_none((events.GenLep.pt[:, 1] > 10), False)
    events["fiducial_cut"] = events["fiducial_cut"] & ak.fill_none(
        events.GenLep[:, 2].pt < 10, True
    )
    events["fiducial_cut"] = events["fiducial_cut"] & ak.fill_none(
        events.GenJet[:, 1].pt > 50, False
    )
    events["fiducial_cut"] = events["fiducial_cut"] & ak.fill_none(
        abs(events.Gen_mll - 91.0) < 15, False
    )
    events["fiducial_cut"] = events["fiducial_cut"] & ak.fill_none(
        events.Gen_mjj > 200, False
    )

    return events


def gen_analysis(events, dataset):
    GenLep = events["GenDressedLepton"]
    GenLepMask = (
        # GenLep.isPrompt &
        (GenLep.pt > 10.0) & ((abs(GenLep.pdgId) == 11) | (abs(GenLep.pdgId) == 13))
    )
    events["GenLep"] = GenLep[GenLepMask]

    GenJet = events["GenJet"]
    mask = goodJet_func(GenJet, GenLep)
    mask = ak.values_astype(mask, bool, including_unknown=True)

    events["GenJet"] = GenJet[mask]

    events = cuts(events)

    return events
