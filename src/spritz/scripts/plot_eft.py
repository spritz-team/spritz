import concurrent.futures
import json
import os
import subprocess
import sys
from copy import deepcopy

import matplotlib as mpl
import mplhep as hep
import numpy as np
import uproot
from spritz.framework.framework import get_analysis_dict, get_fw_path

mpl.use("Agg")
from matplotlib import pyplot as plt

d = deepcopy(hep.style.CMS)

d["font.size"] = 12
d["figure.figsize"] = (5, 5)

plt.style.use(d)


def darker_color(color):
    rgb = list(mpl.colors.to_rgba(color)[:-1])
    darker_factor = 4 / 5
    rgb[0] = rgb[0] * darker_factor
    rgb[1] = rgb[1] * darker_factor
    rgb[2] = rgb[2] * darker_factor
    return tuple(rgb)


def plot_eft(
    input_file,
    region,
    variable,
    samples,
    nuisances,
    lumi,
    colors,
    year_label,
    blind,
    variable_label=None,
):
    print("Doing ", region, variable)

    histos = {}
    directory = input_file[f"{region}/{variable}"]
    dummy_histo = 0
    axis = 0
    hmin = 1e7
    for sample in samples:
        h = directory[f"histo_{sample}"].to_hist()
        if isinstance(axis, int):
            axis = h.axes[0]
        if isinstance(dummy_histo, int):
            dummy_histo = np.zeros_like(h.values())
        histos[sample] = {}
        histo = histos[sample]
        histo["nom"] = h.values()
        hmin = min(hmin, np.min(histo["nom"]))
        stat = np.sqrt(h.variances())
        histo["stat_up"] = h.values() + stat
        histo["stat_down"] = h.values() - stat
        for nuisance in nuisances:
            if nuisances[nuisance]["type"] == "rateParam":
                continue
            if nuisances[nuisance]["type"] == "auto":
                continue
            if nuisances[nuisance]["type"] == "stat":
                continue
            name = nuisances[nuisance]["name"]

            if sample not in nuisances[nuisance]["samples"]:
                histo[f"{nuisance}_up"] = h.values().copy()
                histo[f"{nuisance}_down"] = h.values().copy()
                continue

            if nuisances[nuisance]["type"] == "lnN":
                scaling = float(nuisances[nuisance]["samples"][sample])
                histo[f"{nuisance}_up"] = scaling * h.values()
                histo[f"{nuisance}_down"] = 1.0 / scaling * h.values()
            else:
                histo[f"{nuisance}_up"] = (
                    directory[f"histo_{sample}_{name}Up"].values().copy()
                )
                histo[f"{nuisance}_down"] = (
                    directory[f"histo_{sample}_{name}Down"].values().copy()
                )
    hlast = dummy_histo.copy()
    hlast_bkg = dummy_histo.copy()
    v_syst_bkg = {
        syst: {
            "up": dummy_histo.copy(),
            "down": dummy_histo.copy(),
        }
        for syst in nuisances
    }

    for histoName in histos:
        is_signal = samples[histoName].get("is_signal", False)
        # if samples[histoName].get("is_data", False):
        #     continue
        if is_signal:
            hlast += histos[histoName]["nom"].copy()
        else:
            hlast += histos[histoName]["nom"].copy()
            hlast_bkg += histos[histoName]["nom"].copy()

        for vname in nuisances:
            if sample not in nuisances[vname]["samples"]:
                v_syst_bkg[vname]["up"] += histos[histoName]["nom"].copy()
                v_syst_bkg[vname]["down"] += histos[histoName]["nom"].copy()
            else:
                v_syst_bkg[vname]["up"] += histos[histoName][vname + "_up"].copy()
                v_syst_bkg[vname]["down"] += histos[histoName][vname + "_down"].copy()

    vvar_up = dummy_histo.copy()
    vvar_do = dummy_histo.copy()
    for syst in v_syst_bkg:
        vvar_up += np.square(v_syst_bkg[syst]["up"].copy() - hlast)
        vvar_do += np.square(v_syst_bkg[syst]["down"].copy() - hlast)
    vvar_up = np.sqrt(vvar_up)
    vvar_do = np.sqrt(vvar_do)
    hlast = np.where(hlast >= 1e-6, hlast, 1e-6)
    hlast_bkg = np.where(hlast_bkg >= 1e-6, hlast_bkg, 1e-6)

    # mc_err_up = 0
    # mc_err_up = np.sqrt(mc_err_up)
    # mc_err_down = np.sqrt(mc_err_down)
    # syst_up = np.sqrt(syst_up)
    # syst_down = np.sqrt(syst_down)
    # stat_up = np.sqrt(syst_up)
    # stat_down = np.sqrt(syst_down)
    # mc = np.where(mc >= 1e-5, mc, 1e-5)
    # print('time after sum mc', time.time()-start)
    # start = time.time()

    ###

    signal_tot = hlast - hlast_bkg
    # significance = signal_tot / np.sqrt(hlast_bkg)
    significance = signal_tot / hlast_bkg
    # print(region, variable, significance)
    blind_mask = significance > 0.10

    x = axis.centers
    edges = axis.edges

    tmp_sum = dummy_histo.copy()
    fig, ax = plt.subplots(
        2, 1, sharex=True, gridspec_kw={"height_ratios": [3, 1]}, dpi=200
    )  # figsize=(5,5), dpi=200)
    fig.tight_layout(pad=-0.5)
    hep.cms.label(
        region, data=True, lumi=round(lumi, 2), ax=ax[0], year=year_label
    )  # ,fontsize=16)
    # for i, histoName in enumerate(["Top", "DY", "Zjj", "Data"]):
    for i, histoName in enumerate(histos.keys()):
        is_signal = samples[histoName].get("is_signal", False)
        y = histos[histoName]["nom"].copy()
        integral = round(np.sum(y), 2)
        label = histoName + f" [{integral}]"
        # if histoName == "Data":
        # if samples[histoName].get("is_data", False):
        #     yup = histos[histoName]["stat_up"] - y
        #     ydown = y - histos[histoName]["stat_down"]
        #     # if "sr" in region:
        #     if blind:
        #         y_blind = np.zeros_like(y)
        #         yup_blind = np.zeros_like(y)
        #         ydown_blind = np.zeros_like(y)
        #         y = np.where(blind_mask, y_blind, y)
        #         yup = np.where(blind_mask, yup_blind, yup)
        #         ydown = np.where(blind_mask, ydown_blind, ydown)
        #     ax[0].errorbar(
        #         x,
        #         y,
        #         yerr=(ydown, yup),
        #         fmt="ko",
        #         markersize=4,
        #         label="Data" + f" [{integral}]",
        #         zorder=len(histos),
        #     )
        #       continue
        color = colors[histoName]
        if is_signal:
            ax[0].stairs(y, edges, zorder=i, linewidth=2, color=color, label=label)

        if isinstance(tmp_sum, int):
            tmp_sum = y.copy()
        else:
            tmp_sum += y
        # print(i, tmp_sum - hlast)

        if "sm" in histoName:
            ax[0].stairs(
                tmp_sum,
                edges,
                label=label,
                fill=True,
                zorder=-i,
                color=color,
                edgecolor=darker_color(color),
                linewidth=2.0,
            )
    # print('time loop stairs', time.time()-start)

    # unc = np.max([mc_err_up, mc_err_down], axis=0)
    # unc = round(np.sum(unc + mc), 2)
    unc_up = round(np.sum(vvar_up) / np.sum(hlast_bkg) * 100, 2)
    unc_down = round(np.sum(vvar_do) / np.sum(hlast_bkg) * 100, 2)
    # ax[0].stairs(mc+mc_err_up, edges, baseline=mc-mc_err_down, fill=True, alpha=0.2, label=f"Syst [$\pm${unc}%]")
    # ax[0].stairs(mc+mc_err_up, edges, baseline=mc-mc_err_down, fill=True, alpha=0.2, label=f"Syst [-{unc_down}, +{unc_up}]%")
    unc_dict = dict(
        fill=True, hatch="///", color="darkgrey", facecolor="none", zorder=9
    )
    # ax[0].stairs(
    #     # hlast_bkg + vvar_up,
    #     hlast_bkg + vvar_up,
    #     edges,
    #     # baseline=hlast_bkg - vvar_do,
    #     baseline=hlast - vvar_do,
    #     label=f"Syst [-{unc_down}, +{unc_up}]%",
    #     **unc_dict,
    # )
    # integral = round(np.sum(hlast), 2)
    # # print(tmp_sum - hlast)
    # ax[0].stairs(
    #     hlast, edges, label=f"Tot MC [{integral}]", color="darkgrey", linewidth=1
    # )
    ax[0].set_yscale("log")
    ax[0].legend(
        loc="upper center",
        # loc=(0.016, 0.75),
        frameon=True,
        ncols=3,
        framealpha=0.8,
        fontsize=8,
    )
    print(variable, np.max(hlast))
    ax[0].set_ylim(max(0.5, hmin), np.max(hlast) * 1e2)  # FIXME remove comment

    ratio_err_up = vvar_up / hlast
    ratio_err_down = vvar_do / hlast
    ax[1].stairs(
        1 + ratio_err_up,
        edges,
        baseline=1 - ratio_err_down,
        fill=True,
        color="lightgray",
    )

    # ratio_stat_up = stat_up / mc
    # ratio_stat_down = stat_down / mc
    # ax[1].stairs(
    #     1 + ratio_stat_up,
    #     edges,
    #     baseline=1 - ratio_stat_down,
    #     # fill=True,
    #     color="lightgreen",
    #     linestyle="dashed",
    #     linewidth=2,
    # )
    # ratio_err_up = syst_up / mc
    # ratio_err_down = syst_down / mc
    # ax[1].stairs(
    #     1 + ratio_err_up,
    #     edges,
    #     baseline=1 - ratio_err_down,
    #     # fill=True,
    #     color="red",
    #     linestyle="dashed",
    #     linewidth=2,
    # )
    ydata = hlast_bkg.copy()
    ydata_up = np.sqrt(hlast_bkg).copy()
    ydata_down = np.sqrt(hlast_bkg).copy()
    for histoName in histos:
        if samples[histoName].get("is_data", False):
            ydata = histos[histoName]["nom"]
            ydata_up = histos[histoName]["stat_up"] - ydata
            ydata_down = ydata - histos[histoName]["stat_down"]

    # Blind all signal region
    # if "sr" in region:
    if blind:
        ydata_blind = np.zeros_like(hlast_bkg)
        ydata_up_blind = np.zeros_like(hlast_bkg)
        ydata_down_blind = np.zeros_like(hlast_bkg)
        ydata = np.where(blind_mask, ydata_blind, ydata)
        ydata_up = np.where(blind_mask, ydata_up_blind, ydata_up)
        ydata_down = np.where(blind_mask, ydata_down_blind, ydata_down)

    ratio = ydata / hlast
    ratio_data_up = ydata_up / hlast
    ratio_data_down = ydata_down / hlast
    ax[1].errorbar(
        x,
        ratio,
        (ratio_data_down, ratio_data_up),
        fmt="ko",
        markersize=4,
    )
    ax[1].plot(edges, np.ones_like(edges), color="black", linestyle="dashed")
    delta = 0.3
    # delta = 1  # FIXME
    ax[1].set_ylim(1.0 - delta, 1.0 + delta)
    ax[1].set_xlim(np.min(edges), np.max(edges))
    ax[0].set_ylabel("Events")
    ax[1].set_ylabel("SM / SM+EFT")
    if variable_label:
        ax[1].set_xlabel(variable_label)
    else:
        ax[1].set_xlabel(variable)
    # print('time before fig save', time.time()-start)
    fig.savefig(
        f"plots/{region}_{variable}.png",
        facecolor="white",
        pad_inches=0.1,
        bbox_inches="tight",
    )
    plt.close()
    # print('time after fig save', time.time()-start)


