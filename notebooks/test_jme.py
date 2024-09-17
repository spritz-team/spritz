import json

import correctionlib
from spritz.framework.framework import get_fw_path

cfg = {
    "jme": {
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
    "jer_smear": "RPLME_PATH_FW/data/Full2018v9/clib/jer_smear.json.gz",
    "jet_jerc": "RPLME_PATH_FW/data/Full2018v9/clib/jet_jerc.json.gz",
}

cfg = json.loads(json.dumps(cfg).replace("RPLME_PATH_FW", get_fw_path()))

cset_jerc = correctionlib.CorrectionSet.from_file(cfg["jet_jerc"])
cset_jersmear = correctionlib.CorrectionSet.from_file(cfg["jer_smear"])
jme_cfg = cfg["jme"]

jec_tag = jme_cfg["jec_tag"]["mc"]
key = "{}_{}_{}".format(jec_tag, jme_cfg["lvl_compound"], jme_cfg["jet_algo"])
cset_jec = cset_jerc.compound[key]

jer_tag = jme_cfg["jer_tag"]
key = "{}_{}_{}".format(jer_tag, "ScaleFactor", jme_cfg["jet_algo"])
cset_jer = cset_jerc[key]

key = "{}_{}_{}".format(jer_tag, "PtResolution", jme_cfg["jet_algo"])
cset_jer_ptres = cset_jerc[key]

key = "JERSmear"
cset_jersmear = cset_jersmear[key]

# events_jme = ak.copy(events)

cset_jer.evaluate()
