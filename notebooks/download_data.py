import json
import os
import subprocess
from copy import deepcopy

import requests

config_eras = {
    "Full2018v9": {
        "SamplesData": "Run2018_UL2018_nAODv9",
        "SamplesMC": "Summer20UL18_106x_nAODv9",
    },
    "Full2017v9": {
        "SamplesData": "Run2017_UL2017_nAODv9",
        "SamplesMC": "Summer20UL17_106x_nAODv9",
    },
    "Full2016v9noHIPM": {
        "SamplesData": "Run2016_UL2016_noHIPM_nAODv9",
        "SamplesMC": "Summer20UL16_106x_noHIPM_nAODv9",
    },
    "Full2016v9HIPM": {
        "SamplesData": "Run2016_UL2016_HIPM_nAODv9",
        "SamplesMC": "Summer20UL16_106x_HIPM_nAODv9",
    },
}


jsonpog_path = "/Users/giorgiopizzati/Downloads/jsonpog-integration-master/POG/"
jsonpog_path = "/cvmfs/cms.cern.ch/rsync/cms-nanoAOD/jsonpog-integration/POG/"


for ERA in config_eras:
    basedir = f"../data/{ERA}/samples/"
    # if "2018" in ERA:
    #     continue

    def setup_cfg():
        # Setup all the needed data

        year_maps = {
            "Full2016v9HIPM": "2016",
            "Full2016v9noHIPM": "2016",
            "Full2017v9": "2017",
            "Full2018v9": "2018",
        }
        cfg = {
            "flags": [
                "goodVertices",
                "globalSuperTightHalo2016Filter",
                "HBHENoiseFilter",
                "HBHENoiseIsoFilter",
                "EcalDeadCellTriggerPrimitiveFilter",
                "BadPFMuonFilter",
                "BadPFMuonDzFilter",
                "ecalBadCalibFilter",
                "eeBadScFilter",
            ],
            "eleWP": "mvaFall17V2Iso_WP90",
            "muWP": "cut_Tight_HWWW",
            "leptonSF": f"RPLME_PATH_FW/data/{ERA}/clib/lepton_sf.json.gz",
            "puWeightsKey": f"Collisions{int(year_maps[ERA])-2000}_UltraLegacy_goldenJSON",
            "run_to_era": f"RPLME_PATH_FW/data/{ERA}/clib/run_to_era.json.gz",
            "do_theory_variations": False,
            "era": ERA,
        }
        cfg["year"] = year_maps[ERA]

        cfg["jet_sel"] = {
            "jetId": 2,
            "minpt": 15,
            "maxeta": 4.7,
        }

        leptons_wp = {
            "Full2016v9HIPM": {
                "eleWP": "mvaFall17V2Iso_WP90",
                "muWP": "cut_Tight80x",
            },
            "Full2016v9noHIPM": {
                "eleWP": "mvaFall17V2Iso_WP90",
                "muWP": "cut_Tight80x",
            },
            "Full2017v9": {
                "eleWP": "mvaFall17V2Iso_WP90",
                "muWP": "cut_Tight_HWWW",
            },
            "Full2018v9": {
                "eleWP": "mvaFall17V2Iso_WP90",
                "muWP": "cut_Tight_HWWW",
            },
        }
        cfg["leptonsWP"] = leptons_wp[ERA]

        btag_wps = {
            "Full2016v9HIPM": {
                "btagLoose": 0.0508,
                "btagMedium": 0.2598,
                "btagTight": 0.6502,
            },
            "Full2016v9noHIPM": {
                "btagLoose": 0.0480,
                "btagMedium": 0.2489,
                "btagTight": 0.6377,
            },
            "Full2017v9": {
                "btagLoose": 0.0532,
                "btagMedium": 0.3040,
                "btagTight": 0.7476,
            },
            "Full2018v9": {
                "btagLoose": 0.0490,
                "btagMedium": 0.2783,
                "btagTight": 0.7100,
            },
        }
        cfg["bTag"] = btag_wps[ERA]

        jme = {
            "Full2018v9": {
                "lvl_compound": "L1L2L3Res",
                "jet_algo": "AK4PFchs",
                "jer_tag": "Summer19UL18_JRV2_MC",
                "jec_tag": {
                    "mc": "Summer19UL18_V5_MC",
                    "data": {
                        "UL2018A": "Summer19UL18_RunA_V5_DATA",
                        "UL2018B": "Summer19UL18_RunB_V5_DATA",
                        "UL2018C": "Summer19UL18_RunC_V5_DATA",
                        "UL2018D": "Summer19UL18_RunD_V5_DATA",
                    },
                },
                "jes": [
                    "Absolute",
                    "Absolute_2018",
                    "BBEC1",
                    "BBEC1_2018",
                    "EC2",
                    "EC2_2018",
                    "FlavorQCD",
                    "HF",
                    "HF_2018",
                    "RelativeBal",
                    "RelativeSample_2018",
                ],
            },
            "Full2017v9": {
                "lvl_compound": "L1L2L3Res",
                "jet_algo": "AK4PFchs",
                "jer_tag": "Summer19UL17_JRV2_MC",
                "jec_tag": {
                    "mc": "Summer19UL17_V5_MC",
                    "data": {
                        "UL2017B": "Summer19UL17_RunB_V5_DATA",
                        "UL2017C": "Summer19UL17_RunC_V5_DATA",
                        "UL2017D": "Summer19UL17_RunD_V5_DATA",
                        "UL2017E": "Summer19UL17_RunE_V5_DATA",
                        "UL2017F": "Summer19UL17_RunF_V5_DATA",
                    },
                },
                "jes": [
                    "Absolute",
                    "Absolute_2017",
                    "BBEC1",
                    "BBEC1_2017",
                    "EC2",
                    "EC2_2017",
                    "FlavorQCD",
                    "HF",
                    "HF_2017",
                    "RelativeBal",
                    "RelativeSample_2017",
                ],
            },
            "Full2016v9noHIPM": {
                "lvl_compound": "L1L2L3Res",
                "jet_algo": "AK4PFchs",
                "jer_tag": "Summer20UL16_JRV3_MC",
                "jec_tag": {
                    "mc": "Summer19UL16_V7_MC",
                    "data": {
                        "UL2016F": "Summer19UL16_RunFGH_V7_DATA",
                        "UL2016G": "Summer19UL16_RunFGH_V7_DATA",
                        "UL2016H": "Summer19UL16_RunFGH_V7_DATA",
                    },
                },
                "jes": [
                    "Absolute",
                    "Absolute_2016",
                    "BBEC1",
                    "BBEC1_2016",
                    "EC2",
                    "EC2_2016",
                    "FlavorQCD",
                    "HF",
                    "HF_2016",
                    "RelativeBal",
                    "RelativeSample_2016",
                ],
            },
            "Full2016v9HIPM": {
                "lvl_compound": "L1L2L3Res",
                "jet_algo": "AK4PFchs",
                "jer_tag": "Summer20UL16APV_JRV3_MC",
                "jec_tag": {
                    "mc": "Summer19UL16APV_V7_MC",
                    "data": {
                        "UL2016_preVFPB": "Summer19UL16APV_RunBCD_V7_DATA",
                        "UL2016_preVFPC": "Summer19UL16APV_RunBCD_V7_DATA",
                        "UL2016_preVFPD": "Summer19UL16APV_RunBCD_V7_DATA",
                        "UL2016_preVFPE": "Summer19UL16APV_RunEF_V7_DATA",
                        "UL2016_preVFPF": "Summer19UL16APV_RunEF_V7_DATA",
                    },
                },
                "jes": [
                    "Absolute",
                    "Absolute_2016",
                    "BBEC1",
                    "BBEC1_2016",
                    "EC2",
                    "EC2_2016",
                    "FlavorQCD",
                    "HF",
                    "HF_2016",
                    "RelativeBal",
                    "RelativeSample_2016",
                ],
            },
        }
        cfg["jme"] = jme[ERA]

        # basedir = os.path.abspath(".") + "/data/2018/jme/"
        # os.makedirs(basedir, exist_ok=True)

        # jet_object = "AK4PFchs"
        # production_jec = "Summer19UL18_V5_MC"
        # production_jer = "Summer19UL18_JRV2_MC"
        # base_url_jec = (
        #     "https://raw.githubusercontent.com/cms-jet/JECDatabase/master/textFiles/"
        # )
        # base_url_jer = (
        #     "https://raw.githubusercontent.com/cms-jet/JRDatabase/master/textFiles/"
        # )

        # files = ["L1FastJet", "L2Relative", "L3Absolute", "L2L3Residual"]
        # files = [production_jec + "_" + file + "_" + jet_object for file in files] + [
        #     f"Regrouped_{production_jec}_UncertaintySources" + "_" + jet_object
        # ]
        # postfixes = 4 * ["jec"] + ["junc"]
        # urls = [base_url_jec + production_jec + "/" + file + ".txt" for file in files]

        # files_jer = [
        #     production_jer + "_PtResolution_" + jet_object,
        #     production_jer + "_SF_" + jet_object,
        # ]
        # postfixes += ["jr", "jrsf"]
        # urls += [
        #     base_url_jer + production_jer + "/" + file + ".txt" for file in files_jer
        # ]
        # files += files_jer
        # print(files)

        # print(urls)

        # paths = []
        # jec_names = []
        # junc = 0
        # for file, url, postfix in zip(files, urls, postfixes):
        #     new_filename = f"{file}.{postfix}.txt"
        #     if postfix == "junc":
        #         junc = file
        #     # print(url)

        #     with open(basedir + new_filename, "w") as f:
        #         f.write(requests.get(url).text)
        #     paths.append(basedir + new_filename)
        #     jec_names.append(file)

        # print(paths)
        # print(jec_names)
        # print(junc)
        # print("\n\n")
        # jme = {"jec_stack_names": jec_names, "jec_stack_paths": paths, "junc": junc}

        # cfg["JME"] = jme
        year_maps = {
            "Full2016v9HIPM": "2016preVFP_UL",
            "Full2016v9noHIPM": "2016postVFP_UL",
            "Full2017v9": "2017_UL",
            "Full2018v9": "2018_UL",
        }

        files_to_copy = [
            "/cvmfs/cms.cern.ch/rsync/cms-nanoAOD/jsonpog-integration/POG/JME/jer_smear.json.gz",
            f"/cvmfs/cms.cern.ch/rsync/cms-nanoAOD/jsonpog-integration/POG/JME/{year_maps[ERA]}/jet_jerc.json.gz",
            f"/cvmfs/cms.cern.ch/rsync/cms-nanoAOD/jsonpog-integration/POG/JME/{year_maps[ERA]}/jmar.json.gz",
            f"/cvmfs/cms.cern.ch/rsync/cms-nanoAOD/jsonpog-integration/POG/BTV/{year_maps[ERA]}/btagging.json.gz",
            f"/cvmfs/cms.cern.ch/rsync/cms-nanoAOD/jsonpog-integration/POG/LUM/{year_maps[ERA]}/puWeights.json.gz",
        ]
        files_to_copy = list(
            map(lambda k: jsonpog_path + k.split("POG")[-1], files_to_copy)
        )
        keys = ["jer_smear", "jet_jerc", "puidSF", "btagSF", "puWeights"]

        basedir = f"../data/{ERA}/clib/"
        os.makedirs(basedir, exist_ok=True)

        for key, file_to_copy in zip(keys, files_to_copy):
            # for file_to_copy in files_to_copy:
            fname = file_to_copy.split("/")[-1]
            cfg[key] = f"RPLME_PATH_FW/data/{ERA}/clib/{fname}"
            proc = subprocess.Popen(f"cp {file_to_copy} {basedir}", shell=True)
            proc.wait()

        files_to_download = {
            "Full2016v9noHIPM": "https://cms-service-dqmdc.web.cern.ch/CAF/certification/Collisions16/13TeV/Legacy_2016/Cert_271036-284044_13TeV_Legacy2016_Collisions16_JSON.txt",
            "Full2016v9HIPM": "https://cms-service-dqmdc.web.cern.ch/CAF/certification/Collisions16/13TeV/Legacy_2016/Cert_271036-284044_13TeV_Legacy2016_Collisions16_JSON.txt",
            "Full2017v9": "https://cms-service-dqmdc.web.cern.ch/CAF/certification/Collisions17/13TeV/Legacy_2017/Cert_294927-306462_13TeV_UL2017_Collisions17_GoldenJSON.txt",
            "Full2018v9": "https://cms-service-dqmdc.web.cern.ch/CAF/certification/Collisions18/13TeV/Legacy_2018/Cert_314472-325175_13TeV_Legacy2018_Collisions18_JSON.txt",
        }
        keys = ["lumiMask"]

        basedir = f"../data/{ERA}/lumimask/"
        os.makedirs(basedir, exist_ok=True)

        for key, file_to_download in zip(keys, [files_to_download[ERA]]):
            fname = basedir + file_to_download.split("/")[-1]
            cfg[key] = f"RPLME_PATH_FW/data/{ERA}/lumimask/" + fname.split("/")[-1]
            with open(fname, "wb") as file:
                file.write(requests.get(file_to_download).content)

        files_to_download = {
            "Full2016v9HIPM": "https://github.com/latinos/LatinoAnalysis/raw/UL_production/NanoGardener/python/data/RoccoR2016aUL.txt",
            "Full2016v9noHIPM": "https://github.com/latinos/LatinoAnalysis/raw/UL_production/NanoGardener/python/data/RoccoR2016bUL.txt",
            "Full2017v9": "https://github.com/latinos/LatinoAnalysis/raw/UL_production/NanoGardener/python/data/RoccoR2017UL.txt",
            "Full2018v9": "https://github.com/latinos/LatinoAnalysis/raw/UL_production/NanoGardener/python/data/RoccoR2018UL.txt",
        }
        keys = ["rochester_file"]

        basedir = f"../data/{ERA}/rochester/"
        os.makedirs(basedir, exist_ok=True)

        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"
        }
        for key, file_to_download in zip(keys, [files_to_download[ERA]]):
            fname = basedir + file_to_download.split("/")[-1]
            cfg[key] = f"RPLME_PATH_FW/data/{ERA}/rochester/" + fname.split("/")[-1]
            with open(fname, "wb") as file:
                file.write(requests.get(file_to_download, headers=headers).content)

        print(json.dumps(cfg, indent=2))

        with open(f"../data/{ERA}/cfg.json", "w") as file:
            json.dump(cfg, file, indent=2)

    def download_latinos_samples():
        files_to_download = [
            "https://github.com/latinos/LatinoAnalysis/raw/UL_production/NanoGardener/python/framework/samples/samplesCrossSections_UL.py",
            f"https://github.com/latinos/LatinoAnalysis/raw/UL_production/NanoGardener/python/framework/samples/{config_eras[ERA]['SamplesData']}.py",
            f"https://github.com/latinos/LatinoAnalysis/raw/UL_production/NanoGardener/python/framework/samples/{config_eras[ERA]['SamplesMC']}.py",
        ]

        # files_to_download = [
        #     "https://github.com/latinos/LatinoAnalysis/raw/UL_production/NanoGardener/python/framework/samples/samplesCrossSections_UL.py",
        #     "https://github.com/latinos/LatinoAnalysis/raw/UL_production/NanoGardener/python/framework/samples/Run2018_UL2018_nAODv9.py",
        #     "https://github.com/latinos/LatinoAnalysis/raw/UL_production/NanoGardener/python/framework/samples/Summer20UL18_106x_nAODv9.py",
        # ]

        _basedir = basedir + "/samples_latinos/"
        os.makedirs(_basedir, exist_ok=True)

        for file_to_download in files_to_download:
            fname = _basedir + file_to_download.split("/")[-1]
            with open(fname, "wb") as file:
                file.write(requests.get(file_to_download).content)

    def convert_latinos_samples():
        _basedir = basedir + "/samples_latinos/"

        Samples = {}
        exec(
            f"from data.{ERA}.samples.samples_latinos.{config_eras[ERA]['SamplesData']} import Samples as SamplesData",
            globals(),
            globals(),
        )

        for sample in SamplesData:
            Samples[sample] = deepcopy(SamplesData[sample])

        # from data.samples_latinos.Summer20UL18_106x_nAODv9 import Samples as SamplesMC
        exec(
            f"from data.{ERA}.samples.samples_latinos.{config_eras[ERA]['SamplesMC']} import Samples as SamplesMC",
            globals(),
            globals(),
        )

        for sample in SamplesMC:
            if "AToZHT" in sample:
                continue
            Samples[sample] = deepcopy(SamplesMC[sample])

        print(Samples)

        fname = _basedir + "samplesCrossSections_UL.py"
        with open(fname) as file:
            txt = file.read()

        samples = {}
        lines = []
        headers = []
        for line in txt.split("\n"):
            if "samples[" in line:
                line = line.replace(".extend(", "=")
                line = line.replace(")", "")
                lines.append(line)
            elif line.startswith("#"):
                headers.append(line.replace("\t", " " * 7))

        d = {"samples": samples}
        exec("\n".join(lines), d)
        for sample in samples:
            if sample not in Samples:
                continue
            for string in samples[sample]:
                k, v = string.split("=")
                Samples[sample][k] = v
        print(Samples)

        _basedir = basedir + ""

        try:
            with open(_basedir + "samples_priv.json") as file:
                Samples_priv = json.load(file)
            Samples.update(Samples_priv)
        except Exception as e:
            print("No private samples!\n", e)

        os.makedirs(_basedir, exist_ok=True)
        with open(_basedir + "samples.json", "w") as file:
            json.dump({"headers": headers, "samples": Samples}, file, indent=2)

    download_latinos_samples()
    convert_latinos_samples()
    subprocess.Popen(f"rm -r {basedir}/samples_latinos/", shell=True)
    setup_cfg()
