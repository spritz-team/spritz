ElectronWP = {
    "Full2018v9": {
        ## ------------
        "VetoObjWP": {
            "HLTsafe": {
                "cuts": {
                    # Common cuts
                    "True": ["False"],
                },
            },
        },
        # ------------
        "FakeObjWP": {
            "HLTsafe": {
                "cuts": {
                    # Common cuts
                    "True": [
                        'abs(electron_col[LF_idx]["eta"]) < 2.5',
                        'electron_col[LF_idx]["cutBased"] >= 3',
                        'electron_col[LF_idx]["convVeto"] == 1',
                    ],
                    # Barrel
                    'abs(electron_col[LF_idx]["eta"]) <= 1.479': [
                        'abs(electron_col[LF_idx]["dxy"]) < 0.05',
                        'abs(electron_col[LF_idx]["dz"]) < 0.1',
                    ],
                    # EndCap
                    'abs(electron_col[LF_idx]["eta"]) > 1.479': [
                        'electron_col[LF_idx]["sieie"] < 0.03 ',
                        'abs(electron_col[LF_idx]["eInvMinusPInv"]) < 0.014',
                        'abs(electron_col[LF_idx]["dxy"]) < 0.1',
                        'abs(electron_col[LF_idx]["dz"]) < 0.2',
                    ],
                },
            },
        },
        # ------------
        "TightObjWP": {
            # ----- mvaFall17V2Iso
            "mvaFall17V2Iso_WP90": {
                "cuts": {
                    # Common cuts
                    "True": [
                        'abs(electron_col[LF_idx]["eta"]) < 2.5',
                        'electron_col[LF_idx]["mvaFall17V2Iso_WP90"]',
                        'electron_col[LF_idx]["convVeto"] == 1',
                        'electron_col[LF_idx]["pfRelIso03_all"] < 0.06',
                    ],
                    # Barrel
                    'abs(electron_col[LF_idx]["eta"]) <= 1.479': [
                        'abs(electron_col[LF_idx]["dxy"]) < 0.05',
                        'abs(electron_col[LF_idx]["dz"]) < 0.1',
                    ],
                    # EndCap
                    'abs(electron_col[LF_idx]["eta"]) > 1.479': [
                        'abs(electron_col[LF_idx]["dxy"]) < 0.1',
                        'abs(electron_col[LF_idx]["dz"]) < 0.2',
                    ],
                },
                "tkSF": {
                    "1-1": "/cvmfs/cms.cern.ch/rsync/cms-nanoAOD/jsonpog-integration/POG/EGM/2018_UL/electron.json.gz"
                },
                "wpSF": {
                    "1-1": "LatinoAnalysis/NanoGardener/python/data/scale_factor/Full2018v9/egammaEffi_TightHWW_2018.txt",
                },
                "fakeW": "/LatinoAnalysis/NanoGardener/python/data/fake_prompt_rates/Full2018v9/mvaFall17V2Iso_WP90/",
            },
        },
    },
    "Full2017v9": {
        ## ------------
        "VetoObjWP": {
            "HLTsafe": {
                "cuts": {
                    # Common cuts
                    "True": ["False"],
                },
            },
        },
        # ------------
        "FakeObjWP": {
            "HLTsafe": {
                "cuts": {
                    # Common cuts
                    "True": [
                        'abs(electron_col[LF_idx]["eta"]) < 2.5',
                        'electron_col[LF_idx]["cutBased"] >= 3',
                        'electron_col[LF_idx]["convVeto"] == 1',
                    ],
                    # Barrel
                    'abs(electron_col[LF_idx]["eta"]) <= 1.479': [
                        'abs(electron_col[LF_idx]["dxy"]) < 0.05',
                        'abs(electron_col[LF_idx]["dz"]) < 0.1',
                    ],
                    # EndCap
                    'abs(electron_col[LF_idx]["eta"]) > 1.479': [
                        'electron_col[LF_idx]["sieie"] < 0.03 ',
                        'abs(electron_col[LF_idx]["eInvMinusPInv"]) < 0.014',
                        'abs(electron_col[LF_idx]["dxy"]) < 0.1',
                        'abs(electron_col[LF_idx]["dz"]) < 0.2',
                    ],
                },
            },
        },
        # ------------
        "TightObjWP": {
            # ----- mvaFall17V2Iso
            "mvaFall17V2Iso_WP90": {
                "cuts": {
                    # Common cuts
                    "True": [
                        'abs(electron_col[LF_idx]["eta"]) < 2.5',
                        'electron_col[LF_idx]["mvaFall17V2Iso_WP90"]',
                        'electron_col[LF_idx]["convVeto"] == 1',
                        'electron_col[LF_idx]["pfRelIso03_all"] < 0.06',
                    ],
                    # Barrel
                    'abs(electron_col[LF_idx]["eta"]) <= 1.479': [
                        'abs(electron_col[LF_idx]["dxy"]) < 0.05',
                        'abs(electron_col[LF_idx]["dz"]) < 0.1',
                    ],
                    # EndCap
                    'abs(electron_col[LF_idx]["eta"]) > 1.479': [
                        'abs(electron_col[LF_idx]["dxy"]) < 0.1',
                        'abs(electron_col[LF_idx]["dz"]) < 0.2',
                    ],
                },
                "tkSF": {
                    "1-5": "/cvmfs/cms.cern.ch/rsync/cms-nanoAOD/jsonpog-integration/POG/EGM/2017_UL/electron.json.gz"
                },
                "wpSF": {
                    "1-4": "LatinoAnalysis/NanoGardener/python/data/scale_factor/Full2017v9/egammaEffi_TightHWW_2017BCDE.txt",
                    "5-5": "LatinoAnalysis/NanoGardener/python/data/scale_factor/Full2017v9/egammaEffi_TightHWW_2017F.txt",
                },
                "fakeW": "/LatinoAnalysis/NanoGardener/python/data/fake_prompt_rates/Full2017v9/mvaFall17V2Iso_WP90/",
            },
        },
    },
    "Full2016v9HIPM": {
        ## ------------
        "VetoObjWP": {
            "HLTsafe": {
                "cuts": {
                    # Common cuts
                    "True": ["False"],
                },
            },
        },
        # ------------
        "FakeObjWP": {
            "HLTsafe": {
                "cuts": {
                    # Common cuts
                    "True": [
                        'abs(electron_col[LF_idx]["eta"]) < 2.5',
                        'electron_col[LF_idx]["cutBased"] >= 3',
                        'electron_col[LF_idx]["convVeto"] == 1',
                    ],
                    # Barrel
                    'abs(electron_col[LF_idx]["eta"]) <= 1.479': [
                        'abs(electron_col[LF_idx]["dxy"]) < 0.05',
                        'abs(electron_col[LF_idx]["dz"]) < 0.1',
                    ],
                    # EndCap
                    'abs(electron_col[LF_idx]["eta"]) > 1.479': [
                        'electron_col[LF_idx]["sieie"] < 0.03 ',
                        'abs(electron_col[LF_idx]["eInvMinusPInv"]) < 0.014',
                        'abs(electron_col[LF_idx]["dxy"]) < 0.1',
                        'abs(electron_col[LF_idx]["dz"]) < 0.2',
                    ],
                },
            },
        },
        # ------------
        "TightObjWP": {
            # ----- mvaFall17V2Iso
            "mvaFall17V2Iso_WP90": {
                "cuts": {
                    # Common cuts
                    "True": [
                        'abs(electron_col[LF_idx]["eta"]) < 2.5',
                        'electron_col[LF_idx]["mvaFall17V2Iso_WP90"]',
                        'electron_col[LF_idx]["convVeto"] == 1',
                        'electron_col[LF_idx]["pfRelIso03_all"] < 0.06',
                    ],
                    # Barrel
                    'abs(electron_col[LF_idx]["eta"]) <= 1.479': [
                        'abs(electron_col[LF_idx]["dxy"]) < 0.05',
                        'abs(electron_col[LF_idx]["dz"]) < 0.1',
                    ],
                    # EndCap
                    'abs(electron_col[LF_idx]["eta"]) > 1.479': [
                        'abs(electron_col[LF_idx]["dxy"]) < 0.1',
                        'abs(electron_col[LF_idx]["dz"]) < 0.2',
                    ],
                },
                "tkSF": {
                    "1-3": "/cvmfs/cms.cern.ch/rsync/cms-nanoAOD/jsonpog-integration/POG/EGM/2016preVFP_UL/electron.json.gz"
                },
                "wpSF": {
                    "1-1": "LatinoAnalysis/NanoGardener/python/data/scale_factor/Full2016v9HIPM/egammaEffi_TightHWW_2016BCDE.txt",
                    "2-3": "LatinoAnalysis/NanoGardener/python/data/scale_factor/Full2016v9HIPM/egammaEffi_TightHWW_2016F.txt",
                },
                "fakeW": "/LatinoAnalysis/NanoGardener/python/data/fake_prompt_rates/Full2016v9HIPM/mvaFall17V2Iso_WP90/",
            },
        },
    },
    "Full2016v9noHIPM": {
        ## ------------
        "VetoObjWP": {
            "HLTsafe": {
                "cuts": {
                    # Common cuts
                    "True": ["False"],
                },
            },
        },
        # ------------
        "FakeObjWP": {
            "HLTsafe": {
                "cuts": {
                    # Common cuts
                    "True": [
                        'abs(electron_col[LF_idx]["eta"]) < 2.5',
                        'electron_col[LF_idx]["cutBased"] >= 3',
                        'electron_col[LF_idx]["convVeto"] == 1',
                    ],
                    # Barrel
                    'abs(electron_col[LF_idx]["eta"]) <= 1.479': [
                        'abs(electron_col[LF_idx]["dxy"]) < 0.05',
                        'abs(electron_col[LF_idx]["dz"]) < 0.1',
                    ],
                    # EndCap
                    'abs(electron_col[LF_idx]["eta"]) > 1.479': [
                        'electron_col[LF_idx]["sieie"] < 0.03 ',
                        'abs(electron_col[LF_idx]["eInvMinusPInv"]) < 0.014',
                        'abs(electron_col[LF_idx]["dxy"]) < 0.1',
                        'abs(electron_col[LF_idx]["dz"]) < 0.2',
                    ],
                },
            },
        },
        # ------------
        "TightObjWP": {
            # ----- mvaFall17V2Iso
            "mvaFall17V2Iso_WP90": {
                "cuts": {
                    # Common cuts
                    "True": [
                        'abs(electron_col[LF_idx]["eta"]) < 2.5',
                        'electron_col[LF_idx]["mvaFall17V2Iso_WP90"]',
                        'electron_col[LF_idx]["convVeto"] == 1',
                        'electron_col[LF_idx]["pfRelIso03_all"] < 0.06',
                    ],
                    # Barrel
                    'abs(electron_col[LF_idx]["eta"]) <= 1.479': [
                        'abs(electron_col[LF_idx]["dxy"]) < 0.05',
                        'abs(electron_col[LF_idx]["dz"]) < 0.1',
                    ],
                    # EndCap
                    'abs(electron_col[LF_idx]["eta"]) > 1.479': [
                        'abs(electron_col[LF_idx]["dxy"]) < 0.1',
                        'abs(electron_col[LF_idx]["dz"]) < 0.2',
                    ],
                },
                "tkSF": {
                    "4-7": "/cvmfs/cms.cern.ch/rsync/cms-nanoAOD/jsonpog-integration/POG/EGM/2016postVFP_UL/electron.json.gz"
                },
                "wpSF": {
                    "4-7": "LatinoAnalysis/NanoGardener/python/data/scale_factor/Full2016v9noHIPM/egammaEffi_TightHWW_2016.txt",
                },
                "fakeW": "/LatinoAnalysis/NanoGardener/python/data/fake_prompt_rates/Full2016v9noHIPM/mvaFall17V2Iso_WP90/",
            },
        },
    },
}


