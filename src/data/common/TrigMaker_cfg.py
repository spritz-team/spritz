Trigger = {
    # --------------------------- Full2018v9---------------------------------
    # Full 2018 lumi --> 59.832475339
    "Full2018v9": {
        # Full 2018
        1: {
            "begin": 315252,
            "end": 325175,
            "lumi": 59.832475339,
            "LegEffData": {
                "DoubleEleLegHigPt": "Full2018v9/data/EGM_MVAid/Ele23_Ele12_leg1_pt_eta_efficiency_withSys_Run2018.txt",
                "DoubleEleLegLowPt": "Full2018v9/data/EGM_MVAid/Ele23_Ele12_leg2_pt_eta_efficiency_withSys_Run2018.txt",
                "SingleEle": "Full2018v9/data/EGM_MVAid/Ele32_pt_eta_efficiency_withSys_Run2018.txt",
                "DoubleMuLegHigPt": "Full2018v9/data/Muons/Mu17_Mu8_leg1_pt_eta_2018_SingleMu_nominal_efficiency.txt",
                "DoubleMuLegLowPt": "Full2018v9/data/Muons/Mu17_Mu8_leg2_pt_eta_2018_SingleMu_nominal_efficiency.txt",
                "SingleMu": "Full2018v9/data/Muons/IsoMu24_pt_eta_2018_SingleMu_nominal_efficiency.txt",
                "MuEleLegHigPt": "Full2018v9/data/Muons/Mu23_pt_eta_2018_nominal_efficiency.txt",
                "MuEleLegLowPt": "Full2018v9/data/EGM_MVAid/Ele23_Ele12_leg2_pt_eta_efficiency_withSys_Run2018.txt",
                "EleMuLegHigPt": "Full2018v9/data/EGM_MVAid/Ele23_Ele12_leg1_pt_eta_efficiency_withSys_Run2018.txt",
                "EleMuLegLowPt": "Full2018v9/data/Muons/Mu12_pt_eta_2018_nominal_efficiency.txt",
            },
            "LegEffMC": {
                "DoubleEleLegHigPt": "Full2018v9/mc/EGM_MVAid/Ele23_Ele12_leg1_pt_eta_efficiency_withSys_Run2018.txt",
                "DoubleEleLegLowPt": "Full2018v9/mc/EGM_MVAid/Ele23_Ele12_leg2_pt_eta_efficiency_withSys_Run2018.txt",
                "SingleEle": "Full2018v9/mc/EGM_MVAid/Ele32_pt_eta_efficiency_withSys_Run2018.txt",
                "DoubleMuLegHigPt": "Full2018v9/mc/Muons/Mu17_Mu8_leg1_pt_eta_2018_SingleMu_nominal_efficiency.txt",
                "DoubleMuLegLowPt": "Full2018v9/mc/Muons/Mu17_Mu8_leg2_pt_eta_2018_SingleMu_nominal_efficiency.txt",
                "SingleMu": "Full2018v9/mc/Muons/IsoMu24_pt_eta_2018_SingleMu_nominal_efficiency.txt",
                "MuEleLegHigPt": "Full2018v9/mc/Muons/Mu23_pt_eta_2018_nominal_efficiency.txt",
                "MuEleLegLowPt": "Full2018v9/mc/EGM_MVAid/Ele23_Ele12_leg2_pt_eta_efficiency_withSys_Run2018.txt",
                "EleMuLegHigPt": "Full2018v9/mc/EGM_MVAid/Ele23_Ele12_leg1_pt_eta_efficiency_withSys_Run2018.txt",
                "EleMuLegLowPt": "Full2018v9/mc/Muons/Mu12_pt_eta_2018_nominal_efficiency.txt",
            },
            "DZEffData": {
                "DoubleEle": {"value": [1.0, 0.0]},
                "DoubleMu": {"nvtx": "Full2018v9/DZeff_2018_uu.txt"},
                "MuEle": {"value": [1.0, 0.0]},
                "EleMu": {"nvtx": "Full2018v9/DZeff_2018_eu.txt"},
            },
            "DZEffMC": {
                "DoubleEle": {"value": [1.0, 0.0]},
                "DoubleMu": {"nvtx": "Full2018v9/DZeff_2018_MC_uu.txt"},
                "MuEle": {"value": [1.0, 0.0]},
                "EleMu": {"nvtx": "Full2018v9/DZeff_2018_MC_eu.txt"},
            },
            "DRllSF": {
                "DoubleEle": "DRll_SF_ee.txt",
                "DoubleMu": "DRll_SF_mm.txt",
                "MuEle": "DRll_SF_me.txt",
                "EleMu": "DRll_SF_em.txt",
            },
            # Electron HLT Zvtx Efficiency Scale Factor: 0.934+-0.005
            "GlEff": {
                "DoubleEle": [1.0, 0.0],
                "DoubleMu": [1.0, 0.0],
                "MuEle": [1.0, 0.0],
                "EleMu": [1.0, 0.0],
                "SingleEle": [1.0, 0.0],
                "SingleMu": [1.0, 0.0],
            },
            "EMTFBug": False,
            #'trkSFMu':  [ 1.00 , 1.00 , 1.00 ] , # tracker SF_muons [ cent , up , down ] --> Moved to ID/Iso code
            "DATA": {
                "EleMu": [
                    "HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL",
                    "HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ",
                ],
                "DoubleMu": ["HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8"],
                "SingleMu": ["HLT_IsoMu24"],
                "DoubleEle": ["HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL"],
                "SingleEle": ["HLT_Ele32_WPTight_Gsf"],
            },
            "MC": {
                "EleMu": [
                    "HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL",
                    "HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ",
                ],
                "DoubleMu": ["HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8"],
                "SingleMu": ["HLT_IsoMu24"],
                "DoubleEle": ["HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL"],
                "SingleEle": ["HLT_Ele32_WPTight_Gsf"],
            },
        },
    },
}
