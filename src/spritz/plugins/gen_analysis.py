import awkward as ak
import numpy as np
from spritz.modules.jet_sel import goodJet_func


def dnn_evaluator_gen(sess, events, dnn_t, dnn_cfg):
    scaler_path = dnn_cfg["scaler"]
    arr_type = eval(dnn_cfg["arrays_type"])
    with open(scaler_path) as file:
        scaler = file.read().split("\n")
        scaler = list(filter(lambda k: k != "", scaler))

    input1 = []
    for line in scaler:
        variable, mean, std = line.split(" ")
        mean = float(mean)
        std = float(std)

        arr = (events[f"Gen_{variable}"] - mean) / std
        arr = arr.to_numpy()
        arr = arr.astype(arr_type)
        input1.append(arr)

    input1 = np.array(input1)
    # input1 = input1.reshape(-1, 23)
    input1 = input1.T
    # arr = sess.run(["dense_6"], {"dense_input": input1})[0].reshape(-1)
    # arr = np.where(arr <= 0.0, 1e-6, arr)
    # arr = np.where(arr >= 1.0, 1 - 1e-6, arr)
    arr = sess.run([dnn_cfg["output_node"]], {"dense_input": input1})[0]
    arr = arr.flatten()
    arr = dnn_t(arr)

    arr = ak.Array(arr)

    events["Gen_dnn"] = arr

    # assert not ak.any(ak.is_none(events.dnn))
    return events


def cuts(events, onnx_session, dnn_t, dnn_cfg):
    events["GenLep"] = ak.pad_none(events.GenLep, 3, clip=True)
    events["GenJet"] = ak.pad_none(events.GenJet, 3, clip=False)

    events["Gen_mll"] = ak.fill_none(
        (events.GenLep[:, 0] + events.GenLep[:, 1]).mass, -10
    )
    events["Gen_ptll"] = ak.fill_none(
        (events.GenLep[:, 0] + events.GenLep[:, 1]).pt, -10
    )

    # events["Gen_dphill"] = ak.fill_none(
    #     events.GenLep[:, 0].deltaphi(events.GenLep[:, 1]), -10
    # )
    # events["Gen_dphijj"] = ak.fill_none(
    #     events.GenJet[:, 0].deltaphi(events.GenJet[:, 1]), -10
    # )

    events["Gen_dphill"] = np.abs(
        ak.fill_none(events.GenLep[:, 0].deltaphi(events.GenLep[:, 1]), -10)
    )
    events["Gen_dphijj"] = np.abs(
        ak.fill_none(events.GenJet[:, 0].deltaphi(events.GenJet[:, 1]), -10)
    )

    events["Gen_detall"] = np.abs(
        ak.fill_none(events.GenLep[:, 0].deltaeta(events.GenLep[:, 1]), -10)
    )

    events["Gen_detajj"] = np.abs(
        ak.fill_none(events.GenJet[:, 0].deltaeta(events.GenJet[:, 1]), -10)
    )

    events["Gen_mjj"] = ak.fill_none(
        (events.GenJet[:, 0] + events.GenJet[:, 1]).mass, -10
    )

    events["Gen_Zeppenfeld_Z"] = ak.fill_none(
        0.5
        * abs(
            (events.GenLep[:, 0].eta + events.GenLep[:, 1].eta)
            - (events.GenJet[:, 0].eta + events.GenJet[:, 1].eta)
        ),
        -9999.0,
    )

    events["Gen_MET"] = events.GenMET.pt

    events["Gen_ptjj"] = ak.fill_none(
        (events.GenJet[:, 0] + events.GenJet[:, 1]).pt, -10
    )

    events["Gen_ptj3"] = ak.fill_none(events.GenJet[:, 2].pt, -10)
    events["Gen_add_HT"] = ak.fill_none(ak.sum(events.GenJet[:, 2:], axis=1).pt, -10)

    events["Gen_ptl1"] = ak.fill_none((events.GenLep[:, 0]).pt, -10)
    events["Gen_ptl2"] = ak.fill_none((events.GenLep[:, 1]).pt, -10)

    events["Gen_etal1"] = ak.fill_none((events.GenLep[:, 0]).eta, -10)
    events["Gen_etal2"] = ak.fill_none((events.GenLep[:, 1]).eta, -10)

    events["Gen_phil1"] = ak.fill_none((events.GenLep[:, 0]).phi, -10)
    events["Gen_phil2"] = ak.fill_none((events.GenLep[:, 1]).phi, -10)

    events["Gen_ptj1"] = ak.fill_none((events.GenJet[:, 0]).pt, -10)
    events["Gen_ptj2"] = ak.fill_none((events.GenJet[:, 1]).pt, -10)

    events["Gen_etaj1"] = ak.fill_none((events.GenJet[:, 0]).eta, -10)
    events["Gen_etaj2"] = ak.fill_none((events.GenJet[:, 1]).eta, -10)

    events["Gen_phij1"] = ak.fill_none((events.GenJet[:, 0]).phi, -10)
    events["Gen_phij2"] = ak.fill_none((events.GenJet[:, 1]).phi, -10)

    # events = dnn_evaluator_gen(
    #     onnx_session,
    #     events,
    #     dnn_t,
    #     dnn_cfg,
    # )

    events["Gen_fiducial_cut"] = ak.fill_none((events.GenLep.pt[:, 1] > 10), False)
    events["Gen_fiducial_cut"] = events["Gen_fiducial_cut"] & ak.fill_none(
        events.GenLep[:, 2].pt < 10, True
    )
    events["Gen_fiducial_cut"] = events["Gen_fiducial_cut"] & ak.fill_none(
        events.GenJet[:, 1].pt > 50, False
    )
    events["Gen_fiducial_cut"] = events["Gen_fiducial_cut"] & ak.fill_none(
        abs(events.Gen_mll - 91.0) < 15, False
    )
    events["Gen_fiducial_cut"] = events["Gen_fiducial_cut"] & ak.fill_none(
        events.Gen_mjj > 200, False
    )

    # events["Gen_fiducial_cut"] = events["Gen_fiducial_cut"] & ak.fill_none(
    #     events.Gen_dnn > 0.9, False
    # )

    events["Gen_fiducial_cut"] = events["Gen_fiducial_cut"] & ak.fill_none(
        events.Gen_mjj > 1000, False
    )

    events["Gen_fiducial_cut"] = events["Gen_fiducial_cut"] & ak.fill_none(
        events.Gen_detajj > 3.0, False
    )

    # ee or mm
    events["Gen_fiducial_cut"] = events["Gen_fiducial_cut"] & ak.fill_none(
        ((events.GenLep.pdgId[:, 0] * events.GenLep.pdgId[:, 1]) == -11 * 11)
        | ((events.GenLep.pdgId[:, 0] * events.GenLep.pdgId[:, 1]) == -13 * 13),
        False,
    )

    return events


def genAnalysis(events, onnx_session, dnn_t, dnn_cfg):
    GenLep = events["GenDressedLepton"]
    GenLepMask = (
        # GenLep.isPrompt &
        (GenLep.pt > 10.0) & ((abs(GenLep.pdgId) == 11) | (abs(GenLep.pdgId) == 13))
    )
    events["GenLep"] = GenLep[GenLepMask]

    GenJet = events["GenJet"]
    mask = goodJet_func(GenJet, GenLep[:, :2], 0.3)
    mask = ak.values_astype(mask, bool, including_unknown=True)

    events["GenJet"] = GenJet[mask]

    events = cuts(events, onnx_session, dnn_t, dnn_cfg)

    return events
