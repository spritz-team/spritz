import correctionlib
import awkward as ak
import numba
import numpy as np


def jetSel(events, cfg):
    ceval_jetId = correctionlib.CorrectionSet.from_file(cfg["jetId"])

    minpt = cfg["jet_sel"]["minpt"]
    maxeta = cfg["jet_sel"]["maxeta"]
    jet = events.Jet

    # for 2024 have to define jetId
    # eta < 2.6

    # NumNeutralParticle = neMultiplicity
    # NEMF (Neutral EM fraction) = neEmEF
    # NHF (Neutral hadron fraction) = neHEF
    # CEMF (Charged hadron fraction) = chHEF
    # CEMF (Charged EM fraction) = chEmEF
    # CHM (Charged hadron multiplicity) = chMultiplicity
    # MUF (Muon fraction) = muEF
    # NumConst (Number of Constituents) = nConstituents

    jet["jetId"] = ceval_jetId["AK4PUPPI_TightLeptonVeto"].evaluate(
        jet.eta,
        jet.chHEF,
        jet.neHEF,
        jet.chEmEF,
        jet.neEmEF,
        jet.muEF,
        jet.chMultiplicity,
        jet.neMultiplicity,
        jet.chMultiplicity + jet.neMultiplicity,
    )
    jet = jet[jet.jetId == 1.0]

    # jet = jet[jet.puIdDisc < 0.1 ]

    # jet["jetId"] = (
    #     (
    #         (abs(jet.eta) <= 2.6)
    #         & (jet.chHEF < 0.8)
    #         & (jet.chMultiplicity > 0)
    #         & (jet.chHF > 0.01)
    #         & (jet.nConstituents > 1)
    #         & (jet.neEMF < 0.9)
    #         & (jet.muEF < 0.8)
    #         & (jet.neHF < 0.9)
    #     )
    #     | (
    #         ((abs(jet.eta) > 2.6) & (abs(jet.eta) <= 2.7))
    #         & (jet.chHEF < 0.8)
    #         & (jet.neEMF < 0.99)
    #         & (jet.muEF < 0.8)
    #         & (jet.neHF < 0.9)
    #     )
    #     | ((abs(jet.eta) > 2.7) & (abs(jet.eta) <= 3.0) & (jet.neHF < 0.9999))
    #     | (
    #         ((abs(jet.eta) > 3.0) & (abs(jet.eta) <= 5.0))
    #         & (jet.neEMF < 0.90)
    #         & (jet.neMultiplicity > 2)
    #     )
    # )

    # pass_puId = ak.values_astype(jet.puId & puId_shift, bool)
    select = jet.pt >= minpt
    select = select & (abs(jet.eta) <= maxeta)
    # select = select & (jet.jetId >= jetId)
    # select = select & (pass_puId | (jet.pt > 50.0))
    events["Jet"] = events.Jet[select]
    return events


@numba.njit
def goodJet_kernel(jet, lepton, fixed_dr, builder):
    for ievent in range(len(jet)):
        builder.begin_list()
        for ijet in range(len(jet[ievent])):
            dRs = np.ones(len(lepton[ievent])) * 10
            for ipart in range(len(lepton[ievent])):
                single_jet = jet[ievent][ijet]
                single_lepton = lepton[ievent][ipart]
                dRs[ipart] = single_jet.deltaR(single_lepton)
            builder.boolean(~np.any(dRs < fixed_dr))
        builder.end_list()
    return builder


def goodJet_func(jets, leptons, fixed_dr):
    if ak.backend(jets) == "typetracer":
        # here we fake the output of find_4lep_kernel since
        # operating on length-zero data returns the wrong layout!
        ak.typetracer.length_zero_if_typetracer(
            jets.pt
        )  # force touching of the necessary data
        return ak.Array(ak.Array([[True]]).layout.to_typetracer(forget_length=True))

    return goodJet_kernel(jets, leptons, fixed_dr, ak.ArrayBuilder()).snapshot()


def clean_collection(events, coll1, coll2, fixed_dr=0.3):
    mask = goodJet_func(events[coll1], events[coll2], fixed_dr)
    mask = ak.values_astype(mask, bool, including_unknown=True)

    events[coll1] = events[coll1][mask]
    return events
