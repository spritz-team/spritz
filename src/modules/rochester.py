import awkward as ak
import numpy as np
from coffea.lookup_tools import txt_converters, rochester_lookup


def getRochester(cfg):
    rochester_file = cfg["rochester_file"]
    rochester_data = txt_converters.convert_rochester_file(
        rochester_file, loaduncs=True
    )
    rochester = rochester_lookup.rochester_lookup(rochester_data)
    return rochester


def correctRochester(events, is_data, rochester):
    # muons = events.Muon[ak.mask(events.Lepton.muonIdx, mu_mask)]
    muons = events.Muon
    muons["charge"] = muons.pdgId / (-abs(muons.pdgId))

    if is_data:
        muSF = rochester.kScaleDT(
            muons["charge"], muons["pt"], muons["eta"], muons["phi"]
        )
    else:
        muons["genPartIdx"] = ak.mask(muons.genPartIdx, muons.genPartIdx >= 0)
        # if reco pt has corresponding gen pt
        mcSF1 = rochester.kSpreadMC(
            muons["charge"],
            muons["pt"],
            muons["eta"],
            muons["phi"],
            events.GenPart[muons.genPartIdx].pt,
        )
        # if reco pt has no corresponding gen pt
        counts = ak.num(muons["pt"])
        mc_rand = np.random.uniform(size=ak.sum(counts))
        mc_rand = ak.unflatten(mc_rand, counts)
        mcSF2 = rochester.kSmearMC(
            muons["charge"],
            muons["pt"],
            muons["eta"],
            muons["phi"],
            muons["nTrackerLayers"],
            mc_rand,
        )
        # Combine the two scale factors and scale the pt
        muSF = ak.where(ak.is_none(muons.genPartIdx, axis=1), mcSF2, mcSF1)
        # Remove masking from layout, none of the SF are masked here
        muSF = ak.fill_none(muSF, 0)
    mu_pt = muSF * muons.pt

    # remap to Lepton.pt
    mu_pt = mu_pt[events.Lepton.muonIdx]
    mu_mask = abs(events.Lepton.pdgId) == 13

    events[("Lepton", "pt")] = ak.where(mu_mask, mu_pt, events.Lepton.pt)
    return events
