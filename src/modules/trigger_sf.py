# import awkward as ak

# def get_LegEff(self, pt, eta, run_p, trig_name, isdata):
#     legEffs = self.TM_LegEffData[run_p][trig_name] if isdata else self.TM_LegEffMC[run_p][trig_name]
#     for eff_l in legEffs:
#         if len(eff_l) > 5:
#             if (eta >= float(eff_l[0]) and eta <= float(eff_l[1]) and         # the "=" in both directions is only used by the overflow bin
#                 pt  >= float(eff_l[2]) and pt  <= float(eff_l[3]) ) :         # in other cases the set is (min, max]

#                 eff = float(eff_l[4])
#                 eff_stat_u = min(1.0, float(eff_l[4]) + float(eff_l[6]))
#                 eff_stat_d = max(0.0, float(eff_l[4]) - float(eff_l[5]))
#                 eff_syst_u = min(1.0, float(eff_l[4]) + float(eff_l[8]))
#                 eff_syst_d = max(0.0, float(eff_l[4]) - float(eff_l[7]))

#                 eff_d = math.sqrt(eff_stat_d**2 + eff_syst_d**2)
#                 eff_u = math.sqrt(eff_stat_u**2 + eff_syst_u**2)

#                 return [eff, eff_d, eff_u, eff_stat_d, eff_stat_u, eff_syst_d, eff_syst_u]
#         elif len(eff_l) > 2:
#             raise IOError('Unexpected info in /LatinoAnalysis/NanoGardener/python/data/trigger/' + self.Trigger[self.cmssw][run_p]['LegEff'][trig_name] +\
#                         ': ' + eff_l + ' not enough inputs?')
#     return [0. , 0., 0.]

# def over_under(self, pdgId, pt, eta):
#     if abs(pdgId) == 11:
#         return max(self.el_minPt, min(self.el_maxPt, pt)), max(self.el_minEta, min(self.el_maxEta, eta))
#     elif abs(pdgId) == 13:
#         return max(self.mu_minPt, min(self.mu_maxPt, pt)), max(self.mu_minEta, min(self.mu_maxEta, eta))
#     else:
#         raise ValueError('_over_under can only operate on leptons, pdgI = ' + str(pdgId) + ', pt = ' + str(pt) + ', eta = ' + str(eta))

# def get_SF(self, eff_data, eff_mc):
#     return eff_data / eff_mc if eff_mc!=0. else 0.

# def get_SFUnc(self, eff_data, eff_mc):

#     eff_data_nom = eff_data[0]
#     # stat up and down should be the same, but let's propgate them as they are in the input files
#     eff_data_stat_d = eff_data[3]
#     eff_data_stat_u = eff_data[4]
#     eff_data_syst_d = eff_data[5]
#     eff_data_syst_u = eff_data[6]

#     eff_mc_nom = eff_mc[0]
#     # stat up and down should be the same, but let's propgate them as they are in the input files
#     eff_mc_stat_d = eff_mc[3]
#     eff_mc_stat_u = eff_mc[4]
#     eff_mc_syst_d = eff_mc[5]
#     eff_mc_syst_u = eff_mc[6]

#     if eff_mc_nom==0. or eff_data_nom==0.: return (0,0)

#     SF_stat_d = math.sqrt( (abs(eff_data_stat_d-eff_data_nom)/eff_data_nom)**2 + (abs(eff_mc_stat_d-eff_mc_nom)/eff_mc_nom)**2 )*eff_data_nom/eff_mc_nom
#     SF_stat_u = math.sqrt( (abs(eff_data_stat_u-eff_data_nom)/eff_data_nom)**2 + (abs(eff_mc_stat_u-eff_mc_nom)/eff_mc_nom)**2 )*eff_data_nom/eff_mc_nom

#     SF_syst_d = eff_data_syst_d/eff_mc_syst_d if eff_mc_syst_d!=0 else 0
#     SF_syst_u = eff_data_syst_u/eff_mc_syst_u if eff_mc_syst_u!=0 else 0

#     # return (down, up) uncertainties
#     return ( math.sqrt( SF_stat_d**2 + SF_syst_d**2 ),
#                 math.sqrt( SF_stat_u**2 + SF_syst_u**2 )
#             )

# def get_DRll_SF(run_p, trigName, drllIn):
#     DRll_SF = 1.
#     for val in self.TM_DRllSF[run_p][trigName] :
#         if drllIn >= float(val[0]) and drllIn < float(val[1]) :
#             DRll_SF = float(val[2])
#     return DRll_SF

