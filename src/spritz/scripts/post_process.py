import concurrent.futures
import fnmatch
import json
import sys

import hist
import numpy as np
import uproot
from spritz.framework.framework import (
    add_dict_iterable,
    get_analysis_dict,
    get_fw_path,
    read_chunks,
)

path_fw = get_fw_path()


def renorm(h, xs, sumw, lumi):
    scale = xs * 1000 * lumi / sumw
    # print(scale)
    _h = h.copy()
    a = _h.view(True)
    a.value = a.value * scale
    a.variance = a.variance * scale * scale
    return _h


def hist_move_content(h, ifrom, ito):
    """
    Moves content of a histogram from `ifrom` bin to `ito` bin.
    Content and sumw2 of bin `ito` will be the sum of the original `ibin`
    and `ito`.
    Content and sumw2 of bin `ifrom` will be 0.
    Modifies in place the histogram.

    Parameters
    ----------
    h : hist
        Histogram
    ifrom : int
        the index of the bin where content will be reset
    ito : int
        the index of the bin where content will be the sum
    """
    dimension = len(h.axes)
    # numpy view is a numpy array containing two keys, value
    # and variances for each bin
    numpy_view = h.view(True)
    content = numpy_view.value
    sumw2 = numpy_view.variance

    if dimension == 1:
        content[ito] += content[ifrom]
        content[ifrom] = 0.0

        sumw2[ito] += sumw2[ifrom]
        sumw2[ifrom] = 0.0

    elif dimension == 2:
        content[ito, :] += content[ifrom, :]
        content[ifrom, :] = 0.0
        content[:, ito] += content[:, ifrom]
        content[:, ifrom] = 0.0

        sumw2[ito, :] += sumw2[ifrom, :]
        sumw2[ifrom, :] = 0.0
        sumw2[:, ito] += sumw2[:, ifrom]
        sumw2[:, ifrom] = 0.0

    elif dimension == 3:
        content[ito, :, :] += content[ifrom, :, :]
        content[ifrom, :, :] = 0.0
        content[:, ito, :] += content[:, ifrom, :]
        content[:, ifrom, :] = 0.0
        content[:, :, ito] += content[:, :, ifrom]
        content[:, :, ifrom] = 0.0

        sumw2[ito, :, :] += sumw2[ifrom, :, :]
        sumw2[ifrom, :, :] = 0.0
        sumw2[:, ito, :] += sumw2[:, ifrom, :]
        sumw2[:, ifrom, :] = 0.0
        sumw2[:, :, ito] += sumw2[:, :, ifrom]
        sumw2[:, :, ifrom] = 0.0


def hist_fold(h, fold_method):
    """
    Fold a histogram (hist object)

    Parameters
    ----------
    h : hist
        Histogram to fold, will be modified in place (aka no copy)
    fold_method : int
        choices 0: no fold
        choices 1: fold underflow
        choices 2: fold overflow
        choices 3: fold both underflow and overflow
    """
    if fold_method == 1 or fold_method == 3:
        hist_move_content(h, 0, 1)
    if fold_method == 2 or fold_method == 3:
        hist_move_content(h, -1, -2)


def hist_unroll(h):
    """
    Unrolls n-dimensional histogram

    Parameters
    ----------
    h : hist
        Histogram to unroll

    Returns
    -------
    hist
        Unrolled 1-dimensional histogram
    """
    dimension = len(h.axes)
    if dimension != 2:
        raise Exception(
            "Error in hist_unroll: can only unroll 2D histograms, while got ",
            dimension,
            "dimensions",
        )

    numpy_view = h.view()  # no under/overflow!
    nx = numpy_view.shape[0]
    ny = numpy_view.shape[1]
    h_unroll = hist.Hist(hist.axis.Regular(nx * ny, 0, nx * ny), hist.storage.Weight())

    numpy_view_unroll = h_unroll.view()
    numpy_view_unroll.value = numpy_view.value.T.flatten()
    numpy_view_unroll.variance = numpy_view.variance.T.flatten()

    return h_unroll


def get_variations(h):
    axis = h.axes[-1]
    variation_names = [axis.value(i) for i in range(len(axis.centers))]
    return variation_names


def blind(region, variable, edges):
    if "sr" in region and "dnn" in variable:
        return np.arange(0, len(edges)) > len(edges) / 2


