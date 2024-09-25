from data.common.TrigMaker_cfg import Trigger


# year = "Full2016v9noHIPM"
for year in Trigger:
    lumi = 0.0
    for era in Trigger[year]:
        lumi += float(Trigger[year][era]['lumi'])
    print(year, lumi)
