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

DataRun = [
    ["B", "Run2016B-ver2_HIPM_UL2016-v2"],
    ["C", "Run2016C-HIPM_UL2016-v2"],
    ["D", "Run2016D-HIPM_UL2016-v2"],
    ["E", "Run2016E-HIPM_UL2016-v2"],
    ["F", "Run2016F-HIPM_UL2016-v2"],
]

DataSets = ["MuonEG", "SingleMuon", "SingleElectron", "DoubleMuon", "DoubleEG"]
for _, sd in DataRun:
    for pd in DataSets:
        tag = pd + "_" + sd
        if "DoubleEG" in pd and "Run2016B-ver2" in sd:  # Run2016B-ver2_HIPM_UL2016-v2
            tag = tag.replace("v2", "v3")
        active_samples.append(tag)
