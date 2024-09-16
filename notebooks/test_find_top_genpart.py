import awkward as ak
import numpy as np
import rich

rng = np.random.Generator(np.random.PCG64(31))

nevents = 100_000

n_genpart = rng.integers(0, 7, nevents)
n_genpart_tot = np.sum(n_genpart)
pt = rng.normal(30, 2, n_genpart_tot)
pt = ak.unflatten(pt, n_genpart)
pdg_ids = rng.integers(-6, 7, n_genpart_tot)
pdg_ids = ak.unflatten(pdg_ids, n_genpart)


GenPart = ak.zip(
    {
        "pt": pt,
        "pdgId": pdg_ids,
        "statusFlags": ak.values_astype(ak.ones_like(pdg_ids), int) << 13,
    }
)

events = ak.zip(
    {
        "GenPart": GenPart,
    },
    depth_limit=1,
)


top_particle_mask = (events.GenPart.pdgId == 6) & ak.values_astype(
    (events.GenPart.statusFlags >> 13) & 1, bool
)
toppt = ak.fill_none(
    ak.mask(events, ak.num(events.GenPart[top_particle_mask]) >= 1)
    .GenPart[top_particle_mask][:, -1]
    .pt,
    0.0,
)


atop_particle_mask = (events.GenPart.pdgId == -6) & ak.values_astype(
    (events.GenPart.statusFlags >> 13) & 1, bool
)
atoppt = ak.fill_none(
    ak.mask(events, ak.num(events.GenPart[atop_particle_mask]) >= 1)
    .GenPart[atop_particle_mask][:, -1]
    .pt,
    0.0,
)


top_pt_rwgt = (toppt * atoppt > 0.0) * (
    np.sqrt(np.exp(0.0615 - 0.0005 * toppt) * np.exp(0.0615 - 0.0005 * atoppt))
) + (toppt * atoppt <= 0.0)

print(toppt)
print(toppt[ak.num(events.GenPart[top_particle_mask]) >= 1])

print(atoppt)
print(atoppt[ak.num(events.GenPart[atop_particle_mask]) >= 1])
print(np.sum(top_pt_rwgt))
# rich.print(top_particle_mask)
# ak.mask(events, (ak.num(events.GenPart[top_particle_mask])>=1)
