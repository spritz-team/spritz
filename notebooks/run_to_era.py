from data.common.TrigMaker_cfg import Trigger
import hist
import numpy as np
import correctionlib
import correctionlib.convert
import rich
import gzip


ERA = "Full2017v9"

for ERA, year in [
    ("Full2018v9", "2018"),
    ("Full2017v9", "2017"),
    ("Full2016v9HIPM", "2016preVFP"),
    ("Full2016v9noHIPM", "2016postVFP"),
]:
    run_ranges = {}
    for era in Trigger[ERA]:
        if 'begin' in Trigger[ERA][era]:
            begin = Trigger[ERA][era]["begin"]
            end = Trigger[ERA][era]["end"]+1
            run_ranges[(begin, end)] = era
        else:
            for run in  sorted(Trigger[ERA][era]['runList']):
                begin = run
                end = run + 1
                run_ranges[(begin, end)] = era
    bins = []
    vals = []
    for (begin, end), era in run_ranges.items():
        if len(bins) > 0:
            if bins[-1] != begin:
                vals.append(-1)
                bins.append(begin)
        else:
            bins.append(begin)
        vals.append(era)
        bins.append(end)

    # vals = vals[:-1]
    print(bins)
    print(vals)

    h = hist.Hist(
        hist.axis.Variable(np.array(bins), flow=False, name="run_number"),
        hist.storage.Double(),
        data=np.array(vals),
    )
    h.name = "eras"
    h.label = "era"
    print(h)

    cset = correctionlib.convert.from_histogram(h)
    rich.print(cset)

    import os

    os.makedirs(f"../data/{ERA}/clib", exist_ok=True)
    with gzip.open(f"../data/{ERA}/clib/run_to_era.json.gz", "wt") as fout:
        fout.write(cset.json(exclude_unset=True))

    # ceval = cset.to_evaluator()
    # runs = np.arange(297020, 306463)
    # print(ceval.evaluate(runs))
