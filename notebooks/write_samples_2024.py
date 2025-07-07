import json

Samples = {}


# pd = "JetMET"
# for pd_t in range(2):
#     for era, tag in [
#         ("C", "ReReco"),
#         ("D", "ReReco"),
#         ("E", "ReReco"),
#         ("F", "Prompt"),
#         ("G", "Prompt"),
#         ("H", "Prompt"),
#         ("I", "Prompt"),
#     ]:
#         version = "v1"
#         if era == "F" or era == "G" or era == "H":
#             version = "v2"
#         if era == "I" and pd_t == 0:
#             version = "v2"

#         Samples[f"{pd}{pd_t}_Run2024{era}-{tag}-v1"] = {
#             "nanoAOD": f"/{pd}{pd_t}/Run2024{era}-MINIv6NANOv15-{version}/NANOAOD",
#         }

Samples["MuonEG_Run2024C-ReReco-v1"] = {
    "nanoAOD": "/MuonEG/Run2024C-MINIv6NANOv15-v1/NANOAOD",
}
Samples["MuonEG_Run2024D-ReReco-v1"] = {
    "nanoAOD": "/MuonEG/Run2024D-MINIv6NANOv15-v1/NANOAOD",
}
Samples["MuonEG_Run2024E-ReReco-v1"] = {
    "nanoAOD": "/MuonEG/Run2024E-MINIv6NANOv15-v1/NANOAOD",
}
Samples["MuonEG_Run2024F-Prompt-v1"] = {
    "nanoAOD": "/MuonEG/Run2024F-MINIv6NANOv15-v2/NANOAOD",
}
Samples["MuonEG_Run2024G-Prompt-v1"] = {
    "nanoAOD": "/MuonEG/Run2024G-MINIv6NANOv15-v3/NANOAOD",
}
Samples["MuonEG_Run2024H-Prompt-v1"] = {
    "nanoAOD": "/MuonEG/Run2024H-MINIv6NANOv15-v2/NANOAOD",
}
Samples["MuonEG_Run2024I-Prompt-v1"] = {
    "nanoAOD": "/MuonEG/Run2024I-MINIv6NANOv15-v2/NANOAOD",
}

Samples["Muon0_Run2024C-ReReco-v1"] = {
    "nanoAOD": "/Muon0/Run2024C-MINIv6NANOv15-v1/NANOAOD",
}
Samples["Muon0_Run2024D-ReReco-v1"] = {
    "nanoAOD": "/Muon0/Run2024D-MINIv6NANOv15-v1/NANOAOD",
}
Samples["Muon0_Run2024E-ReReco-v1"] = {
    "nanoAOD": "/Muon0/Run2024E-MINIv6NANOv15-v1/NANOAOD",
}
Samples["Muon0_Run2024F-Prompt-v1"] = {
    "nanoAOD": "/Muon0/Run2024F-MINIv6NANOv15-v1/NANOAOD",
}
Samples["Muon0_Run2024G-Prompt-v1"] = {
    "nanoAOD": "/Muon0/Run2024G-MINIv6NANOv15-v1/NANOAOD",
}
Samples["Muon0_Run2024H-Prompt-v1"] = {
    "nanoAOD": "/Muon0/Run2024H-MINIv6NANOv15-v1/NANOAOD",
}
Samples["Muon0_Run2024I-Prompt-v1"] = {
    "nanoAOD": "/Muon0/Run2024I-MINIv6NANOv15-v1/NANOAOD",
}
# Samples["Muon0_Run2024I-Prompt-v2"] = {  # Is there Run2024I-v2 in nanoAODv15?
#    "nanoAOD": "",
# }
Samples["Muon1_Run2024C-ReReco-v1"] = {
    "nanoAOD": "/Muon1/Run2024C-MINIv6NANOv15-v1/NANOAOD",
}
Samples["Muon1_Run2024D-ReReco-v1"] = {
    "nanoAOD": "/Muon1/Run2024D-MINIv6NANOv15-v1/NANOAOD",
}
Samples["Muon1_Run2024E-ReReco-v1"] = {
    "nanoAOD": "/Muon1/Run2024E-MINIv6NANOv15-v1/NANOAOD",
}
Samples["Muon1_Run2024F-Prompt-v1"] = {
    "nanoAOD": "/Muon1/Run2024F-MINIv6NANOv15-v1/NANOAOD",
}
Samples["Muon1_Run2024G-Prompt-v1"] = {
    "nanoAOD": "/Muon1/Run2024G-MINIv6NANOv15-v2/NANOAOD",
}
Samples["Muon1_Run2024H-Prompt-v1"] = {
    "nanoAOD": "/Muon1/Run2024H-MINIv6NANOv15-v2/NANOAOD",
}
Samples["Muon1_Run2024I-Prompt-v1"] = {
    "nanoAOD": "/Muon1/Run2024I-MINIv6NANOv15-v1/NANOAOD",
}
# Samples["Muon1_Run2024I-Prompt-v2"] = {
#    "nanoAOD": "",
# }


