import awkward as ak
import numba


def prompt_gen_match_leptons(events):
    only_ele_mu = (
        (abs(events.GenPart.pdgId) == 11) | (abs(events.GenPart.pdgId) == 13)
    ) & (events.GenPart.status == 1)
    only_tau = abs(events.GenPart.pdgId) == 15

    isDecayed = ak.values_astype((events.GenPart.statusFlags >> 1) & 1, bool)
    LastCopy = ak.values_astype((events.GenPart.statusFlags >> 13) & 1, bool)

    genlep_mask = only_ele_mu | (only_tau & isDecayed & LastCopy)

    genleptons = events.GenPart[genlep_mask]
    genleptons["isPrompt"] = ak.values_astype(genleptons.statusFlags & 1, bool)
    genleptons["isDirectPromptTauDecayProduct"] = ak.values_astype(
        (genleptons.statusFlags >> 5) & 1, bool
    )

    @numba.njit
    def leptonPromptGen_kernel(
        leptons, gen_leptons, status, isPrompt, isDirectPromptTauDecayProduct, builder
    ):
        for ievent in range(len(leptons)):
            builder.begin_list()
            for ilep in range(len(leptons[ievent])):
                isPromptMatched = False
                for igen in range(len(gen_leptons[ievent])):
                    lep = leptons[ievent][ilep]
                    gen = gen_leptons[ievent][igen]
                    dR = lep.deltaR(gen)
                    if dR < 0.3 and status[ievent][igen] == 1:
                        if (
                            isPrompt[ievent][igen]
                            or isDirectPromptTauDecayProduct[ievent][igen]
                        ):
                            isPromptMatched = True

                builder.boolean(isPromptMatched)
            builder.end_list()
        return builder

    def leptonPromptGen(
        leptons, gen_leptons, status, isPrompt, isDirectPromptTauDecayProduct
    ):
        if ak.backend(leptons) == "typetracer":
            ak.typetracer.length_zero_if_typetracer(
                leptons.pt
            )  # force touching of the necessary data
            return ak.Array(ak.Array([[True]]).layout.to_typetracer(forget_length=True))

        return leptonPromptGen_kernel(
            leptons,
            gen_leptons,
            status,
            isPrompt,
            isDirectPromptTauDecayProduct,
            ak.ArrayBuilder(),
        ).snapshot()

    mask = leptonPromptGen(
        events.Lepton,
        genleptons,
        genleptons.status,
        genleptons.isPrompt,
        genleptons.isDirectPromptTauDecayProduct,
    )

    isPrompt = ak.values_astype(mask, to=bool, including_unknown=True)
    events[("Lepton", "promptgenmatched")] = isPrompt
    return events
