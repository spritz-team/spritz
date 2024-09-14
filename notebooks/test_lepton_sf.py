import awkward as ak
import numpy as np

rng = np.random.Generator(np.random.PCG64(31))

nmu = rng.integers(0, 5, 100)
print(nmu)
nmu_tot = np.sum(nmu)
print("total mu:", nmu_tot)
mu_pt = rng.normal(30, 2, nmu_tot)
mu_pt = ak.unflatten(mu_pt, nmu)
print("mu_pt:", mu_pt)

nele = rng.integers(0, 5, 100)
print(nele)
nele_tot = np.sum(nele)
print("total ele:", nele_tot)
ele_pt = rng.normal(30, 2, nele_tot)
ele_pt = ak.unflatten(ele_pt, nele)
print("ele_pt:", ele_pt)

mu_none = ak.mask(mu_pt, ak.is_none(mu_pt, axis=1))
ele_none = ak.mask(ele_pt, ak.is_none(ele_pt, axis=1))

lep_pdgId = ak.concatenate(
    [11 * ak.ones_like(ele_pt), 13 * ak.ones_like(mu_pt)], axis=1
)
lep_pt = ak.concatenate([ele_pt, mu_pt], axis=1)
print("lep_pt:", lep_pt)

muonIdx = ak.values_astype(
    ak.concatenate([ele_none, ak.local_index(mu_pt, axis=1)], axis=1), int
)

mu_sf = ak.unflatten(rng.normal(1.0, 0.05, nmu_tot), nmu)
new_mu_pt = mu_pt * mu_sf


mu_mask = abs(lep_pdgId) == 13
print(mu_mask)
print(mu_mask)
mu_idx = ak.to_packed(muonIdx)
print(new_mu_pt[mu_idx])

print(ak.where(mu_mask, new_mu_pt[mu_idx], lep_pt))

# print(ak.num(lep_pt))
# print(ak.num(lep_pdgId))
# print(ak.num(new_mu_pt[mu_idx]))