Samples["EGamma0_Run2024C-ReReco-v1"] = {
    "nanoAOD": "/EGamma0/Run2024C-MINIv6NANOv15-v1/NANOAOD",
}
Samples["EGamma0_Run2024D-ReReco-v1"] = {
    "nanoAOD": "/EGamma0/Run2024D-MINIv6NANOv15-v1/NANOAOD",
}
Samples["EGamma0_Run2024E-ReReco-v1"] = {
    "nanoAOD": "/EGamma0/Run2024E-MINIv6NANOv15-v1/NANOAOD",
}
Samples["EGamma0_Run2024F-Prompt-v1"] = {
    "nanoAOD": "/EGamma0/Run2024F-MINIv6NANOv15-v1/NANOAOD",
}
Samples["EGamma0_Run2024G-Prompt-v1"] = {
    "nanoAOD": "/EGamma0/Run2024G-MINIv6NANOv15-v2/NANOAOD",
}
Samples["EGamma0_Run2024H-Prompt-v1"] = {
    "nanoAOD": "/EGamma0/Run2024H-MINIv6NANOv15-v2/NANOAOD",
}
Samples["EGamma0_Run2024I-Prompt-v1"] = {
    "nanoAOD": "/EGamma0/Run2024I-MINIv6NANOv15-v1/NANOAOD",
}
# Samples["EGamma0_Run2024I-Prompt-v2"] = {
#    "nanoAOD": "",
# }
Samples["EGamma1_Run2024C-ReReco-v1"] = {
    "nanoAOD": "/EGamma1/Run2024C-MINIv6NANOv15-v1/NANOAOD",
}
Samples["EGamma1_Run2024D-ReReco-v1"] = {
    "nanoAOD": "/EGamma1/Run2024D-MINIv6NANOv15-v1/NANOAOD",
}
Samples["EGamma1_Run2024E-ReReco-v1"] = {
    "nanoAOD": "/EGamma1/Run2024E-MINIv6NANOv15-v1/NANOAOD",
}
Samples["EGamma1_Run2024F-Prompt-v1"] = {
    "nanoAOD": "/EGamma1/Run2024F-MINIv6NANOv15-v1/NANOAOD",
}
Samples["EGamma1_Run2024G-Prompt-v1"] = {
    "nanoAOD": "/EGamma1/Run2024G-MINIv6NANOv15-v2/NANOAOD",
}
Samples["EGamma1_Run2024H-Prompt-v1"] = {
    "nanoAOD": "/EGamma1/Run2024H-MINIv6NANOv15-v1/NANOAOD",
}
Samples["EGamma1_Run2024I-Prompt-v1"] = {
    "nanoAOD": "/EGamma1/Run2024I-MINIv6NANOv15-v1/NANOAOD",
}
# Samples["EGamma1_Run2024I-Prompt-v2"] = {
#    "nanoAOD": "",
# }

Samples["MuonEG_Run2024C-ReReco-v1"] = {
    "nanoAOD": "/MuonEG/Run2024C-MINIv6NANOv15-v1/NANOAOD",
}
Samples["MuonEG_Run2024D-ReReco-v1"] = {
    "nanoAOD": "/MuonEG/Run2024D-MINIv6NANOv15-v1/NANOAOD",
}
Samples["MuonEG_Run2024E-ReReco-v1"] = {
    "nanoAOD": "/MuonEG/Run2024E-MINIv6NANOv15-v1/NANOAOD",
}
Samples["MuonEG_Run2024F-Prompt-v1"] = {
    "nanoAOD": "/MuonEG/Run2024F-MINIv6NANOv15-v2/NANOAOD",
}
Samples["MuonEG_Run2024G-Prompt-v1"] = {
    "nanoAOD": "/MuonEG/Run2024G-MINIv6NANOv15-v3/NANOAOD",
}
Samples["MuonEG_Run2024H-Prompt-v1"] = {
    "nanoAOD": "/MuonEG/Run2024H-MINIv6NANOv15-v2/NANOAOD",
}
Samples["MuonEG_Run2024I-Prompt-v1"] = {
    "nanoAOD": "/MuonEG/Run2024I-MINIv6NANOv15-v2/NANOAOD",
}
# Samples["MuonEG_Run2024I-Prompt-v2"] = {
#    "nanoAOD": ""
# }


## DY -> ee
# Samples["DYto2E-2Jets_MLL-10to50"] = {
#     "nanoAOD": "/DYto2E_Bin-MLL-10to50_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2/NANOAODSIM"
# }
Samples["DYto2E-2Jets_MLL-50"] = {
    "nanoAOD": "/DYto2E-2Jets_Bin-MLL-50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v4/NANOAODSIM"
}
# Samples["DYto2E-2Jets_MLL-50-LO"] = {
#     "nanoAOD": "/DYto2E-4Jets_Bin-MLL-50_TuneCP5_13p6TeV_madgraphMLM-pythia8/RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v3/NANOAODSIM"
# }

