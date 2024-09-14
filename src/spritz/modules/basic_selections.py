import json

import awkward as ak
import fsspec
import numba
import numpy
from data.common.TrigMaker_cfg import Trigger
from numba import types
from numba.typed import Dict


def pass_trigger(events, year):
    keys = ["SingleEle", "DoubleEle", "SingleMu", "DoubleMu"]
    for key in keys:
        events[key] = ak.ones_like(events.weight) == 0.0  # all False

    # since each era might have a different trigger we loop on them and look for events
    # that pass an era cut (e.g. event is of era "B") and apply those cuts

    for era in Trigger[year]:
        for key in keys:
            tmp = ak.ones_like(events.weight) == 0.0  # all False
            for val in Trigger[year][era]["MC"][key]:
                # some hlt flags are not present in some files for some eras
                # e.g. DZ filters in '16
                try:
                    events.HLT[val[len("HLT_") :]]
                except ak.errors.FieldNotFoundError:
                    events[("HLT", val[len("HLT_") :])] = (
                        ak.ones_like(events.weight) != 1.0
                    )

                tmp = tmp | events.HLT[val[len("HLT_") :]]
            events[key] = events[key] | (events.run_period == era) & tmp

    pass_trigger = ak.ones_like(events.weight) == 0.0  # all False
    for key in keys:
        pass_trigger = pass_trigger | events[key]
    events["pass_trigger"] = pass_trigger
    return events


def pass_flags(events, flags):
    events["pass_flags"] = ak.ones_like(events.weight) == 1.0  # all True
    for flag in flags:
        events["pass_flags"] = events["pass_flags"] & events.Flag[flag]
    return events


# copied from coffea!
class LumiMask:
    """Holds a luminosity mask index, and provides vectorized lookup

    Parameters
    ----------
        jsonfile : str
            Path the the 'golden json' file or other valid lumiSection database in json format.

    This class parses a CMS lumi json into an efficient valid lumiSection lookup table
    """

    def __init__(self, jsonfile):
        with fsspec.open(jsonfile) as fin:
            goldenjson = json.load(fin)

        self._masks = {}

        for run, lumilist in goldenjson.items():
            mask = numpy.array(lumilist, dtype=numpy.uint32).flatten()
            mask[::2] -= 1
            self._masks[numpy.uint32(run)] = mask

    def __call__(self, runs, lumis):
        """Check if run and lumi are valid

        Parameters
        ----------
            runs : numpy.ndarray or awkward.highlevel.Array or dask_awkward.Array
                Vectorized list of run numbers
            lumis : numpy.ndarray or awkward.highlevel.Array or dask_awkward.Array
                Vectorized list of lumiSection numbers

        Returns
        -------
            mask_out : numpy.ndarray
                An array of dtype `bool` where valid (run, lumi) tuples
                will have their corresponding entry set ``True``.
        """

        def apply(runs, lumis):
            # fill numba typed dict
            _masks = Dict.empty(key_type=types.uint32, value_type=types.uint32[:])
            for k, v in self._masks.items():
                _masks[k] = v

            runs_orig = runs
            if isinstance(runs, ak.highlevel.Array):
                runs = ak.to_numpy(ak.typetracer.length_zero_if_typetracer(runs))
            if isinstance(lumis, ak.highlevel.Array):
                lumis = ak.to_numpy(ak.typetracer.length_zero_if_typetracer(lumis))
            mask_out = numpy.zeros(dtype="bool", shape=runs.shape)
            LumiMask._apply_run_lumi_mask_kernel(_masks, runs, lumis, mask_out)
            if isinstance(runs_orig, ak.Array):
                mask_out = ak.Array(mask_out)
            if ak.backend(runs_orig) == "typetracer":
                mask_out = ak.Array(mask_out.layout.to_typetracer(forget_length=True))
            return mask_out

        return apply(runs, lumis)

    # This could be run in parallel, but windows does not support it
    @staticmethod
    @numba.njit(parallel=False, fastmath=True)
    def _apply_run_lumi_mask_kernel(masks, runs, lumis, mask_out):
        for iev in numba.prange(len(runs)):
            run = numpy.uint32(runs[iev])
            lumi = numpy.uint32(lumis[iev])

            if run in masks:
                lumimask = masks[run]
                ind = numpy.searchsorted(lumimask, lumi)
                if numpy.mod(ind, 2) == 1:
                    mask_out[iev] = 1


def lumi_mask(events, lumimask):
    return events[lumimask(events.run, events.luminosityBlock)]
