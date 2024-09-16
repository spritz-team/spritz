import awkward as ak
from data.common.TrigMaker_cfg import Trigger

pt_min_max = {
    11: [10 + 1e-3, 100 - 1e-3],
    13: [10 + 1e-3, 200 - 1e-3],
}
eta_min_max = {
    11: [-2.5 + 1e-3, 2.5 - 1e-3],
    13: [-2.4 + 1e-3, 2.4 - 1e-3],
}


def max_vec(vec, val):
    return ak.where(vec > val, vec, val)


def over_under(val, min, max):
    val = ak.where(val >= max, max, val)
    val = ak.where(val <= min, min, val)
    return val


def trigger_sf(events, variations, cset_trigger, cfg):
    year = cfg["era"]

    trigger_sf = ak.ones_like(events.run_period)
    for era in Trigger[year]:
        trigger_events = ak.mask(
            events, (events.run_period == 1) & (ak.num(events.Lepton) >= 2)
        )

        idxs = [0, 1, 0, 1, 0, 1]

        effData = [ak.ones_like(trigger_events.run_period) for _ in range(len(idxs))]
        effMC = [ak.ones_like(trigger_events.run_period) for _ in range(len(idxs))]

        DRll_SF = ak.ones_like(trigger_events.run_period)

        eff_gl = [ak.ones_like(trigger_events.run_period) for _ in range(3)]

        effData_dz = ak.ones_like(trigger_events.run_period)
        effMC_dz = ak.ones_like(trigger_events.run_period)

        legss = [
            (
                [
                    "SingleEle",
                    "SingleEle",
                    "DoubleEleLegHigPt",
                    "DoubleEleLegHigPt",
                    "DoubleEleLegLowPt",
                    "DoubleEleLegLowPt",
                ],
                [11, 11],
                "DoubleEle",
            ),
            (
                [
                    "SingleMu",
                    "SingleMu",
                    "DoubleMuLegHigPt",
                    "DoubleMuLegHigPt",
                    "DoubleMuLegLowPt",
                    "DoubleMuLegLowPt",
                ],
                [13, 13],
                "DoubleMu",
            ),
            (
                [
                    "SingleEle",
                    "SingleMu",
                    "EleMuLegHigPt",
                    "MuEleLegHigPt",
                    "MuEleLegLowPt",
                    "EleMuLegLowPt",
                ],
                [11, 13],
                "EleMu",
            ),
            (
                [
                    "SingleMu",
                    "SingleEle",
                    "MuEleLegHigPt",
                    "EleMuLegHigPt",
                    "EleMuLegLowPt",
                    "MuEleLegLowPt",
                ],
                [13, 11],
                "MuEle",
            ),
        ]

        for legs, pdgs, combo_name in legss:
            mask = (abs(trigger_events.Lepton.pdgId[:, 0]) == pdgs[0]) & (
                abs(trigger_events.Lepton.pdgId[:, 1]) == pdgs[1]
            )
            leptons = ak.mask(trigger_events.Lepton, mask)

            # DZ for Data and MC
            dz_type, dz_value = list(
                Trigger[year][era]["DZEffData"][combo_name].items()
            )[0]
            pvs = ak.where(
                trigger_events.PV.npvsGood > 69, 69, trigger_events.PV.npvsGood
            )
            # mask low pts and fill 1.0 for DZ, should be removed from the analysis
            pt1 = ak.where(leptons[:, 0].pt > 99.9, 99.9, leptons[:, 0].pt)
            pt1 = ak.mask(pt1, pt1 >= 25.0)
            pt2 = ak.where(leptons[:, 1].pt > 99.9, 99.9, leptons[:, 1].pt)
            pt2 = ak.mask(pt1, pt1 >= 10.0)
            if dz_type == "value":
                effData_dz = ak.where(mask, dz_value[0], effData_dz)
            elif dz_type == "nvtx":
                sf = cset_trigger[f"{era}_DZEff_Data_{combo_name}"].evaluate("eff", pvs)
                effData_dz = ak.where(mask, sf, effData_dz)
            elif dz_type == "pt1:pt2":
                sf = cset_trigger[f"{era}_DZEff_Data_{combo_name}"].evaluate(
                    "eff",
                    pt1,
                    pt2,
                )
                sf = ak.fill_none(sf, 1.0)
                effData_dz = ak.where(mask, sf, effData_dz)
            dz_type, dz_value = list(Trigger[year][era]["DZEffMC"][combo_name].items())[
                0
            ]
            if dz_type == "value":
                effMC_dz = ak.where(mask, dz_value[0], effMC_dz)
            elif dz_type == "nvtx":
                sf = cset_trigger[f"{era}_DZEff_MC_{combo_name}"].evaluate("eff", pvs)
                effMC_dz = ak.where(mask, sf, effMC_dz)
            elif dz_type == "pt1:pt2":
                sf = cset_trigger[f"{era}_DZEff_MC_{combo_name}"].evaluate(
                    "eff",
                    pt1,
                    pt2,
                )
                sf = ak.fill_none(sf, 1.0)
                effMC_dz = ak.where(mask, sf, effMC_dz)

            # DRll SF
            drll = leptons[:, 0].deltaR(leptons[:, 1])
            sf = cset_trigger[f"DRllSF_{combo_name}"].evaluate(drll)
            DRll_SF = ak.where(mask, sf, DRll_SF)
            for i, name in enumerate([legs[0], legs[1], combo_name]):
                eff_gl[i] = ak.where(
                    mask, Trigger[year][era]["GlEff"][name][0], eff_gl[i]
                )

            # Leg Efficiencies
            for i, (leg, idx) in enumerate(zip(legs, idxs)):
                pt = ak.copy(leptons[:, idx].pt)
                eta = ak.copy(leptons[:, idx].eta)

                pt = over_under(pt, *pt_min_max[pdgs[idx]])
                eta = over_under(eta, *eta_min_max[pdgs[idx]])

                data_type = "Data"
                sf = cset_trigger[f"{era}_LegEff_{data_type}_{leg}"].evaluate(
                    "eff",
                    eta,
                    pt,
                )
                effData[i] = ak.where(mask, sf, effData[i])
                data_type = "MC"
                sf = cset_trigger[f"{era}_LegEff_{data_type}_{leg}"].evaluate(
                    "eff",
                    eta,
                    pt,
                )
                effMC[i] = ak.where(mask, sf, effMC[i])

        effData_dbl = max_vec(
            (
                effData[4] * effData[3]
                + effData[2] * effData[5]
                - effData[3] * effData[2]
            )
            * eff_gl[2]
            * effData_dz,
            0.0001,
        )
        effData_sgl = (
            effData[0] * eff_gl[0]
            + effData[1] * eff_gl[1]
            - effData[0] * effData[1] * eff_gl[0] * eff_gl[1]
        )
        effData_evt = (
            effData_dbl
            + effData_sgl
            - effData[5] * eff_gl[2] * effData[0] * eff_gl[0]
            - effData[4]
            * eff_gl[2]
            * effData[1]
            * eff_gl[1]
            * (1 - effData[5] * eff_gl[2] * effData[0] * eff_gl[0] / effData_dbl)
        ) * DRll_SF

        effMC_dbl = max_vec(
            (effMC[4] * effMC[3] + effMC[2] * effMC[5] - effMC[3] * effMC[2])
            * eff_gl[2]
            * effMC_dz,
            0.0001,
        )

        effMC_sgl = (
            effMC[0] * eff_gl[0]
            + effMC[1] * eff_gl[1]
            - effMC[0] * effMC[1] * eff_gl[0] * eff_gl[1]
        )
        effMC_evt = (
            effMC_dbl
            + effMC_sgl
            - effMC[5] * eff_gl[2] * effMC[0] * eff_gl[0]
            - effMC[4]
            * eff_gl[2]
            * effMC[1]
            * eff_gl[1]
            * (1 - effMC[5] * eff_gl[2] * effMC[0] * eff_gl[0] / effMC_dbl)
        ) * DRll_SF

        sf = effData_evt / effMC_evt
        sf = ak.fill_none(sf, 1.0)
        trigger_sf = ak.where(events.run_period == era, sf, trigger_sf)
    events["TriggerSFweight_2l"] = trigger_sf
    return events, variations
