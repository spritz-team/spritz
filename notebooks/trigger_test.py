import awkward as ak
import correctionlib
import numpy as np
import vector
from data.common.TrigMaker_cfg import Trigger
from spritz.framework.framework import get_fw_path

vector.register_awkward()

year = "Full2017v9"

rng = np.random.Generator(np.random.PCG64(31))

nevents = 1_000_000

maxeta_ele = 2.4999
maxeta_mu = 2.3999

nmu = rng.integers(0, 6, nevents)
nmu_tot = np.sum(nmu)
mu_pt = rng.normal(30, 2, nmu_tot)
mu_pt = ak.unflatten(mu_pt, nmu)
mu_eta = rng.normal(0, 1, nmu_tot)
mu_eta = np.where(abs(mu_eta) <= maxeta_mu, mu_eta, maxeta_mu)
mu_eta = ak.unflatten(mu_eta, nmu)
mu_phi = rng.uniform(0, np.pi, nmu_tot)
mu_phi = ak.unflatten(mu_phi, nmu)

nele = rng.integers(0, 5, nevents)
nele_tot = np.sum(nele)
ele_pt = rng.normal(30, 2, nele_tot)
ele_pt = ak.unflatten(ele_pt, nele)
ele_eta = rng.normal(0, 1, nele_tot)
ele_eta = np.where(abs(ele_eta) <= maxeta_ele, ele_eta, maxeta_ele)
ele_eta = ak.unflatten(ele_eta, nele)
ele_phi = rng.uniform(0, np.pi, nele_tot)
ele_phi = ak.unflatten(ele_phi, nele)

mu_none = ak.mask(mu_pt, ak.is_none(mu_pt, axis=1))
ele_none = ak.mask(ele_pt, ak.is_none(ele_pt, axis=1))

lep_pdgId = ak.concatenate(
    [11 * ak.ones_like(ele_pt), 13 * ak.ones_like(mu_pt)], axis=1
)
lep_pt = ak.concatenate([ele_pt, mu_pt], axis=1)
lep_eta = ak.concatenate([ele_eta, mu_eta], axis=1)
lep_phi = ak.concatenate([ele_phi, mu_phi], axis=1)

lepton = ak.zip(
    {
        "pt": lep_pt,
        "eta": lep_eta,
        "phi": lep_phi,
        "mass": ak.zeros_like(lep_pt),
        "pdgId": lep_pdgId,
    },
    with_name="Momentum4D",
)

lepton = lepton[ak.argsort(lepton.pt, ascending=False, axis=-1)]
print(lepton)

run_period = rng.integers(1, 6, nevents)

pvs = rng.normal(50, 10, nevents)
pvs = ak.Array(pvs)
pvs = ak.values_astype(pvs, int)
PV = ak.zip({"npvsGood": pvs})

events = ak.zip(
    {
        "Lepton": lepton,
        "run_period": run_period,
        "PV": PV,
    },
    depth_limit=1,
)


def max_vec(vec, val):
    return ak.where(vec > val, vec, val)


cset_trigger = correctionlib.CorrectionSet.from_file(
    f"{get_fw_path()}/data/{year}/clib/trigger_sf.json.gz"
)

# era = 1
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
        dz_type, dz_value = list(Trigger[year][era]["DZEffData"][combo_name].items())[0]
        pvs = ak.where(trigger_events.PV.npvsGood > 69, 69, trigger_events.PV.npvsGood)
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
        dz_type, dz_value = list(Trigger[year][era]["DZEffMC"][combo_name].items())[0]
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
            eff_gl[i] = ak.where(mask, Trigger[year][era]["GlEff"][name][0], eff_gl[i])

        # Leg Efficiencies
        for i, (leg, idx) in enumerate(zip(legs, idxs)):
            pt = ak.copy(leptons[:, idx].pt)
            pt = ak.where(pt >= 200, 199.99, pt)
            eta = ak.copy(leptons[:, idx].eta)

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
        (effData[4] * effData[3] + effData[2] * effData[5] - effData[3] * effData[2])
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
print(trigger_sf)

# Checks on run period generation
# trig = Trigger[year]
# eras = np.array([era for era in trig])
# lumis = np.array([trig[era]["lumi"] for era in trig])
# print(eras)
# print(lumis)
# cdf = np.cumsum(lumis)
# cdf = cdf / cdf[-1]
# values = rng.random(size=1_000_000)
# value_bins = np.searchsorted(cdf, values)
# run_period = eras[value_bins]
# print(run_period)
# print(np.histogram(run_period, bins=np.linspace(0.5, 5.5, 6)))
# contents, _ = np.histogram(run_period, bins=np.linspace(0.5, 5.5, 6))
# lumi = 41479.680528 / 1000
# print(contents / np.sum(contents) * lumi)
# print(np.sum(contents))
