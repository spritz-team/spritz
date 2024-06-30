import awkward as ak
from data.common import LeptonSel


def createLepton(events):

    events[("Muon", "mass")] = ak.zeros_like(events.Muon.pt)
    events[("Electron", "mass")] = ak.zeros_like(events.Electron.pt)

    ele_none = ak.mask(events.Electron.pt, ak.is_none(events.Electron.pt, axis=1))
    mu_none = ak.mask(events.Muon.pt, ak.is_none(events.Muon.pt, axis=1))

    Lepton = ak.zip(
        {
            "pt": ak.concatenate([events.Electron.pt, events.Muon.pt], axis=1),
            "eta": ak.concatenate([events.Electron.eta, events.Muon.eta], axis=1),
            "phi": ak.concatenate([events.Electron.phi, events.Muon.phi], axis=1),
            "mass": ak.concatenate([events.Electron.mass, events.Muon.mass], axis=1),
            "pdgId": ak.concatenate([events.Electron.pdgId, events.Muon.pdgId], axis=1),
            "electronIdx": ak.values_astype(
                ak.concatenate(
                    [ak.local_index(events.Electron, axis=1), mu_none], axis=1
                ),
                int,
            ),
            "muonIdx": ak.values_astype(
                ak.concatenate([ele_none, ak.local_index(events.Muon, axis=1)], axis=1),
                int,
            ),
        },
        with_name="Momentum4D",
    )

    Lepton = Lepton[(abs(Lepton.pdgId) == 11) | (abs(Lepton.pdgId) == 13)]
    Lepton = Lepton[ak.argsort(Lepton.pt, ascending=False, axis=-1)]
    events["Lepton"] = Lepton
    return events


def leptonSel(events):
    ElectronWP = LeptonSel.ElectronWP["Full2018v9"]
    MuonWP = LeptonSel.MuonWP["Full2018v9"]

    ele_mask = abs(events.Lepton.pdgId) == 11
    mu_mask = abs(events.Lepton.pdgId) == 13

    electron_col = events.Electron[ak.mask(events.Lepton.electronIdx, ele_mask)]
    muon_col = events.Muon[ak.mask(events.Lepton.muonIdx, mu_mask)]

    for wp in ElectronWP["FakeObjWP"]:
        comb = ak.ones_like(electron_col.pt) == 1.0
        for key, cuts in ElectronWP["FakeObjWP"][wp]["cuts"].items():
            tmp1 = eval(key.replace("[LF_idx]", ""))
            tmp2 = ak.ones_like(electron_col.pt) == 1.0
            for cut in cuts:
                tmp2 = tmp2 & eval(cut.replace("[LF_idx]", ""))
            comb = comb & (~tmp1 | tmp2)
        comb = ak.values_astype(comb, bool)
        events[("Lepton", "ele_isLoose")] = ak.where(ele_mask, comb, False)

    for wp in MuonWP["FakeObjWP"]:
        comb = ak.ones_like(muon_col.pt) == 1.0
        for key, cuts in MuonWP["FakeObjWP"][wp]["cuts"].items():
            tmp1 = eval(key.replace("[LF_idx]", ""))
            tmp2 = ak.ones_like(muon_col.pt) == 1.0
            for cut in cuts:
                tmp2 = tmp2 & eval(cut.replace("[LF_idx]", ""))
            comb = comb & (~tmp1 | tmp2)
        comb = ak.values_astype(comb, bool)
        events[("Lepton", "mu_isLoose")] = ak.where(mu_mask, comb, False)

    events[("Lepton", "isLoose")] = ak.values_astype(
        events.Lepton.ele_isLoose | events.Lepton.mu_isLoose, bool
    )
    events[("Lepton", "isLoose")] = ak.fill_none(events.Lepton.isLoose, False)

    for wp in ElectronWP["TightObjWP"]:
        comb = ak.ones_like(electron_col.pt) == 1.0
        for key, cuts in ElectronWP["TightObjWP"][wp]["cuts"].items():
            tmp1 = eval(key.replace("[LF_idx]", ""))
            tmp2 = ak.ones_like(electron_col.pt) == 1.0
            for cut in cuts:
                tmp2 = tmp2 & eval(cut.replace("[LF_idx]", ""))
            comb = comb & (~tmp1 | tmp2)
        comb = ak.values_astype(comb, bool)
        events[("Lepton", "isTightElectron_" + wp)] = ak.where(ele_mask, comb, False)

    for wp in MuonWP["TightObjWP"]:
        comb = ak.ones_like(muon_col.pt) == 1.0
        for key, cuts in MuonWP["TightObjWP"][wp]["cuts"].items():
            tmp1 = eval(key.replace("[LF_idx]", ""))
            tmp2 = ak.ones_like(muon_col.pt) == 1.0
            for cut in cuts:
                tmp2 = tmp2 & eval(cut.replace("[LF_idx]", ""))
            comb = comb & (~tmp1 | tmp2)
        comb = ak.values_astype(comb, bool)
        events[("Lepton", "isTightMuon_" + wp)] = ak.where(mu_mask, comb, False)

    return events
