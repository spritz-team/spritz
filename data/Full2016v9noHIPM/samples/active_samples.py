active_samples = [
    # DY NLO
    "DYJetsToLL_M-50",
    # DY Jet binned
    "DYJetsToLL_0J",
    "DYJetsToLL_1J",
    "DYJetsToLL_2J",
    # # DY LO
    # "DYJetsToLL_M-50-LO",
    # "DYJetsToLL_M-50-LO_ext1",
    # Signal
    "EWK_LLJJ_MLL-50_MJJ-120",
    # # Interference
    "EWK_LLJJ_MLL-50_MJJ-120_QCD",
    # Top
    "TTTo2L2Nu",
    "ST_s-channel",
    "ST_t-channel_antitop",
    "ST_t-channel_top",
    "ST_tW_antitop",
    "ST_tW_top",
]

DataRun = [
    ["F", "Run2016F-UL2016-v1"],
    ["G", "Run2016G_UL2016-v1"],
    ["H", "Run2016H_UL2016-v1"],
]

DataSets = ["MuonEG", "SingleMuon", "SingleElectron", "DoubleMuon", "DoubleEG"]

for _, sd in DataRun:
    for pd in DataSets:
        tag = pd + "_" + sd
        if "DoubleMuon" in pd and "Run2016G" in sd:
            tag = tag.replace("v1", "v2")
        active_samples.append(tag)
