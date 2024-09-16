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
    "WW_TuneCP5_13TeV-pythia8",
    "WZ_TuneCP5_13TeV-pythia8",
    "ZZ_TuneCP5_13TeV-pythia8",
]

# Data
DataRun = [
    ["B", "Run2017B-UL2017-v1"],
    ["C", "Run2017C-UL2017-v1"],
    ["D", "Run2017D-UL2017-v1"],
    ["E", "Run2017E-UL2017-v1"],
    ["F", "Run2017F-UL2017-v1"],
]

DataSets = ["MuonEG", "SingleMuon", "SingleElectron", "DoubleMuon", "DoubleEG"]
for _, sd in DataRun:
    for pd in DataSets:
        active_samples.append(pd + "_" + sd)
