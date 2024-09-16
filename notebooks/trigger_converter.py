import gzip
import os
import sys

import correctionlib
import correctionlib.convert
import hist
import numpy as np
import pandas as pd
import requests
import rich
from spritz.framework.framework import get_fw_path

sys.path.insert(0, f"{get_fw_path()}/data")
from data.common.TrigMaker_cfg import Trigger

base_url = "https://raw.githubusercontent.com/latinos/LatinoAnalysis/UL_production/NanoGardener/python/data/trigger/"


def get_cset(name, url):
    with open("test_sf.txt", "wb") as file:
        file.write(requests.get(base_url + url).content)
    columns = "eff stat_d stat_u syst_d syst_u"
    columns = columns.split(" ")
    df = pd.read_csv(
        "test_sf.txt",
        sep="\t",
        skiprows=0,
        header=None,
        names=["eta_l", "eta_h", "pt_l", "pt_h"] + columns,
    )
    for var in ["eta", "pt"]:
        df[var] = list(zip(df[var + "_l"], df[var + "_h"]))
        del df[var + "_l"]
        del df[var + "_h"]
    eta_bin = np.array(
        list(map(lambda k: k[0], np.unique(df["eta"]))) + [np.unique(df["eta"])[-1][-1]]
    )
    pt_bin = np.array(
        list(map(lambda k: k[0], np.unique(df["pt"]))) + [np.unique(df["pt"])[-1][-1]]
    )
    h = hist.Hist(
        hist.axis.StrCategory(columns, name="syst"),
        hist.axis.Variable(eta_bin, name="eta"),
        hist.axis.Variable(pt_bin, name="pt"),
        hist.storage.Double(),
    )
    for syst in columns:
        for pt_c in (pt_bin[1:] + pt_bin[:-1]) / 2:
            for eta_c in (eta_bin[1:] + eta_bin[:-1]) / 2:
                for i, (ipt, ieta) in enumerate(
                    list(zip(list(df["pt"]), list(df["eta"])))
                ):
                    if ieta[0] <= eta_c < ieta[1] and ipt[0] <= pt_c < ipt[1]:
                        h[hist.loc(syst), hist.loc(eta_c), hist.loc(pt_c)] = df[syst][i]
    h.name = name
    h.label = "out"
    cset = correctionlib.convert.from_histogram(h)
    return cset


def get_cset_drll(name, url):
    with open("test_sf.txt", "wb") as file:
        file.write(requests.get(base_url + url).content)
    with open("test_sf.txt") as file:
        lines = file.read().split("\n")
    lines = list(map(lambda k: k.strip(), lines))
    with open("test_sf.txt", "w") as file:
        file.write("\n".join(lines))

    columns = "sf"
    columns = columns.split(" ")
    df = pd.read_csv(
        "test_sf.txt",
        sep=" ",
        index_col=False,
        skiprows=0,
        header=None,
        names=["drll_l", "drll_h"] + columns,
    )
    for var in ["drll"]:
        df[var] = list(zip(df[var + "_l"], df[var + "_h"]))
        del df[var + "_l"]
        del df[var + "_h"]
    drll_bin = np.array(
        list(map(lambda k: k[0], np.unique(df["drll"])))
        + [np.unique(df["drll"])[-1][-1]]
    )

    h = hist.Hist(
        hist.axis.Variable(drll_bin, name="drll"),
        hist.storage.Double(),
    )

    for drll_c in (drll_bin[1:] + drll_bin[:-1]) / 2:
        for i, (idrll) in enumerate(list(df["drll"])):
            if idrll[0] <= drll_c < idrll[1]:
                h[hist.loc(drll_c)] = df["sf"][i]
    h.name = name
    h.label = "out"
    cset = correctionlib.convert.from_histogram(h)
    return cset


