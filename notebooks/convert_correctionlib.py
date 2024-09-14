#!/usr/bin/env python
# coding: utf-8

import gzip
import json

import correctionlib
import correctionlib.convert
import hist
import numpy as np
import pandas as pd
import requests
import rich
import uproot
from data.common.LeptonSel_cfg import ElectronWP, MuonWP

path_jsonpog = "/Users/giorgiopizzati/Downloads/jsonpog-integration-master/POG"
path_jsonpog = "/cvmfs/cms.cern.ch/rsync/cms-nanoAOD/jsonpog-integration/POG"
url_latinos = "https://raw.githubusercontent.com/latinos/LatinoAnalysis/UL_production/NanoGardener/python/data/scale_factor/"
for ERA, year in [
    ("Full2018v9", "2018"),
    ("Full2017v9", "2017"),
    ("Full2016v9HIPM", "2016preVFP"),
    ("Full2016v9noHIPM", "2016postVFP"),
]:
    fname = (
        path_jsonpog
        + list(ElectronWP[ERA]["TightObjWP"]["mvaFall17V2Iso_WP90"]["tkSF"].values())[
            0
        ].split("POG")[-1]
    )
    print(fname)

    ceval = correctionlib.CorrectionSet.from_file(fname)

    # ## Explore correctionlib json file

    with gzip.open(fname) as file:
        corr = json.load(file)

    def find_key(key: str, l: list):
        for i in range(len(l)):
            if l[i]["key"] == key:
                return i

    def print_keys(l: list):
        for i in range(len(l)):
            print(l[i]["key"])

    corr["corrections"][0]["data"]["content"][0]["value"]["input"]

    real_content = corr["corrections"][0]["data"]["content"][0]["value"]["content"]

    print_keys(real_content)

    find_key("sf", real_content)

    sf = real_content[0]["value"]
    sf["input"], sf.keys()

    print_keys(sf["content"])

    find_key("RecoBelow20", sf["content"])

    def get_cset_electron(era, wp, return_histo=False):
        real_content = corr["corrections"][0]["data"]["content"][0]["value"]["content"]
        content_syst = []
        for valType in ["sf", "sfdown", "sfup"]:
            sf_ind = find_key(valType, real_content)
            sf = real_content[sf_ind]["value"]["content"]

            wp_ind = find_key(wp, sf)
            obj = sf[wp_ind]["value"]
            content = np.array(obj["content"])
            content_syst.append(content)
            axis = [
                hist.axis.Variable(edges, name=name)
                for edges, name in zip(obj["edges"], obj["inputs"])
            ]
        content_syst = np.array(content_syst)
        shape = [ax.edges.shape[0] - 1 for ax in axis]
        content_syst = content_syst.reshape(3, *shape)
        syst = ["nominal", "syst_down", "syst_up"]
        # syst = ['sf', 'sfdown', 'sfup']
        h = hist.Hist(
            hist.axis.StrCategory(syst, name="syst"),
            *axis,
            hist.storage.Double(),
            data=content_syst,
        )
        h.name = "Electron_RecoSF_" + wp
        h.label = "out"
        cset = correctionlib.convert.from_histogram(h)

        if return_histo:
            return h, cset
        return cset

    def rand_in_axis(axis):
        min = axis[0] if axis[0] > -np.inf else axis[1] - (axis[2] - axis[1]) / 2
        max = axis[-1] if axis[-1] < np.inf else axis[-2] + (axis[-2] - axis[-3]) / 2
        return np.random.uniform(min, max)

    def rand_in_histos(h, nrands=10):
        result = []
        for i in range(nrands):
            r = []
            for j in range(len(h.axes)):
                r.append(rand_in_axis(h.axes[j].edges))
            result.append(r)
        return result

    def different_val(a, b):
        precision = 1e-10
        if a == b:
            return False
        if abs(a) < precision and abs(b) < precision:
            return False
        d = abs(a - b)
        if d < precision:
            return False
        return True

    for wp in ["RecoBelow20", "RecoAbove20"]:
        valTypes = ["sf", "sfdown", "sfup"]
        systs = ["nominal", "syst_down", "syst_up"]
        h, cset = get_cset_electron(year, wp, return_histo=True)
        ceval_new = cset.to_evaluator()
        l = [h.axes[i].centers for i in range(1, len(h.axes))]
        rand_inputs = np.transpose(
            [np.tile(l[0], len(l[1])), np.repeat(l[1], len(l[0]))]
        )
        rand_inputs[rand_inputs == np.inf] = 100
        rand_inputs[rand_inputs == -np.inf] = -100
        # rand_inputs = rand_in_histos(h, nrands=100)
        for syst, valType in zip(systs, valTypes):
            for eta, pt in rand_inputs:
                # new_val = h[hist.loc(syst), hist.loc(eta), hist.loc(pt)]
                new_val = ceval_new.evaluate(syst, eta, pt)
                old_val = ceval["UL-Electron-ID-SF"].evaluate(
                    year, valType, wp, eta, pt
                )
                if different_val(new_val, old_val):
                    raise Exception(
                        "Different values for eta", eta, "pt", pt, old_val, new_val
                    )
        print("Everything ok for", wp)

    csets = []
    for wp in ["RecoBelow20", "RecoAbove20"]:
        csets.append(get_cset_electron(year, wp))
        rich.print(csets[-1])

    def get_cset_electron_wp():
        dfs = {}

        d = ElectronWP[ERA]["TightObjWP"]["mvaFall17V2Iso_WP90"]["wpSF"]
        all_eras = list(d.keys())
        all_files = list(d.values())
        all_files = list(map(lambda k: k.split("scale_factor")[-1], all_files))

        for eras, fname in zip(all_eras, all_files):
            with open("test_sf.txt", "w") as file:
                url = f"https://raw.githubusercontent.com/latinos/LatinoAnalysis/UL_production/NanoGardener/python/data/scale_factor/{fname}"
                print(
                    "downloading",
                    url,
                )
                r = requests.get(url)
                file.write(r.text)

            columns = "effData statErrData systErrData effMC statErrMC systErrMC effDataAltBkg effDataAltSig effMCAltMC effMCTagSel"
            columns = columns.split(" ")
            df = pd.read_csv(
                "test_sf.txt",
                sep="\t",
                skiprows=3,
                header=None,
                names=["eta_l", "eta_h", "pt_l", "pt_h"] + columns,
            )
            df
            for var in ["eta", "pt"]:
                df[var] = list(zip(df[var + "_l"], df[var + "_h"]))
                del df[var + "_l"]
                del df[var + "_h"]

            df["sf"] = df["effData"] / df["effMC"]
            df["sf_err"] = (
                np.sqrt(
                    (df["statErrData"] / df["effData"]) ** 2
                    + (df["statErrMC"] / df["effMC"]) ** 2
                )
                * df["sf"]
            )
            df["sf_syst"] = (
                np.sqrt(
                    (df["systErrData"] / df["effData"]) ** 2
                    + (df["systErrMC"] / df["effMC"]) ** 2
                )
                * df["sf"]
            )
            dfs[eras] = df

        eras_bin = list(map(lambda k: int(k.split("-")[0]), all_eras))
        eras_bin.append(int(all_eras[-1].split("-")[-1]) + 0.01)
        eras_bin = np.array(eras_bin)
        print(eras_bin)

        eta_bin = np.array(
            list(map(lambda k: k[0], np.unique(df["eta"])))
            + [np.unique(df["eta"])[-1][-1]]
        )
        pt_bin = np.array(
            list(map(lambda k: k[0], np.unique(df["pt"])))
            + [np.unique(df["pt"])[-1][-1]]
        )
        h = hist.Hist(
            hist.axis.Variable(eras_bin, name="eras", flow=False),
            hist.axis.StrCategory(["nominal", "stat", "syst"], name="syst"),
            hist.axis.Variable(eta_bin, name="eta"),
            hist.axis.Variable(pt_bin, name="pt"),
            hist.storage.Double(),
        )
        for eras in all_eras:
            _eras = (int(eras.split("-")[0]) + int(eras.split("-")[1])) / 2
            print(
                eras,
                _eras,
            )
            for syst, sf_name in zip(
                ["nominal", "stat", "syst"], ["sf", "sf_err", "sf_syst"]
            ):
                for pt_c in (pt_bin[1:] + pt_bin[:-1]) / 2:
                    for eta_c in (eta_bin[1:] + eta_bin[:-1]) / 2:
                        for i, (ipt, ieta) in enumerate(
                            list(zip(list(df["pt"]), list(df["eta"])))
                        ):
                            if ieta[0] <= eta_c < ieta[1] and ipt[0] <= pt_c < ipt[1]:
                                h[
                                    hist.loc(_eras),
                                    hist.loc(syst),
                                    hist.loc(eta_c),
                                    hist.loc(pt_c),
                                ] = dfs[eras][sf_name][i]
            print(
                "hist loc",
                h[
                    hist.loc(_eras),
                    :,
                    :,
                    :,
                ],
            )

        h.name = "Electron_WP_SF"
        h.label = "out"
        return correctionlib.convert.from_histogram(h)

    csets.append(get_cset_electron_wp())
    rich.print(csets[-1])

    # Muons SF

    corrections = {
        "Muon_IdSF": "NUM_TightHWW_DEN_TrackerMuons_eta_pt",
        "Muon_IsoSF": "NUM_TightHWW_ISO_DEN_TightHWW_eta_pt",
    }

    def get_muon_cset(corrName, histoName):
        url = f"https://github.com/latinos/LatinoAnalysis/raw/UL_production/NanoGardener/python/data/scale_factor/{ERA}/{histoName}.root"
        with open("test_sf.root", "wb") as file:
            file.write(requests.get(url).content)
        f = uproot.open("test_sf.root")
        h = f[histoName].to_hist()
        axis = [
            hist.axis.Variable(axis.edges, name=name)
            for axis, name in zip(h.axes, ["eta", "pt"])
        ]
        data = np.array([h.values(), np.sqrt(h.variances())])
        h_sf = hist.Hist(
            hist.axis.StrCategory(["nominal", "syst"], name="syst"), *axis, data=data
        )
        h_sf.name = corrName
        h_sf.label = "out"
        cset = correctionlib.convert.from_histogram(h_sf)
        return cset

    for corrName, histoName in corrections.items():
        csets.append(get_muon_cset(corrName, histoName))
        rich.print(csets[-1])

    # Save everything

    cset = correctionlib.schemav2.CorrectionSet(
        schema_version=2, description="", corrections=csets
    )

    rich.print(cset)

    import os

    # os.makedirs(f"../data/{ERA}/clib", exist_ok=True)
    # with gzip.open(f"../data/{ERA}/clib/lepton_sf.json.gz", "wt") as fout:
    #     fout.write(cset.json(exclude_unset=True))