MuonWP = {
    "Full2018v9": {
        "VetoObjWP": {
            "HLTsafe": {
                "cuts": {
                    # Common cuts
                    "True": [
                        'abs(muon_col[LF_idx]["eta"]) < 2.4',
                        'muon_col[LF_idx]["pt"] > 10.0',
                    ]
                },
            }
        },
        # ------------
        "FakeObjWP": {
            "HLTsafe": {
                "cuts": {
                    # Common cuts
                    "True": [
                        'abs(muon_col[LF_idx]["eta"]) < 2.4',
                        'muon_col[LF_idx]["tightId"] == 1',
                        'abs(muon_col[LF_idx]["dz"]) < 0.1',
                        'muon_col[LF_idx]["pfRelIso04_all"] < 0.4',
                    ],
                    # dxy for pT < 20 GeV
                    'muon_col[LF_idx]["pt"] <= 20.0': [
                        'abs(muon_col[LF_idx]["dxy"]) < 0.01 ',
                    ],
                    # dxy for pT > 20 GeV
                    'muon_col[LF_idx]["pt"] > 20.0': [
                        'abs(muon_col[LF_idx]["dxy"]) < 0.02 ',
                    ],
                },
            },
        },
        # ------------
        "TightObjWP": {
            "cut_Tight_HWWW": {
                "cuts": {
                    # Common cuts
                    "True": [
                        'abs(muon_col[LF_idx]["eta"]) < 2.4',
                        'muon_col[LF_idx]["tightId"] == 1',
                        'abs(muon_col[LF_idx]["dz"]) < 0.1',
                        'muon_col[LF_idx]["pfRelIso04_all"] < 0.15',
                    ],
                    # dxy for pT < 20 GeV
                    'muon_col[LF_idx]["pt"] <= 20.0': [
                        'abs(muon_col[LF_idx]["dxy"]) < 0.01 ',
                    ],
                    # dxy for pT > 20 GeV
                    'muon_col[LF_idx]["pt"] > 20.0': [
                        'abs(muon_col[LF_idx]["dxy"]) < 0.02 ',
                    ],
                },
                "idSF": {
                    "1-1": [
                        "LatinoAnalysis/NanoGardener/python/data/scale_factor/Full2018v9/NUM_TightHWW_DEN_TrackerMuons_eta_pt.root"
                    ],
                },
                "isoSF": {
                    "1-1": [
                        "LatinoAnalysis/NanoGardener/python/data/scale_factor/Full2018v9/NUM_TightHWW_ISO_DEN_TightHWW_eta_pt.root"
                    ],
                },
                "fakeW": "/LatinoAnalysis/NanoGardener/python/data/fake_prompt_rates/Full2018v9/cut_Tight_HWWW/",
            },
        },
    },
    "Full2017v9": {
        ## ------------
        "VetoObjWP": {
            "HLTsafe": {
                "cuts": {
                    # Common cuts
                    "True": [
                        'abs(muon_col[LF_idx]["eta"]) < 2.4',
                        'muon_col[LF_idx]["pt"] > 10.0',
                    ]
                },
            }
        },
        # ------------
        "FakeObjWP": {
            "HLTsafe": {
                "cuts": {
                    # Common cuts
                    "True": [
                        'abs(muon_col[LF_idx]["eta"]) < 2.4',
                        'muon_col[LF_idx]["tightId"] == 1',
                        'abs(muon_col[LF_idx]["dz"]) < 0.1',
                        'muon_col[LF_idx]["pfRelIso04_all"] < 0.4',
                    ],
                    # dxy for pT < 20 GeV
                    'muon_col[LF_idx]["pt"] <= 20.0': [
                        'abs(muon_col[LF_idx]["dxy"]) < 0.01 ',
                    ],
                    # dxy for pT > 20 GeV
                    'muon_col[LF_idx]["pt"] > 20.0': [
                        'abs(muon_col[LF_idx]["dxy"]) < 0.02 ',
                    ],
                },
            },
        },
        # ------------
        "TightObjWP": {
            "cut_Tight_HWWW": {
                "cuts": {
                    # Common cuts
                    "True": [
                        'abs(muon_col[LF_idx]["eta"]) < 2.4',
                        'muon_col[LF_idx]["tightId"] == 1',
                        'abs(muon_col[LF_idx]["dz"]) < 0.1',
                        'muon_col[LF_idx]["pfRelIso04_all"] < 0.15',
                    ],
                    # dxy for pT < 20 GeV
                    'muon_col[LF_idx]["pt"] <= 20.0': [
                        'abs(muon_col[LF_idx]["dxy"]) < 0.01 ',
                    ],
                    # dxy for pT > 20 GeV
                    'muon_col[LF_idx]["pt"] > 20.0': [
                        'abs(muon_col[LF_idx]["dxy"]) < 0.02 ',
                    ],
                },
                # Negligible, POG recommended to set to 1.
                #'tkSF':  {
                #           '1-5' : 'LatinoAnalysis/NanoGardener/python/data/scale_factor/Full2017/muon_tracker_eff_Full2017.root' ,
                #         } ,
                #'tkSFerror': 0.01,
                "idSF": {
                    "1-5": [
                        "LatinoAnalysis/NanoGardener/python/data/scale_factor/Full2017v9/NUM_TightHWW_DEN_TrackerMuons_eta_pt.root"
                    ],
                },
                "isoSF": {
                    "1-5": [
                        "LatinoAnalysis/NanoGardener/python/data/scale_factor/Full2017v9/NUM_TightHWW_ISO_DEN_TightHWW_eta_pt.root"
                    ],
                },
                "fakeW": "/LatinoAnalysis/NanoGardener/python/data/fake_prompt_rates/Full2017v9/cut_Tight_HWWW/",
            },
        },
    },
    "Full2016v9HIPM": {
        ## ------------
        "VetoObjWP": {
            "HLTsafe": {
                "cuts": {
                    # Common cuts
                    "True": [
                        'abs(muon_col[LF_idx]["eta"]) < 2.4',
                        'muon_col[LF_idx]["pt"] > 10.0',
                    ]
                },
            }
        },
        # ------------
        "FakeObjWP": {
            "HLTsafe": {
                "cuts": {
                    # Common cuts
                    "True": [
                        'abs(muon_col[LF_idx]["eta"]) < 2.4',
                        'muon_col[LF_idx]["tightId"] == 1',
                        'abs(muon_col[LF_idx]["dz"]) < 0.1',
                        'muon_col[LF_idx]["pfRelIso04_all"] < 0.4',
                        #'muon_col[LF_idx]["trackIso"]/muon_col[LF_idx]["pt"] < 0.4' ,
                    ],
                    # dxy for pT < 20 GeV
                    'muon_col[LF_idx]["pt"] <= 20.0': [
                        'abs(muon_col[LF_idx]["dxy"]) < 0.01 ',
                    ],
                    # dxy for pT > 20 GeV
                    'muon_col[LF_idx]["pt"] > 20.0': [
                        'abs(muon_col[LF_idx]["dxy"]) < 0.02 ',
                    ],
                },
            },
        },
        # ------------
        "TightObjWP": {
            "cut_Tight80x": {
                "cuts": {
                    # Common cuts
                    "True": [
                        'abs(muon_col[LF_idx]["eta"]) < 2.4',
                        'muon_col[LF_idx]["tightId"] == 1',
                        'abs(muon_col[LF_idx]["dz"]) < 0.1',
                        'muon_col[LF_idx]["pfRelIso04_all"] < 0.15',
                        #'muon_col[LF_idx]["trackIso"]/muon_col[LF_idx]["pt"] < 0.4' ,
                    ],
                    # dxy for pT < 20 GeV
                    'muon_col[LF_idx]["pt"] <= 20.0': [
                        'abs(muon_col[LF_idx]["dxy"]) < 0.01 ',
                    ],
                    # dxy for pT > 20 GeV
                    'muon_col[LF_idx]["pt"] > 20.0': [
                        'abs(muon_col[LF_idx]["dxy"]) < 0.02 ',
                    ],
                },
                "idSF": {
                    "1-3": [
                        "LatinoAnalysis/NanoGardener/python/data/scale_factor/Full2016v9HIPM/NUM_TightHWW_DEN_TrackerMuons_eta_pt.root"
                    ],
                },
                "isoSF": {
                    "1-3": [
                        "LatinoAnalysis/NanoGardener/python/data/scale_factor/Full2016v9HIPM/NUM_TightHWW_ISO_DEN_TightHWW_eta_pt.root"
                    ],
                },
                "fakeW": "/LatinoAnalysis/NanoGardener/python/data/fake_prompt_rates/Full2016v9HIPM/cut_Tight80x/",
            },
        },
    },
    "Full2016v9noHIPM": {
        ## ------------
        "VetoObjWP": {
            "HLTsafe": {
                "cuts": {
                    # Common cuts
                    "True": [
                        'abs(muon_col[LF_idx]["eta"]) < 2.4',
                        'muon_col[LF_idx]["pt"] > 10.0',
                    ]
                },
            }
        },
        # ------------
        "FakeObjWP": {
            "HLTsafe": {
                "cuts": {
                    # Common cuts
                    "True": [
                        'abs(muon_col[LF_idx]["eta"]) < 2.4',
                        'muon_col[LF_idx]["tightId"] == 1',
                        'abs(muon_col[LF_idx]["dz"]) < 0.1',
                        'muon_col[LF_idx]["pfRelIso04_all"] < 0.4',
                        #'muon_col[LF_idx]["trackIso"]/muon_col[LF_idx]["pt"] < 0.4' ,
                    ],
                    # dxy for pT < 20 GeV
                    'muon_col[LF_idx]["pt"] <= 20.0': [
                        'abs(muon_col[LF_idx]["dxy"]) < 0.01 ',
                    ],
                    # dxy for pT > 20 GeV
                    'muon_col[LF_idx]["pt"] > 20.0': [
                        'abs(muon_col[LF_idx]["dxy"]) < 0.02 ',
                    ],
                },
            },
        },
        # ------------
        "TightObjWP": {
            "cut_Tight80x": {
                "cuts": {
                    # Common cuts
                    "True": [
                        'abs(muon_col[LF_idx]["eta"]) < 2.4',
                        'muon_col[LF_idx]["tightId"] == 1',
                        'abs(muon_col[LF_idx]["dz"]) < 0.1',
                        'muon_col[LF_idx]["pfRelIso04_all"] < 0.15',
                        #'muon_col[LF_idx]["trackIso"]/muon_col[LF_idx]["pt"] < 0.4' ,
                    ],
                    # dxy for pT < 20 GeV
                    'muon_col[LF_idx]["pt"] <= 20.0': [
                        'abs(muon_col[LF_idx]["dxy"]) < 0.01 ',
                    ],
                    # dxy for pT > 20 GeV
                    'muon_col[LF_idx]["pt"] > 20.0': [
                        'abs(muon_col[LF_idx]["dxy"]) < 0.02 ',
                    ],
                },
                "idSF": {
                    "4-7": [
                        "LatinoAnalysis/NanoGardener/python/data/scale_factor/Full2016v9noHIPM/NUM_TightHWW_DEN_TrackerMuons_eta_pt.root"
                    ],
                },
                "isoSF": {
                    "4-7": [
                        "LatinoAnalysis/NanoGardener/python/data/scale_factor/Full2016v9noHIPM/NUM_TightHWW_ISO_DEN_TightHWW_eta_pt.root"
                    ],
                },
                "fakeW": "/LatinoAnalysis/NanoGardener/python/data/fake_prompt_rates/Full2016v9noHIPM/cut_Tight80x/",
            },
        },
    },
}