def get_cset_dz(name, d):
    type_eff, url = tuple(d.items())[0]

    if type_eff == "value":
        return
    elif type_eff == "nvtx":
        with open("test_sf.txt", "wb") as file:
            file.write(requests.get(base_url + url).content)
        columns = "eff err err2"
        columns = columns.split(" ")
        df = pd.read_csv(
            "test_sf.txt",
            sep=" ",
            skiprows=0,
            header=None,
            names=["nvtx_l", "nvtx_h"] + columns,
        )
        columns = columns[:-1]
        for var in ["nvtx"]:
            df[var] = list(zip(df[var + "_l"], df[var + "_h"]))
            del df[var + "_l"]
            del df[var + "_h"]
        nvtx_bin = np.array(
            list(map(lambda k: k[0], np.unique(df["nvtx"])))
            + [np.unique(df["nvtx"])[-1][-1]]
        )
        h = hist.Hist(
            hist.axis.StrCategory(columns, name="syst"),
            hist.axis.Variable(nvtx_bin, name="nvtx"),
            hist.storage.Double(),
        )
        for syst in columns:
            for nvtx_c in (nvtx_bin[1:] + nvtx_bin[:-1]) / 2:
                for i, (invtx) in enumerate(list(list(df["nvtx"]))):
                    if invtx[0] <= nvtx_c < invtx[1]:
                        h[hist.loc(syst), hist.loc(nvtx_c)] = df[syst][i]

    elif type_eff == "pt1:pt2":
        with open("test_sf.txt", "wb") as file:
            file.write(requests.get(base_url + url).content)
        columns = "eff err err2"
        columns = columns.split(" ")
        df = pd.read_csv(
            "test_sf.txt",
            sep=" ",
            skiprows=0,
            header=None,
            names=["pt1_l", "pt1_h", "pt2_l", "pt2_h"] + columns,
        )
        columns = columns[:-1]
        for var in ["pt1", "pt2"]:
            df[var] = list(zip(df[var + "_l"], df[var + "_h"]))
            del df[var + "_l"]
            del df[var + "_h"]
        pt1_bin = np.array(
            list(map(lambda k: k[0], np.unique(df["pt1"])))
            + [np.unique(df["pt1"])[-1][-1]]
        )
        pt2_bin = np.array(
            list(map(lambda k: k[0], np.unique(df["pt2"])))
            + [np.unique(df["pt2"])[-1][-1]]
        )
        h = hist.Hist(
            hist.axis.StrCategory(columns, name="syst"),
            hist.axis.Variable(pt1_bin, name="pt1"),
            hist.axis.Variable(pt2_bin, name="pt2"),
            hist.storage.Double(),
        )
        for syst in columns:
            for pt1_c in (pt1_bin[1:] + pt1_bin[:-1]) / 2:
                for pt2_c in (pt2_bin[1:] + pt2_bin[:-1]) / 2:
                    for i, (ipt1, ipt2) in enumerate(
                        list(zip(list(df["pt1"]), list(df["pt2"])))
                    ):
                        if ipt1[0] <= pt1_c < ipt1[1] and ipt2[0] <= pt2_c < ipt2[1]:
                            h[hist.loc(syst), hist.loc(pt1_c), hist.loc(pt2_c)] = df[
                                syst
                            ][i]
    h.name = name
    h.label = "out"
    cset = correctionlib.convert.from_histogram(h)

    return cset


for year in Trigger:
    csets = []
    for era in Trigger[year]:
        for is_data in ["MC", "Data"]:
            for trigger, d in Trigger[year][era][f"DZEff{is_data}"].items():
                cset = get_cset_dz(f"{era}_DZEff_{is_data}_{trigger}", d)
                if cset:
                    csets.append(cset)
            for trigger, d in Trigger[year][era][f"LegEff{is_data}"].items():
                cset = get_cset(f"{era}_LegEff_{is_data}_{trigger}", d)
                csets.append(cset)

    # DRll SF is not era dependent!
    for trigger, d in Trigger[year][era]["DRllSF"].items():
        cset = get_cset_drll(f"DRllSF_{trigger}", d)
        csets.append(cset)

    cset = correctionlib.schemav2.CorrectionSet(
        schema_version=2, description="", corrections=csets
    )
    rich.print(cset)

    os.makedirs(f"../data/{year}/clib", exist_ok=True)
    with gzip.open(f"../data/{year}/clib/trigger_sf.json.gz", "wt") as fout:
        fout.write(cset.json(exclude_unset=True))
