import awkward as ak


def hardPUJets(events):
    jet = events.Jet
    jet_genmatched = (jet.genJetIdx >= 0) & (jet.genJetIdx < ak.num(events.GenJet))
    jet_genmatched = ak.pad_none(jet_genmatched, 2)
    both_jets_gen_matched = ak.fill_none(
        jet_genmatched[:, 0] & jet_genmatched[:, 1], False
    )
    events["hard"] = both_jets_gen_matched
    events["PU"] = ~both_jets_gen_matched
    return events
