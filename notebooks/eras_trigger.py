import awkward as ak
import numpy as np

rng = np.random.Generator(np.random.PCG64(1))
d = {"eras": rng.integers(1, 4, size=100)}
d.update({k: rng.random(size=100) < 0.1 for k in ["a", "b", "c"]})
events = ak.zip(d)
print(events)
print(events.eras)

trigs = {1: "a", 2: "b", 3: "c"}
pass_trig = ak.ones_like(events.eras) != 1.0
for era in trigs:
    pass_trig = pass_trig | ((events.eras == era) & (events[trigs[era]]))

print(pass_trig)
print(len(pass_trig[pass_trig]) / len(pass_trig))

# print((1 <= events.eras) & (events.eras <= 3) & events.a)
