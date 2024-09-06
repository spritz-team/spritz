import json

import uproot
from spritz.framework.framework import add_dict, get_fw_path, read_events

rootfile = "root://gaexrdoor.ciemat.es:1094//store/data/Run2016B/SingleElectron/NANOAOD/ver2_HIPM_UL2016_MiniAODv2_NanoAODv9-v2/2520000/7FB4E7BC-0D30-8C4D-9BF7-125CBAEAD12C.root"
era = "Full2016v9HIPM"


with open(f"{get_fw_path()}/data/common/forms.json", "r") as file:
    forms_common = json.load(file)
with open(f"{get_fw_path()}/data/{era}/forms.json", "r") as file:
    forms_era = json.load(file)
forms = add_dict(forms_common, forms_era)


forms = add_dict(forms_common, forms_era)

# events = read_events(rootfile, 0, 100, forms["data"])
# events.HLT.Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ

print(
    uproot.open(rootfile)["Events"][
        "HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ"
    ].array(entry_stop=100)
)
