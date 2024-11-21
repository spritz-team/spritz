import sys

import numpy

try:
    import cStringIO as io
except ImportError:
    import io

# for later
# func = numbaize(formula,['p%i'%i for i in range(nParams)]+[varnames[i] for i in range(nEvalVars)])


def is_gz_file(filename):
    with open(filename, "rb") as f:
        return f.read(2) == b"\x1f\x8b"


def convert_rochester_file(path, loaduncs=True):
    initialized = False

    fopen = open
    fmode = "rt"
    if is_gz_file(path):
        import gzip

        fopen = gzip.open
        fmode = (
            "r"
            if sys.platform.startswith("win") and sys.version_info.major < 3
            else fmode
        )

    with fopen(path, fmode) as f:
        for line in f:
            line = line.strip("\n")
            # the number of sets available
            if line.startswith("NSET"):
                nsets = int(line.split()[1])
            # the number of members in a given set
            elif line.startswith("NMEM"):
                members = [int(x) for x in line.split()[1:]]
                assert len(members) == nsets
            # the type of the values provided: 0 is default, 1 is replicas (for stat unc), 2 is Symhes (for various systematics)
            elif line.startswith("TVAR"):
                tvars = [int(x) for x in line.split()[1:]]
                assert len(tvars) == nsets
            # number of phi bins
            elif line.startswith("CPHI"):
                nphi = int(line.split()[1])
                phiedges = [
                    float(x) * 2 * numpy.pi / nphi - numpy.pi for x in range(nphi + 1)
                ]
            # number of eta bins and edges
            elif line.startswith("CETA"):
                neta = int(line.split()[1])
                etaedges = [float(x) for x in line.split()[2:]]
                assert len(etaedges) == neta + 1
            # minimum number of tracker layers with measurement
            elif line.startswith("RMIN"):
                nmin = int(line.split()[1])
            # number of bins in the number of tracker layers measurements
            elif line.startswith("RTRK"):
                ntrk = int(line.split()[1])
            # number of abseta bins and edges
            elif line.startswith("RETA"):
                nabseta = int(line.split()[1])
                absetaedges = [float(x) for x in line.split()[2:]]
                assert len(absetaedges) == nabseta + 1
            # load the parameters
            # the structure will be
            # SETNUMBER MEMBERNUMBER TAG[T,R,F,C] [TAG specific indices] [values]
            else:
                if not initialized:
                    # don't want to necessarily load uncertainties
                    toload = nsets if loaduncs else 1
                    M = {
                        s: {m: {t: {} for t in range(2)} for m in range(members[s])}
                        for s in range(toload)
                    }
                    A = {
                        s: {m: {t: {} for t in range(2)} for m in range(members[s])}
                        for s in range(toload)
                    }
                    kRes = {
                        s: {m: {t: [] for t in range(2)} for m in range(members[s])}
                        for s in range(toload)
                    }
                    rsPars = {
                        s: {m: {t: {} for t in range(3)} for m in range(members[s])}
                        for s in range(toload)
                    }
                    cbS = {s: {m: {} for m in range(members[s])} for s in range(toload)}
                    cbA = {s: {m: {} for m in range(members[s])} for s in range(toload)}
                    cbN = {s: {m: {} for m in range(members[s])} for s in range(toload)}
                    initialized = True
                remainder = line.split()
                setn, membern, tag, *remainder = remainder
                setn = int(setn)
                membern = int(membern)
                tag = str(tag)
                # tag T has 2 indices corresponding to TYPE BINNUMBER and has RTRK+1 values each
                # these correspond to the nTrk[2] parameters of RocRes (and BINNUMBER is the abseta bin)
                if tag == "T":
                    t, b, *remainder = remainder
                    t = int(t)
                    b = int(b)
                    values = [float(x) for x in remainder]
                    assert len(values) == ntrk + 1

                # tag R has 2 indices corresponding to VARIABLE BINNUMBER and has RTRK values each
                # these variables correspond to the rsPar[3] and crystal ball (std::vector<CrystalBall> cb) of RocRes where CrystalBall has values s, a, n
                # (and BINNUMBER is the abseta bin)
                # Note: crystal ball here is a symmetric double-sided crystal ball
                elif tag == "R":
                    v, b, *remainder = remainder
                    v = int(v)
                    b = int(b)
                    values = [float(x) for x in remainder]
                    assert len(values) == ntrk
                    if v in range(3):
                        if setn in rsPars:
                            rsPars[setn][membern][v][b] = values
                            if v == 2:
                                rsPars[setn][membern][v][b] = [x * 0.01 for x in values]
                    elif v == 3:
                        if setn in cbS:
                            cbS[setn][membern][b] = values
                    elif v == 4:
                        if setn in cbA:
                            cbA[setn][membern][b] = values
                    elif v == 5:
                        if setn in cbN:
                            cbN[setn][membern][b] = values

                # tag F has 1 index corresponding to TYPE and has RETA values each
                # these correspond to the kRes[2] of RocRes
                elif tag == "F":
                    t, *remainder = remainder
                    t = int(t)
                    values = [float(x) for x in remainder]
                    assert len(values) == nabseta
                    if setn in kRes:
                        kRes[setn][membern][t] = values

                # tag C has 3 indices corresponding to TYPE VARIABLE BINNUMBER and has NPHI values each
                # these correspond to M and A values of CorParams (and BINNUMBER is the eta bin)
                # These are what are used to get the scale factor for kScaleDT (and kScaleMC)
                #       scale = 1.0 / (M+Q*A*pT)
                # For the kSpreadMC (gen matched, recommended) and kSmearMC (not gen matched), we need all of the above parameters
                elif tag == "C":
                    t, v, b, *remainder = remainder
                    t = int(t)
                    v = int(v)
                    b = int(b)
                    values = [float(x) for x in remainder]
                    assert len(values) == nphi
                    if v == 0:
                        if setn in M:
                            M[setn][membern][t][b] = [1.0 + x * 0.01 for x in values]
                    elif v == 1:
                        if setn in A:
                            A[setn][membern][t][b] = [x * 0.01 for x in values]

                else:
                    raise ValueError(line)

    # now build the lookup tables
    # for data scale, simple, just M A in bins of eta,phi
    _scaleedges = (numpy.array(etaedges), numpy.array(phiedges))
    _Mvalues = {
        s: {
            m: {t: numpy.array([M[s][m][t][b] for b in range(neta)]) for t in M[s][m]}
            for m in M[s]
        }
        for s in M
    }
    _Avalues = {
        s: {
            m: {t: numpy.array([A[s][m][t][b] for b in range(neta)]) for t in A[s][m]}
            for m in A[s]
        }
        for s in A
    }

    # for mc scale, more complicated
    # version 1 if gen pt available
    # only requires the kRes lookup
    _resedges = numpy.array(absetaedges)
    _kResvalues = {
        s: {m: {t: numpy.array(kRes[s][m][t]) for t in kRes[s][m]} for m in kRes[s]}
        for s in kRes
    }

    # version 2 if gen pt not available
    trkedges = [0] + [nmin + x + 0.5 for x in range(ntrk)]
    _cbedges = (numpy.array(absetaedges), numpy.array(trkedges))
    _rsParsvalues = {
        s: {
            m: {
                t: numpy.array([rsPars[s][m][t][b] for b in range(nabseta)])
                for t in rsPars[s][m]
            }
            for m in rsPars[s]
        }
        for s in rsPars
    }
    _cbSvalues = {
        s: {m: numpy.array([cbS[s][m][b] for b in range(nabseta)]) for m in cbS[s]}
        for s in cbS
    }
    _cbAvalues = {
        s: {m: numpy.array([cbA[s][m][b] for b in range(nabseta)]) for m in cbA[s]}
        for s in cbA
    }
    _cbNvalues = {
        s: {m: numpy.array([cbN[s][m][b] for b in range(nabseta)]) for m in cbN[s]}
        for s in cbN
    }

    wrapped_up = {
        "nsets": nsets,
        "members": members,
        "edges": {
            "scales": _scaleedges,
            "res": _resedges,
            "cb": _cbedges,
        },
        "values": {
            "M": _Mvalues,
            "A": _Avalues,
            "kRes": _kResvalues,
            "rsPars": _rsParsvalues,
            "cbS": _cbSvalues,
            "cbA": _cbAvalues,
            "cbN": _cbNvalues,
        },
    }
    return wrapped_up
