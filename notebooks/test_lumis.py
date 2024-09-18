import pandas as pd
from data.common.TrigMaker_cfg import Trigger

year = "Full2016v9HIPM"
year = "Full2016v9noHIPM"
# year = "Full2017v9"
# year = "Full2018v9"
# runs = []
# for era in Trigger[year]:
#     if "runList" in Trigger[year][era]:
#         runs.extend(Trigger[year][era]["runList"])
#     elif "begin" in Trigger[year][era]:
#         runs.extend(range(Trigger[year][era]["begin"], Trigger[year][era]["end"] + 1))
# print(len(runs))
# print(list(set(runs)) == runs)
# print(runs[0], runs[-1])


fnames = {
    "Full2016v9HIPM": "16HIPM.csv",
    "Full2016v9noHIPM": "16noHIPM.csv",
    "Full2017v9": "17.csv",
    "Full2018v9": "18.csv",
}

fname = fnames[year]
df = pd.read_csv(
    f"lumis/{fname}",
    skiprows=3,
    names=["run_fill", "time", "a", "b", "del", "record"],
    skipfooter=5,
    engine="python",
)

df = df[["run_fill", "record"]]
df["run"] = df["run_fill"].apply(lambda x: int(x.split(":")[0]))
df = df[["run", "record"]]
# print(df)


lumi_tot = 0.0
lumi_tot_old = 0.0
print(year)
for era in Trigger[year]:
    runs = []
    if "runList" in Trigger[year][era]:
        runs = Trigger[year][era]["runList"]
    elif "begin" in Trigger[year][era]:
        runs = list(range(Trigger[year][era]["begin"], Trigger[year][era]["end"] + 1))

    lumi = df[df["run"].isin(runs)]["record"].sum()
    lumi_tot += lumi
    lumi_old = Trigger[year][era]["lumi"]
    lumi_tot_old += lumi_old
    print(era, lumi, lumi_old - lumi, (lumi_old - lumi) / lumi * 100)

print("Tot lumi", lumi_tot)
print("Tot lumi old", lumi_tot_old)