def plot_validation(
    input_file,
    region,
    variable,
    samples,
    nuisances,
    lumi,
    colors,
    year_label,
    blind,
    variable_label=None,
):
    print("Doing ", region, variable)

    histos = {}
    directory = input_file[f"{region}/{variable}"]
    dummy_histo = 0
    axis = 0
    hmin = 1e7

    for nuisance in list(nuisances.keys()):
        if "stat" not in nuisance:
            del nuisances[nuisance]

    for sample in samples:
        h = directory[f"histo_{sample}"].to_hist()
        if isinstance(axis, int):
            axis = h.axes[0]
        if isinstance(dummy_histo, int):
            dummy_histo = np.zeros_like(h.values())
        histos[sample] = {}
        histo = histos[sample]
        histo["nom"] = h.values()
        hmin = min(hmin, np.min(histo["nom"]))
        stat = np.sqrt(h.variances())
        histo["stat_up"] = h.values() + stat
        histo["stat_down"] = h.values() - stat
        for nuisance in nuisances:
            if nuisances[nuisance]["type"] == "rateParam":
                continue
            if nuisances[nuisance]["type"] == "auto":
                continue
            if nuisances[nuisance]["type"] == "stat":
                continue
            name = nuisances[nuisance]["name"]

            if sample not in nuisances[nuisance]["samples"]:
                histo[f"{nuisance}_up"] = h.values().copy()
                histo[f"{nuisance}_down"] = h.values().copy()
                continue

            if nuisances[nuisance]["type"] == "lnN":
                scaling = float(nuisances[nuisance]["samples"][sample])
                histo[f"{nuisance}_up"] = scaling * h.values()
                histo[f"{nuisance}_down"] = 1.0 / scaling * h.values()
            else:
                histo[f"{nuisance}_up"] = (
                    directory[f"histo_{sample}_{name}Up"].values().copy()
                )
                histo[f"{nuisance}_down"] = (
                    directory[f"histo_{sample}_{name}Down"].values().copy()
                )
    hlast = dummy_histo.copy()
    hlast_bkg = dummy_histo.copy()
    v_syst_bkg = {
        syst: {
            "up": dummy_histo.copy(),
            "down": dummy_histo.copy(),
        }
        for syst in nuisances
    }

    for histoName in histos:
        if samples[histoName].get("is_data", False):
            continue
        is_signal = samples[histoName].get("is_signal", False)
        if is_signal:
            hlast += histos[histoName]["nom"].copy()
        else:
            hlast += histos[histoName]["nom"].copy()
            hlast_bkg += histos[histoName]["nom"].copy()

        for vname in nuisances:
            if sample not in nuisances[vname]["samples"]:
                v_syst_bkg[vname]["up"] += histos[histoName]["nom"].copy()
                v_syst_bkg[vname]["down"] += histos[histoName]["nom"].copy()
            else:
                v_syst_bkg[vname]["up"] += histos[histoName][vname + "_up"].copy()
                v_syst_bkg[vname]["down"] += histos[histoName][vname + "_down"].copy()

    vvar_up = dummy_histo.copy()
    vvar_do = dummy_histo.copy()
    for syst in v_syst_bkg:
        vvar_up += np.square(v_syst_bkg[syst]["up"].copy() - hlast)
        vvar_do += np.square(v_syst_bkg[syst]["down"].copy() - hlast)
    vvar_up = np.sqrt(vvar_up)
    vvar_do = np.sqrt(vvar_do)
    hlast = np.where(hlast >= 1e-6, hlast, 1e-6)
    hlast_bkg = np.where(hlast_bkg >= 1e-6, hlast_bkg, 1e-6)
    ###

    x = axis.centers
    edges = axis.edges

    tmp_sum = dummy_histo.copy()
    fig, ax = plt.subplots(
        2, 1, sharex=True, gridspec_kw={"height_ratios": [3, 1]}, dpi=200
    )  # figsize=(5,5), dpi=200)
    fig.tight_layout(pad=-0.5)
    hep.cms.label(
        region, data=True, lumi=round(lumi, 2), ax=ax[0], year=year_label
    )  # ,fontsize=16)
    # for i, histoName in enumerate(["Top", "DY", "Zjj", "Data"]):
    for i, histoName in enumerate(histos.keys()):
        is_signal = samples[histoName].get("is_signal", False)
        is_data = samples[histoName].get("is_data", False)
        y = histos[histoName]["nom"].copy()
        integral = round(np.sum(y), 2)
        label = histoName + f" [{integral}]"
        # if histoName == "Data":
        if is_data:
            yup = histos[histoName]["stat_up"] - y
            ydown = y - histos[histoName]["stat_down"]
            unc_up = round(np.sum(yup) / np.sum(y) * 100, 2)
            unc_down = round(np.sum(ydown) / np.sum(y) * 100, 2)
            ax[0].errorbar(
                x,
                y,
                yerr=(ydown, yup),
                fmt="ko",
                markersize=4,
                label="Data" + f" [{integral}] [-{unc_down}, +{unc_up}]%",
                zorder=len(histos),
            )
        elif is_signal:
            color = colors[histoName]
            if is_signal:
                ax[0].stairs(y, edges, zorder=i, linewidth=2, color=color)

            if isinstance(tmp_sum, int):
                tmp_sum = y.copy()
            else:
                tmp_sum += y
            # print(i, tmp_sum - hlast)
            ax[0].stairs(
                tmp_sum,
                edges,
                label=label,
                fill=True,
                zorder=-i,
                color=color,
                edgecolor=darker_color(color),
                linewidth=2.0,
            )
    # print('time loop stairs', time.time()-start)

    unc_up = round(np.sum(vvar_up) / np.sum(hlast) * 100, 2)
    unc_down = round(np.sum(vvar_do) / np.sum(hlast) * 100, 2)
    unc_dict = dict(
        fill=True, hatch="///", color="darkgrey", facecolor="none", zorder=9
    )
    ax[0].stairs(
        # hlast_bkg + vvar_up,
        hlast + vvar_up,
        edges,
        # baseline=hlast_bkg - vvar_do,
        baseline=hlast - vvar_do,
        label=f"Stat [-{unc_down}, +{unc_up}]%",
        **unc_dict,
    )

    ax[0].set_yscale("log")
    ax[0].legend(
        loc="upper center",
        # loc=(0.016, 0.75),
        frameon=True,
        ncols=3,
        framealpha=0.8,
        fontsize=8,
    )
    print(variable, np.max(hlast))
    ax[0].set_ylim(max(0.5, hmin) * 1e-2, np.max(hlast) * 1e2)  # FIXME remove comment

    ratio_err_up = vvar_up / hlast
    ratio_err_down = vvar_do / hlast
    ax[1].stairs(
        1 + ratio_err_up,
        edges,
        baseline=1 - ratio_err_down,
        fill=True,
        color="lightgray",
    )

    ydata = hlast_bkg.copy()
    ydata_up = np.sqrt(hlast_bkg).copy()
    ydata_down = np.sqrt(hlast_bkg).copy()
    for histoName in histos:
        if samples[histoName].get("is_data", False):
            ydata = histos[histoName]["nom"]
            ydata_up = histos[histoName]["stat_up"] - ydata
            ydata_down = ydata - histos[histoName]["stat_down"]

    ratio = ydata / hlast
    ratio_data_up = ydata_up / hlast
    ratio_data_down = ydata_down / hlast
    ax[1].errorbar(
        x,
        ratio,
        (ratio_data_down, ratio_data_up),
        fmt="ko",
        markersize=4,
    )
    ax[1].plot(edges, np.ones_like(edges), color="black", linestyle="dashed")
    delta = 0.3
    # delta = 1  # FIXME
    ax[1].set_ylim(1.0 - delta, 1.0 + delta)
    ax[1].set_xlim(np.min(edges), np.max(edges))
    ax[0].set_ylabel("Events")
    ax[1].set_ylabel("SM / SM+EFT")
    if variable_label:
        ax[1].set_xlabel(variable_label)
    else:
        ax[1].set_xlabel(variable)
    # print('time before fig save', time.time()-start)
    fig.savefig(
        f"plots/{region}_{variable}.png",
        facecolor="white",
        pad_inches=0.1,
        bbox_inches="tight",
    )
    plt.close()
    # print('time after fig save', time.time()-start)


