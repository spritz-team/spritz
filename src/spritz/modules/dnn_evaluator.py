import awkward as ak
import numpy as np
import uproot
from scipy.interpolate import interp1d


def dnn_transform(cumulative_signal_path):
    fin = uproot.open(cumulative_signal_path)
    _x = fin["dnn_t"]["x"].array().to_numpy()
    _y = fin["dnn_t"]["y"].array().to_numpy()
    fin.close()

    dnn_t = interp1d(_x, _y)
    return dnn_t


def dnn_evaluator(sess, events, dnn_t, dnn_cfg):
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

        arr = (events[variable] - mean) / std
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

    events["dnn"] = arr

    # assert not ak.any(ak.is_none(events.dnn))
    return events
