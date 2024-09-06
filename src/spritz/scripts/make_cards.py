import os
import sys
from textwrap import dedent

import numpy as np
import uproot


def get_datacard_header(bin_name, data_integral):
    return dedent(f"""\n
    ## Shape input card
    imax 1 number of channels
    jmax * number of background
    kmax * number of nuisance parameters
    ----------------------------------------------------------------------------------------------------
    bin         {bin_name}
    observation {data_integral}
    shapes  *           * shapes.root     histo_$PROCESS histo_$PROCESS_$SYSTEMATIC
    shapes  data_obs           * shapes.root     histo_Data
    """)


def make_datacard(
    input_file,
    region,
    variable,
    nuisances,
    samples,
):
    output_path = f"datacards/{region}/{variable}"

    os.makedirs(output_path, exist_ok=True)
    output_file = uproot.recreate(f"{output_path}/shapes.root")

    sig_idx = 0
    bkg_idx = 1

    bin_name = f"{region}_{variable}"
    rows = [
        ["bin"],
        ["process"],
        ["process"],
        ["rate"],
    ]
    systs = {}

    h_data = 0
    for sample_name in samples:
        final_name = f"{region}/{variable}/histo_{sample_name}"
        h = input_file[final_name].to_hist().copy()
        name = samples[sample_name].get("name", sample_name)
        is_signal = samples[sample_name].get("is_signal", False)
        is_data = samples[sample_name].get("is_data", False)
        noStat = samples[sample_name].get("noStat", False)

        if is_signal:
            idx = sig_idx
            sig_idx -= 1
        else:
            idx = bkg_idx
            bkg_idx += 1

        if is_data:
            h_data = h.copy()

        if is_data and name != "Data":
            raise Exception("Cannot use is_data with a name != 'Data'")

        if noStat:
            histo_view = h.view(True)
            histo_view.variance = np.zeros_like(histo_view.variance)

        rows[0].append(bin_name)
        rows[1].append(name)
        rows[2].append(str(idx))
        rows[3].append(str(np.sum(h.values(True))))

        for systematic in nuisances:
            if sample_name in nuisances[systematic]["samples"]:
                if nuisances[systematic]["type"] == "lnN":
                    syst = nuisances[systematic]["samples"][sample_name]
                else:
                    syst = "1.0"
                    for tag in ["Up", "Down"]:
                        _final_name = final_name + f"_{systematic}{tag}"
                        _h = input_file[_final_name].to_hist().copy()
                        output_file[f"histo_{name}_{systematic}{tag}"] = _h
            else:
                syst = "-"
            if systematic not in systs:
                systs[systematic] = [nuisances[systematic]["type"], syst]
            else:
                systs[systematic].append(syst)

        output_file[f"histo_{name}"] = h

    if isinstance(h_data, int):
        h_data = h.copy()
        histo_view = h_data.view(True)
        histo_view.value = np.zeros_like(histo_view.value)
        histo_view.variance = np.zeros_like(histo_view.variance)
        output_file["histo_Data"] = h_data
    datacard = get_datacard_header(bin_name, np.sum(h_data.values(True)))
    for row in rows:
        datacard += "\t".join(row) + "\n"

    datacard += "-" * 100 + "\n"

    for syst in systs:
        datacard += nuisances[syst]["name"] + "\t" + "\t".join(systs[syst]) + "\n"
    with open(f"{output_path}/datacard.txt", "w") as file:
        file.write(datacard)


def main():
    path = os.path.abspath("analysis")
    print("Working in analysis path:", path)
    sys.path.insert(0, path)

    exec("import config as analysis_cfg", globals(), globals())
    analysis_dict = analysis_cfg.__dict__  # type: ignore # noqa: F821
    samples = analysis_dict["samples"]
    nuisances = analysis_dict["nuisances"]
    regions = analysis_dict["regions"]
    variables = analysis_dict["variables"]
    fin = uproot.open("histos.root")
    for region in regions:
        for variable in variables:
            if "axis" not in variables[variable]:
                continue
            make_datacard(
                fin,
                region,
                variable,
                nuisances,
                samples,
            )


if __name__ == "__main__":
    main()
