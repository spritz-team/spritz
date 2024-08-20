import numpy as np
import awkward as ak
from data.common.TrigMaker_cfg import Trigger


def assign_run(events, is_data, cfg, ceval_assign_run):
    # events = ak.zip({'run_number': np.arange(100_000)})
    if is_data:
        events["run_period"] = ceval_assign_run.evaluate(events.run_number)
    else:
        if len(events) > 0:
            rnd_seed = events[0].run_number
        else:
            rnd_seed = 1291
        rng = np.random.Generator(np.random.PCG64(rnd_seed))
        trig = Trigger[cfg["era"]]
        eras = np.array([era for era in trig])
        lumis = np.array([trig[era]["lumi"] for era in trig])
        cdf = np.cumsum(lumis)
        cdf = cdf / cdf[-1]
        values = rng.random(size=len(events))
        value_bins = np.searchsorted(cdf, values)
        events["run_period"] = eras[value_bins]

    events['run_period'] = ak.values_astype(events.run_period, int)
    return events