# def get_DZEff(self,run_p,trigName,nvtxIn,pt1In,pt2In,isdata):
#     DZeffs = self.TM_DZEffData[run_p][trigName] if isdata else self.TM_DZEffMC[run_p][trigName]
#     DZeff = 1.
#     DZeff_err = 0.
#     nvtx = nvtxIn
#     pt1 = pt1In
#     pt2 = pt2In
#     if    DZeffs['type'] == 'value' :
#         DZeff      = DZeffs['vals'][0]
#         DZeff_err  = DZeffs['vals'][1]
#     elif  DZeffs['type'] == 'nvtx'  :
#     if nvtx >= 70 : nvtx = 69
#     for eff_dz in DZeffs['vals'] :
#         if nvtx >= float(eff_dz[0]) and nvtx < float(eff_dz[1]) :
#         DZeff     = float(eff_dz[2])
#         DZeff_err = float(eff_dz[3])
#     elif  DZeffs['type'] == 'pt1:pt2' :
#     if pt1 >= 100. : pt1 = 99.9
#     if pt2 >= 100. : pt2 = 99.9
#     for eff_dz in DZeffs['vals'] :
#         if pt1 >= float(eff_dz[0]) and pt1 < float(eff_dz[1]) and pt2 >= float(eff_dz[2]) and pt2 < float(eff_dz[3]) :
#         DZeff     = float(eff_dz[4])
#         DZeff_err = float(eff_dz[5])

#     #print run_p,trigName,nvtx,pt1,pt2,DZeff,DZeff_err,DZeff-DZeff_err,min(1.,DZeff+DZeff_err)
#     return DZeff,DZeff-DZeff_err,min(1.,DZeff+DZeff_err)

# def pair_eff(pdgId1, pt1, pdgId2, pt2, nvtx, run_p, drll):
#     """
#     Look op leg efficiencies and apply 5% sys for Electron and tracker SF for Muon
#     """

#     eff_gl = []
#     drll_sf = 1.0
#     # Leg_map = ['singA', 'singB', 'leadA', 'leadB', 'trailA', 'trailB']
#     # With A the lepton with the higer pt, B the one with the lower pt
#     # Lead is the tracked lepton and trail is the trailing
#     Leg_names = []
#     if abs(pdgId1) == 11 and abs(pdgId2) == 11:
#         Leg_names = [
#             "SingleEle",
#             "SingleEle",
#             "DoubleEleLegHigPt",
#             "DoubleEleLegHigPt",
#             "DoubleEleLegLowPt",
#             "DoubleEleLegLowPt",
#         ]
#         effData_dz_nom, effData_dz_do, effData_dz_up = get_DZEff(
#             run_p, "DoubleEle", nvtx, pt1, pt2, isdata=True
#         )
#         effMC_dz_nom, effMC_dz_do, effMC_dz_up = get_DZEff(
#             run_p, "DoubleEle", nvtx, pt1, pt2, isdata=False
#         )
#         if drll != None:
#             drll_sf = get_DRll_SF(run_p, "DoubleEle", drll)
#         eff_gl.append(self.TM_GlEff[run_p]["SingleEle"])
#         eff_gl.append(self.TM_GlEff[run_p]["SingleEle"])
#         eff_gl.append(self.TM_GlEff[run_p]["DoubleEle"])
#     elif abs(pdgId1) == 13 and abs(pdgId2) == 13:
#         Leg_names = [
#             "SingleMu",
#             "SingleMu",
#             "DoubleMuLegHigPt",
#             "DoubleMuLegHigPt",
#             "DoubleMuLegLowPt",
#             "DoubleMuLegLowPt",
#         ]
#         effData_dz_nom, effData_dz_do, effData_dz_up = self._get_DZEff(
#             run_p, "DoubleMu", nvtx, pt1, pt2, isdata=True
#         )
#         effMC_dz_nom, effMC_dz_do, effMC_dz_up = self._get_DZEff(
#             run_p, "DoubleMu", nvtx, pt1, pt2, isdata=False
#         )
#         if drll != None:
#             drll_sf = get_DRll_SF(run_p, "DoubleMu", drll)
#         eff_gl.append(self.TM_GlEff[run_p]["SingleMu"])
#         eff_gl.append(self.TM_GlEff[run_p]["SingleMu"])
#         eff_gl.append(self.TM_GlEff[run_p]["DoubleMu"])
#     elif abs(pdgId1) == 11 and abs(pdgId2) == 13:
#         Leg_names = [
#             "SingleEle",
#             "SingleMu",
#             "EleMuLegHigPt",
#             "MuEleLegHigPt",
#             "MuEleLegLowPt",
#             "EleMuLegLowPt",
#         ]
#         effData_dz_nom, effData_dz_do, effData_dz_up = self._get_DZEff(
#             run_p, "EleMu", nvtx, pt1, pt2, isdata=True
#         )
#         effMC_dz_nom, effMC_dz_do, effMC_dz_up = self._get_DZEff(
#             run_p, "EleMu", nvtx, pt1, pt2, isdata=False
#         )
#         if drll != None:
#             drll_sf = get_DRll_SF(run_p, "EleMu", drll)
#         eff_gl.append(self.TM_GlEff[run_p]["SingleEle"])
#         eff_gl.append(self.TM_GlEff[run_p]["SingleMu"])
#         eff_gl.append(self.TM_GlEff[run_p]["EleMu"])
#     else:
#         Leg_names = [
#             "SingleMu",
#             "SingleEle",
#             "MuEleLegHigPt",
#             "EleMuLegHigPt",
#             "EleMuLegLowPt",
#             "MuEleLegLowPt",
#         ]
#         effData_dz_nom, effData_dz_do, effData_dz_up = self._get_DZEff(
#             run_p, "MuEle", nvtx, pt1, pt2, isdata=True
#         )
#         effMC_dz_nom, effMC_dz_do, effMC_dz_up = self._get_DZEff(
#             run_p, "MuEle", nvtx, pt1, pt2, isdata=False
#         )
#         if drll != None:
#             drll_sf = get_DRll_SF(run_p, "MuEle", drll)
#         eff_gl.append(self.TM_GlEff[run_p]["SingleMu"])
#         eff_gl.append(self.TM_GlEff[run_p]["SingleEle"])
#         eff_gl.append(self.TM_GlEff[run_p]["MuEle"])

