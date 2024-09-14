#!/bin/bash

cd ~/eft-smp-combination/CMSSW_14_1_0_pre4/src/; cmsenv; cd -

#combineCards.py ../datacards/sr_inc_ee/dnn/datacard.txt ../datacards/dypu_cr_ee/mjj/datacard.txt > comb_card.txt
combineCards.py ../datacards/sr_inc_ee/dnn_mjj/datacard.txt ../datacards/dypu_cr_ee/dnn_mjj/datacard.txt > comb_card.txt
#text2workspace.py comb_card.txt -o combined.root

#combine -M FitDiagnostics --X-rtd MINIMIZER_analytic --cminDefaultMinimizerStrategy 0 -m 125 -d combined.root --setParameterRanges CMS_DY_hard_norm=0.2,2.0:CMS_DY_PU_norm=0.2,2.0 --setParameters r=1 -v 3 -t -1 --toysFreq

text2workspace.py comb_card.txt -o combined.root -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel --PO map='.*\/Zjj_mjj_0':r_0[1,-1,20] --PO map='.*\/Zjj_mjj_1':r_1[1,-1,20] --PO map='.*\/Zjj_mjj_2':r_2[1,-1,20] --PO map='.*\/Zjj_mjj_3':r_3[1,-1,20]
combine -M MultiDimFit --algo singles --X-rtd MINIMIZER_analytic --cminDefaultMinimizerStrategy 0 -m 125 -d combined.root --floatOtherPOIs 1 --setParameterRanges CMS_DY_hard_norm=0.2,2.0:CMS_DY_PU_norm=0.2,2.0 --setParameters r_0=1,r_1=1,r_2=1,r_3=1 -v 3 -t -1 --toysFreq