def main():
    analysis_dict = get_analysis_dict()
    samples = analysis_dict["samples"]

    regions = analysis_dict["regions"]
    variables = analysis_dict["variables"]
    nuisances = analysis_dict["nuisances"]
    blind = analysis_dict.get("blind", False)

    colors = analysis_dict["colors"]
    # plots = analysis_dict["plots"]
    # scales = analysis_dict["scales"]
    plot_label = analysis_dict["plot_label"]
    year_label = analysis_dict.get("year_label", "Run-II")
    lumi = analysis_dict["lumi"]
    # plot_ylim_ratio = analysis_dict["plot_ylim_ratio"]
    print("Doing plots")

    proc = subprocess.Popen(
        "mkdir -p plots && " + f"cp {get_fw_path()}/data/common/index.php plots/",
        shell=True,
    )
    proc.wait()

    # FIXME add nuisance for stat
    nuisances["stat"] = {
        "name": "stat",
        "type": "stat",
        "samples": dict((skey, "1.00") for skey in samples),
    }

    cpus = 10
    operating_mode = analysis_dict.get("plot_op_mode", "eft")
    if operating_mode == "validate_sm":
        for sample in list(samples.keys()):
            if "eft" in sample.lower() and "sm" in sample.lower():
                samples[sample]["is_signal"] = True
            elif "sm" in sample.lower():
                samples[sample]["is_data"] = True
            else:
                del samples[sample]
        plot_func = plot_validation
    elif operating_mode == "eft":
        for sample in list(samples.keys()):
            if "eft" not in sample.lower():
                del samples[sample]
            elif "sm" in sample.lower():
                samples[sample]["is_data"] = True
            else:
                samples[sample]["is_signal"] = True
        plot_func = plot_eft
    else:
        raise ValueError("Invalid operating mode")

    with concurrent.futures.ProcessPoolExecutor(max_workers=cpus) as executor:
        tasks = []

        input_file = uproot.open("histos.root")
        for region in regions:
            # if "sr" not in region or "mm" not in region:
            #     continue
            for variable in variables:
                if "axis" not in variables[variable]:
                    continue
                # if variable != "dnn_ptll" or region != "sr_inc_mm":
                #     continue
                tasks.append(
                    executor.submit(
                        plot_func,
                        input_file,
                        region,
                        variable,
                        samples,
                        nuisances,
                        lumi,
                        colors,
                        year_label,
                        blind,
                        variables[variable].get("label"),
                    )
                )
        concurrent.futures.wait(tasks)
        for task in tasks:
            task.result()

    # for region in regions:
    #     for variable in variables:
    #         if "axis" not in variables[variable]:
    #             continue
    #         plot(
    #             input_file,
    #             region,
    #             variable,
    #             samples,
    #             nuisances,
    #             lumi,
    #             colors,
    #             year_label,
    #         )


if __name__ == "__main__":
    main()