#     effData_dz = []
#     effData_dz.append(effData_dz_nom)
#     effData_dz.append(effData_dz_do)  # tot do
#     effData_dz.append(effData_dz_up)  # tot up
#     # In the following we append the same content of the previous 2 lines, it is just a trick to handle stat and syst components later on
#     effData_dz.append(effData_dz_do)  # stat do
#     effData_dz.append(effData_dz_up)  # stat uo
#     effData_dz.append(
#         effData_dz_nom
#     )  # syst do -> set to nom to avoid double counting when computing the tot SF uncertainty
#     effData_dz.append(
#         effData_dz_nom
#     )  # syst up -> set to nom to avoid double counting when computing the tot SF uncertainty

#     effMC_dz = []
#     effMC_dz.append(effMC_dz_nom)
#     effMC_dz.append(effMC_dz_do)  # tot do
#     effMC_dz.append(effMC_dz_up)  # tot up
#     # In the following we append the same content of the previous 2 lines, it is just a trick to handle stat and syst components later on
#     effMC_dz.append(effMC_dz_do)  # stat do
#     effMC_dz.append(effMC_dz_up)  # stat uo
#     effMC_dz.append(
#         effMC_dz_nom
#     )  # syst do -> set to nom to avoid double counting when computing the tot SF uncertainty
#     effMC_dz.append(
#         effMC_dz_nom
#     )  # syst up -> set to nom to avoid double counting when computing the tot SF uncertainty

#     # eff_map = ['singA', 'singB', 'leadA', 'leadB', 'trailA', 'trailB']
#     effData = []
#     effMC = []
#     for iLeg in range(len(Leg_names)):
#         isdata = True
#         effData.append(
#             get_LegEff(
#                 eval("pt" + str(iLeg % 2 + 1)),
#                 eval("eta" + str(iLeg % 2 + 1)),
#                 run_p,
#                 Leg_names[iLeg],
#                 isdata,
#             )
#         )
#         isdata = False
#         effMC.append(
#             get_LegEff(
#                 eval("pt" + str(iLeg % 2 + 1)),
#                 eval("eta" + str(iLeg % 2 + 1)),
#                 run_p,
#                 Leg_names[iLeg],
#                 isdata,
#             )
#         )