## DY -> mm
# Samples["DYto2Mu-2Jets_MLL-10to50"] = {
#     "nanoAOD": "/DYto2Mu_Bin-MLL-10to50_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2/NANOAODSIM"
# }
Samples["DYto2Mu-2Jets_MLL-50"] = {
    "nanoAOD": "/DYto2Mu-2Jets_Bin-MLL-50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v6/NANOAODSIM"  # Not yet
}
# Samples["DYto2Mu-2Jets_MLL-50-LO"] = {
#     "nanoAOD": "/DYto2Mu-4Jets_Bin-MLL-50_TuneCP5_13p6TeV_madgraphMLM-pythia8/RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v3/NANOAODSIM"  # Not yet
# }


## DY -> tt
# Samples["DYto2Tau-2Jets_MLL-10to50"] = {
#     "nanoAOD": "/DYto2Tau_Bin-MLL-10to50_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2/NANOAODSIM"
# }
Samples["DYto2Tau-2Jets_MLL-50"] = {
    "nanoAOD": "/DYto2Tau-2Jets_Bin-MLL-50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v5/NANOAODSIM"
}

# Samples["DYto2Tau-2Jets_MLL-50-LO"] = {
#     "nanoAOD": "/DYto2Tau-4Jets_Bin-MLL-50_TuneCP5_13p6TeV_madgraphMLM-pythia8/RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v3/NANOAODSIM"
# }

Samples["TTTo2L2Nu"] = {
    "nanoAOD": "/TTto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v3/NANOAODSIM"
}

# Samples["TWplusto2L2Nu"] = {
#     "nanoAOD": "/TWplusto2L2Nu-DS_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2/NANOAODSIM"
# }

# Samples["TWminusto2L2Nu"] = {
#     "nanoAOD": "/TWminusto2L2Nu-DS_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2/NANOAODSIM"
# }

# single top
Samples["TBbarQtoLNu"] = {
    "nanoAOD": "/TBbarQtoLNu-t-channel-4FS_TuneCP5_13p6TeV_powheg-madspin-pythia8/RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2/NANOAODSIM"
}
Samples["TbarBQtoLNu"] = {
    "nanoAOD": "/TbarBQtoLNu-t-channel-4FS_TuneCP5_13p6TeV_powheg-madspin-pythia8/RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2/NANOAODSIM"
}

xs_db = {}
# DY
xs_db["DYJetsToLL_M-50-LO"] = ["xsec=6275.1", "kfact=1.000", "ref=A"]  # 2091.7 * 3
xs_db["DYto2L-2Jets_MLL-50"] = ["xsec=6275.1", "kfact=1.000", "ref=A"]  # 2091.7 * 3
xs_db["DYto2L-2Jets_MLL-10to50"] = ["xsec=19982.5", "kfact=1.000", "ref=H"]

xs_db["DYto2E-2Jets_MLL-10to50"] = [
    "xsec=6660.8",
    "kfact=1.000",
    "ref=H",
]  # 19982.5 / 3
xs_db["DYto2E-2Jets_MLL-50"] = ["xsec=2091.7", "kfact=1.000", "ref=A"]
# xs_db["DYto2E-2Jets_MLL-50-LO"] = ["xsec=2091.7", "kfact=1.000", "ref=A"]

# xs_db["DYto2Mu-2Jets_MLL-10to50"] = ["xsec=6660.8", "kfact=1.000", "ref=H"]
xs_db["DYto2Mu-2Jets_MLL-50"] = ["xsec=2091.7", "kfact=1.000", "ref=A"]
# xs_db["DYto2Mu-2Jets_MLL-50-LO"] = ["xsec=2091.7", "kfact=1.000", "ref=A"]

# xs_db["DYto2Tau-2Jets_MLL-10to50"] = ["xsec=6660.8", "kfact=1.000", "ref=H"]
xs_db["DYto2Tau-2Jets_MLL-50"] = ["xsec=2091.7", "kfact=1.000", "ref=A"]
# xs_db["DYto2Tau-2Jets_MLL-50-LO"] = ["xsec=2091.7", "kfact=1.000", "ref=A"]

xs_db["TTTo2L2Nu"] = [
    "xsec=0.950*923.6*0.1086*0.1086*9",
    "kfact=1.000",
    "ref=Guillelmo",
]

xs_db["TWplusto2L2Nu"] = [
    "xsec=4.67",
    "kfact=1.000",
    "ref=Guillelmo",
]

xs_db["TWminusto2L2Nu"] = [
    "xsec=4.67",
    "kfact=1.000",
    "ref=Guillelmo",
]


samples = {}
for sample in Samples:
    if sample in xs_db:
        samples[sample] = {
            "nanoAOD": Samples[sample]["nanoAOD"],
            "xsec": xs_db[sample][0].split("=")[-1],
            "kfac": xs_db[sample][1],
            "ref": xs_db[sample][2],
        }
    else:
        samples[sample] = {
            "nanoAOD": Samples[sample]["nanoAOD"],
        }

with open("../data/Full2024v15/samples/samples.json", "w") as f:
    json.dump({"headers": [], "samples": samples}, f, indent=2)
