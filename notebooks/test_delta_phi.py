import awkward as ak
import numpy as np
import vector

vector.register_awkward()

#    if ( dphi > M_PI ) {
#    64                dphi -= 2.0*M_PI;
#    65             } else if ( dphi <= -M_PI ) {
#    66                dphi += 2.0*M_PI;
#    67             }
#    68             return dphi;


nevents = 100
rng = np.random.Generator(np.random.PCG64(31))
phi = rng.uniform(-2 * np.pi, 2 * np.pi, nevents)

phi_new = np.where(
    phi > np.pi,
    phi - 2 * np.pi,
    np.where(
        phi <= -np.pi,
        phi + 2 * np.pi,
        phi,
    ),
)
print(np.min(phi), np.max(phi), np.mean(phi))
print(np.min(phi_new), np.max(phi_new), np.mean(phi_new))

print(np.all((phi_new > -np.pi) & (phi_new < np.pi)))


v = ak.zip(
    {
        "pt": ak.zeros_like(phi),
        "eta": ak.zeros_like(phi),
        "phi": phi,
        "mass": ak.zeros_like(phi),
    },
    with_name="Momentum4D",
)

# print(v[0].deltaphi(v[1]))
combs = ak.combinations(v, 2, axis=0)
dphi = combs["0"].deltaphi(combs["1"])
print(ak.min(v.phi), ak.max(v.phi), ak.mean(v.phi))
print(ak.min(dphi), ak.max(dphi), ak.mean(dphi))
