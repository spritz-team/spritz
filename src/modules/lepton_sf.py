from coffea.lookup_tools.correctionlib_wrapper import correctionlib_wrapper
import awkward as ak
import numpy as np
import variation as variation_module


def lepton_sf(events, variations, ceval_lepton_sf, cfg):
    minpt_mu = 10.0001
    maxpt_mu = 199.9999
    mineta_mu = -2.3999
    maxeta_mu = 2.3999

    minpt_ele = 10.0001
    maxpt_ele = 199.9999
    mineta_ele = -2.4999
    maxeta_ele = 2.4999
    ele_mask = abs(events.Lepton.pdgId) == 11
    mu_mask = abs(events.Lepton.pdgId) == 13

    pt = ak.copy(events.Lepton.pt)
    eta = ak.copy(events.Lepton.eta)

    pt = ak.where(ele_mask & (pt < minpt_ele), minpt_ele, pt)
    pt = ak.where(ele_mask & (pt > maxpt_ele), maxpt_ele, pt)
    pt = ak.where(mu_mask & (pt < minpt_mu), minpt_mu, pt)
    pt = ak.where(mu_mask & (pt > maxpt_mu), maxpt_mu, pt)

    eta = ak.where(ele_mask & (eta < mineta_ele), mineta_ele, eta)
    eta = ak.where(ele_mask & (eta > maxeta_ele), maxeta_ele, eta)
    eta = ak.where(mu_mask & (eta < mineta_mu), mineta_mu, eta)
    eta = ak.where(mu_mask & (eta > maxeta_mu), maxeta_mu, eta)

    sfs_dict = {}
    sfs_dict["ele_reco_below"] = {
        "wrap": correctionlib_wrapper(ceval_lepton_sf["Electron_RecoSF_RecoBelow20"]),
        "mask": ele_mask & (pt >= 10.0) & (pt < 20.0),
        "output": "reco_sf",
    }

    sfs_dict["ele_reco_above"] = {
        "wrap": correctionlib_wrapper(ceval_lepton_sf["Electron_RecoSF_RecoAbove20"]),
        "mask": ele_mask & (pt >= 20.0),
        "output": "reco_sf",
    }

    sfs_dict["ele_wp"] = {
        "wrap": correctionlib_wrapper(ceval_lepton_sf["Electron_WP_SF"]),
        "mask": ele_mask & events.Lepton["isTightElectron_" + cfg["eleWP"]],
        "output": "ele_id_iso_sf",
    }

    sfs_dict["muon_id"] = {
        "wrap": correctionlib_wrapper(ceval_lepton_sf["Muon_IdSF"]),
        "mask": mu_mask & events.Lepton["isTightMuon_" + cfg["muWP"]],
        "output": "muon_id_sf",
    }

    sfs_dict["muon_iso"] = {
        "wrap": correctionlib_wrapper(ceval_lepton_sf["Muon_IsoSF"]),
        "mask": mu_mask & events.Lepton["isTightMuon_" + cfg["muWP"]],
        "output": "muon_iso_sf",
    }

    # Lepton Reco SF (only electrons)
    lepton_reco_vars = ["nominal", "syst_down", "syst_up"]
    lepton_reco_sf = {k: ak.ones_like(pt) for k in lepton_reco_vars}

    # Pay attention, ele_reco SF variations do not give the error but they are directly the shifts
    for reco_sf in ["ele_reco_below", "ele_reco_above"]:
        for variation in lepton_reco_vars:
            mask = sfs_dict[reco_sf]["mask"]
            _eta = ak.mask(eta, mask)
            _pt = ak.mask(pt, mask)
            lepton_reco_sf[variation] = ak.where(
                mask,
                sfs_dict[reco_sf]["wrap"](variation, _eta, _pt),
                lepton_reco_sf[variation],
            )

    for variation in lepton_reco_vars:
        lepton_reco_sf[variation] = ak.fill_none(lepton_reco_sf[variation], 1.0)

    events[("Lepton", "RecoSF")] = lepton_reco_sf["nominal"]

    for t, mask in zip(["ele"], [ele_mask]):
        for _, tag in zip([+1, -1], ["up", "down"]):
            var_name = f"{t}_reco_{tag}"
            varied_col = variation_module.Variation.format_varied_column(
                ("Lepton", "RecoSF"), var_name
            )
            #res = lepton_reco_sf["nominal"] + sign * lepton_reco_sf[f"syst_{tag}"]
            res = lepton_reco_sf[f"syst_{tag}"]
            events[varied_col] = ak.where(mask, res, lepton_reco_sf["nominal"])
            variations.register_variation([("Lepton", "RecoSF")], var_name)

    # Lepton IdIso SF
    lepton_idiso_vars = ["nominal", "stat", "syst"]
    lepton_idiso_sf = {
        k: (ak.ones_like(pt) if k == "nominal" else ak.zeros_like(pt))
        for k in lepton_idiso_vars
    }

    for idiso_sf in ["ele_wp"]:
        for variation in lepton_idiso_vars:
            mask = sfs_dict[idiso_sf]["mask"]
            _eta = ak.mask(eta, mask)
            _pt = ak.mask(pt, mask)
            lepton_idiso_sf[variation] = ak.where(
                mask,
                sfs_dict[idiso_sf]["wrap"](variation, _eta, _pt),
                lepton_idiso_sf[variation],
            )

    muon_idiso_vars = ["nominal", "syst"]
    muon_idiso_sf = {
        idiso_sf: {
            k: (ak.ones_like(pt) if k == "nominal" else ak.zeros_like(pt))
            for k in muon_idiso_vars
        }
        for idiso_sf in ["muon_id", "muon_iso"]
    }

    for idiso_sf in ["muon_id", "muon_iso"]:
        for variation in muon_idiso_vars:
            mask = sfs_dict[idiso_sf]["mask"]
            _eta = ak.mask(eta, mask)
            _pt = ak.mask(pt, mask)
            muon_idiso_sf[idiso_sf][variation] = ak.where(
                mask,
                sfs_dict[idiso_sf]["wrap"](variation, _eta, _pt),
                muon_idiso_sf[idiso_sf][variation],
            )

    muon_sf = muon_idiso_sf["muon_id"]["nominal"] * muon_idiso_sf["muon_iso"]["nominal"]
    muon_syst = np.sqrt(
        muon_idiso_sf["muon_id"]["syst"] ** 2 / muon_idiso_sf["muon_id"]["nominal"] ** 2
        + muon_idiso_sf["muon_iso"]["syst"] ** 2
        / muon_idiso_sf["muon_iso"]["nominal"] ** 2
    )

    lepton_idiso_sf["nominal"] = ak.where(mu_mask, muon_sf, lepton_idiso_sf["nominal"])
    lepton_idiso_sf["syst"] = ak.where(mu_mask, muon_syst, lepton_idiso_sf["syst"])

    for variation in lepton_idiso_vars:
        if variation == "nominal":
            lepton_idiso_sf[variation] = ak.fill_none(lepton_idiso_sf[variation], 1.0)
        else:
            lepton_idiso_sf[variation] = ak.fill_none(lepton_idiso_sf[variation], 0.0)

    lepton_idiso_sf["err"] = np.sqrt(
        lepton_idiso_sf["syst"] ** 2 / lepton_idiso_sf["nominal"] ** 2
        + lepton_idiso_sf["stat"] ** 2 / lepton_idiso_sf["nominal"] ** 2
    )

    events[("Lepton", "TightSF")] = lepton_idiso_sf["nominal"]

    for t, mask in zip(["ele", "mu"], [ele_mask, mu_mask]):
        for sign, tag in zip([+1, -1], ["up", "down"]):
            var_name = f"{t}_idiso_{tag}"
            varied_col = variation_module.Variation.format_varied_column(
                ("Lepton", "TightSF"), var_name
            )
            res = lepton_idiso_sf["nominal"] + sign * lepton_idiso_sf["err"]
            events[varied_col] = ak.where(mask, res, lepton_idiso_sf["nominal"])
            variations.register_variation([("Lepton", "TightSF")], var_name)

    return events, variations
