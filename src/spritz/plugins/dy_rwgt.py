def model(x, p0, p1, p2, p3):
    return p0 + p1 * x + p2 * x**2 + p3 * x**3


def rwgt_ptj1(events):
    pars = [1.04327232e00, -1.13639158e-03, 3.66058164e-06, -4.65472602e-09]
    events["weight"] = events.weight * model(events.ptj1, *pars)
    return events