#         # Muon tracker SF
#         # if abs(pdgId1) == 13 and not iLeg%2:
#         #   eff[iLeg] = [a*b for a,b in zip(eff[iLeg], self.TM_trkSFMu[run_p])]
#         # if abs(pdgId2) == 13 and iLeg%2:
#         #   eff[iLeg] = [a*b for a,b in zip(eff[iLeg], self.TM_trkSFMu[run_p])]
#     if drll != None:
#         return effData, effMC, effData_dz, effMC_dz, eff_gl, drll_sf
#     else:
#         return effData, effMC, effData_dz, effMC_dz, eff_gl

#     return


# def get_w(
#     pdgId1, pt1, eta1, pdgId2, pt2, eta2, drll, nvtx, run_p
# ):

#     pt1, eta1 = over_under(pdgId1, pt1, eta1)
#     pt2, eta2 = over_under(pdgId2, pt2, eta2)

#     effData, effMC, effData_dz, effMC_dz, eff_gl, DRll_SF = pair_eff(
#         pdgId1, pt1, pdgId2, pt2, nvtx, run_p, drll
#     )
#     # eff_map = ['SingleEle', 'SingleMu', 'EleMuLegHigPt', 'MuEleLegHigPt', 'MuEleLegLowPt', 'EleMuLegLowPt']

#     # nom, tot_d, tot_u, stat_d, stat_u, syst_d, syst_u
#     effData_dbl = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
#     effData_sgl = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
#     effData_evt = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
#     effMC_dbl = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
#     effMC_sgl = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
#     effMC_evt = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
#     # SFnom, SF_d, SF_u
#     SF_evt = [0.0, 0.0, 0.0]

#     for i in range(7):
#         effData_dbl[i] = max(
#             (
#                 effData[4][i] * effData[3][i]
#                 + effData[2][i] * effData[5][i]
#                 - effData[3][i] * effData[2][i]
#             )
#             * eff_gl[2][i]
#             * effData_dz[i],
#             0.0001,
#         )
#         effData_sgl[i] = (
#             effData[0][i] * eff_gl[0][i]
#             + effData[1][i] * eff_gl[1][i]
#             - effData[0][i] * effData[1][i] * eff_gl[0][i] * eff_gl[1][i]
#         )
#         effData_evt[i] = (
#             effData_dbl[i]
#             + effData_sgl[i]
#             - effData[5][i] * eff_gl[2][i] * effData[0][i] * eff_gl[0][i]
#             - effData[4][i]
#             * eff_gl[2][i]
#             * effData[1][i]
#             * eff_gl[1][i]
#             * (
#                 1
#                 - effData[5][i]
#                 * eff_gl[2][i]
#                 * effData[0][i]
#                 * eff_gl[0][i]
#                 / effData_dbl[i]
#             )
#         ) * DRll_SF

#         effMC_dbl[i] = max(
#             (
#                 effMC[4][i] * effMC[3][i]
#                 + effMC[2][i] * effMC[5][i]
#                 - effMC[3][i] * effMC[2][i]
#             )
#             * eff_gl[2][i]
#             * effMC_dz[i],
#             0.0001,
#         )
#         effMC_sgl[i] = (
#             effMC[0][i] * eff_gl[0][i]
#             + effMC[1][i] * eff_gl[1][i]
#             - effMC[0][i] * effMC[1][i] * eff_gl[0][i] * eff_gl[1][i]
#         )
#         effMC_evt[i] = (
#             effMC_dbl[i]
#             + effMC_sgl[i]
#             - effMC[5][i] * eff_gl[2][i] * effMC[0][i] * eff_gl[0][i]
#             - effMC[4][i]
#             * eff_gl[2][i]
#             * effMC[1][i]
#             * eff_gl[1][i]
#             * (
#                 1
#                 - effMC[5][i] * eff_gl[2][i] * effMC[0][i] * eff_gl[0][i] / effMC_dbl[i]
#             )
#         ) * DRll_SF

#     SF_evt[0] = get_SF(effData_evt[0], effMC_evt[0])
#     SF_evt[1] = get_SFUnc(effData_evt, effMC_evt)[0]
#     SF_evt[2] = get_SFUnc(effData_evt, effMC_evt)[1]
#     return SF_evt


def trigger_sf(events, variations, cfg):
    # events_trigger = ak.mask(events, ak.num(events.Lepton)>=2)
    return events, variations
