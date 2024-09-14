from copy import deepcopy

import matplotlib as mpl

mpl.use("Agg")
import matplotlib.pyplot as plt
import mplhep as hep
import numpy as np
import uproot

d = deepcopy(hep.style.CMS)

d["font.size"] = 12
d["figure.figsize"] = (5, 5)

plt.style.use(d)

# from spritz.framework.framework import read_chunks

# results = read_chunks("../configs/vbfz-2017/results_backup.pkl")
# print(results.keys())

f = uproot.open("../configs/vbfz-2017/histos.root")
h1 = f["sr_inc_ee/mjj/histo_DY_PU"].to_hist()
h2 = f["sr_inc_ee/mjj/histo_DY_hard"].to_hist()
fig, ax = plt.subplots(2, 1, dpi=200, height_ratios=(3, 1), sharex=True)

fig.tight_layout(pad=-0.5)
hep.cms.label(
    "sr", data=True, lumi=round(41, 2), ax=ax[0], year="2017"
)  # ,fontsize=16)
ax[0].stairs(h1.values(), h1.axes[0].edges, label="PU")
ax[0].stairs(h2.values(), h1.axes[0].edges, label="hard")
ax[0].legend()
ax[0].set_yscale("log")
ax[1].stairs(h1.values() / h2.values(), h1.axes[0].edges, baseline=0.0)
ax[1].set_xlabel(r"$m_{jj}\;[GeV]$")
plt.savefig(
    "ratio_dy.png",
    facecolor="white",
    pad_inches=0.1,
    bbox_inches="tight",
)