def single_post_process(results, region, variable, samples, xss, nuisances, lumi):
    dout = {}
    for histoName in samples:
        for sample in samples[histoName]["samples"]:
            try:
                results[sample]["histos"][variable]
            except KeyError:
                print(f"Could not find key {sample} in {variable}")
            h = results[sample]["histos"][variable].copy()
            real_axis = list([slice(None) for _ in range(len(h.axes) - 2)])
            h = h[tuple(real_axis + [hist.loc(region), slice(None)])].copy()
            is_data = samples[histoName].get("is_data", False)
            # renorm mcs
            if not is_data:
                h = renorm(h, xss[sample], results[sample]["sumw"], lumi)

            tmp_histo = h[tuple(real_axis + [hist.loc("nom")])].copy()
            hist_fold(tmp_histo, 3)
            if len(real_axis) > 1:
                tmp_histo = hist_unroll(tmp_histo)
            key = f"{region}/{variable}/histo_{histoName}"
            if key not in dout:
                dout[key] = tmp_histo.copy()
            else:
                dout[key] += tmp_histo.copy()
            nom_histo = tmp_histo.copy()

            for nuis in nuisances:
                if nuisances[nuis]["type"] != "shape":
                    continue
                if histoName not in nuisances[nuis]["samples"]:
                    continue
                if nuisances[nuis]["kind"] in ["suffix", "weight"]:
                    nuis_name = nuisances[nuis]["name"]
                    for tag in ["up", "down"]:
                        tmp_histo = h[
                            tuple(real_axis + [hist.loc(f"{nuis}_{tag}")])
                        ].copy()
                        hist_fold(tmp_histo, 3)
                        if len(real_axis) > 1:
                            tmp_histo = hist_unroll(tmp_histo)
                        key = f"{region}/{variable}/histo_{histoName}_{nuis_name}{tag.capitalize()}"
                        if key not in dout:
                            dout[key] = tmp_histo.copy()
                        else:
                            dout[key] += tmp_histo.copy()
                nuis_kind = nuisances[nuis]["kind"]
                if nuis_kind.endswith("envelope") or nuis_kind.endswith("square"):
                    nuis_name = nuisances[nuis]["name"]
                    variations = []
                    for nuis_histo in nuisances[nuis]["samples"][histoName]:
                        tmp_histo = h[tuple(real_axis + [hist.loc(nuis_histo)])].copy()
                        hist_fold(tmp_histo, 3)
                        if len(real_axis) > 1:
                            tmp_histo = hist_unroll(tmp_histo)
                        variations.append(tmp_histo.values())
                    variations = np.array(variations)
                    arrup = 0
                    arrdo = 0

                    if nuisances[nuis]["kind"].endswith("envelope"):
                        arrup = np.max(variations, axis=0)
                        arrdo = np.min(variations, axis=0)
                    elif nuisances[nuis]["kind"].endswith("square"):
                        arrnom = np.tile(nom_histo.values(), (variations.shape[0], 1))
                        arrv = np.sqrt(np.sum(np.square(variations - arrnom), axis=0))
                        arrup = nom_histo.values() + arrv
                        arrdo = nom_histo.values() - arrv
                    hists = {}
                    hists["Up"] = nom_histo.copy()
                    a = hists["Up"].view()
                    a.value = arrup

                    hists["Down"] = nom_histo.copy()
                    a = hists["Down"].view()
                    a.value = arrdo

                    for tag in ["Up", "Down"]:
                        key = f"{region}/{variable}/histo_{histoName}_{nuis_name}{tag.capitalize()}"
                        tmp_histo = hists[tag]
                        if key not in dout:
                            dout[key] = tmp_histo.copy()
                        else:
                            dout[key] += tmp_histo.copy()
    return dout


def post_process(results, regions, variables, samples, xss, nuisances, lumi):
    print("Start converting histograms")

    cpus = 10

    with concurrent.futures.ProcessPoolExecutor(max_workers=cpus) as executor:
        tasks = []
        print("start post-proc in parallel")
        for region in regions:
            for variable in variables:
                if "axis" not in variables[variable]:
                    continue
                tasks.append(
                    executor.submit(
                        single_post_process,
                        results,
                        region,
                        variable,
                        samples,
                        xss,
                        nuisances,
                        lumi,
                    )
                )
        concurrent.futures.wait(tasks)
        print("done post-proc in parallel")
        results = []
        for task in tasks:
            results.append(task.result())
        dout = add_dict_iterable(results)

    print("start saving in root file")
    fout = uproot.recreate("histos.root")
    for key in dout:
        fout[key] = dout[key]
    fout.close()


def main():
    analysis_dict = get_analysis_dict()
    year = analysis_dict["year"]
    lumi = analysis_dict["lumi"]
    datasets = analysis_dict["datasets"]
    samples = analysis_dict["samples"]
    nuisances = analysis_dict["nuisances"]
    regions = analysis_dict["regions"]
    variables = analysis_dict["variables"]

    with open(f"{path_fw}/data/{year}/samples/samples.json") as file:
        samples_xs = json.load(file)

    xss = {}
    for dataset in datasets:
        if datasets[dataset].get("is_data", False):
            continue
        key = datasets[dataset]["files"]
        print(key)

        # # # FIXME
        # if "DY" in dataset:
        #     samples_xs["samples"][key]["xsec"] += "*0.5"

        if "subsamples" in datasets[dataset]:
            for sub in datasets[dataset]["subsamples"]:
                flat_dataset = f"{dataset}_{sub}"
                # if fnmatch.fnmatch(flat_dataset, "DY*PU"):
                #     xss[flat_dataset] = (
                #         eval(samples_xs["samples"][key]["xsec"]) * 7.7647e-01
                #     )
                # elif fnmatch.fnmatch(flat_dataset, "DY*hard"):
                #     xss[flat_dataset] = (
                #         eval(samples_xs["samples"][key]["xsec"]) * 9.2941e-01
                #     )
                # else:
                #     xss[flat_dataset] = eval(samples_xs["samples"][key]["xsec"])
                xss[flat_dataset] = eval(samples_xs["samples"][key]["xsec"])
                print(flat_dataset, xss[flat_dataset])
        else:
            flat_dataset = dataset
            xss[flat_dataset] = eval(samples_xs["samples"][key]["xsec"])

    print(xss)
    results = read_chunks("condor/results_merged_new.pkl")
    print(results.keys())
    # sys.exit()
    post_process(results, regions, variables, samples, xss, nuisances, lumi)


if __name__ == "__main__":
    main()
