def theory_unc(events, variations):
    # QCD Scale
    nVariations = len(events.LHEScaleWeight[0])
    for i, j in enumerate(
        [
            0,
            1,
            2,
            3,
            nVariations - 1,
            nVariations - 2,
            nVariations - 3,
            nVariations - 4,
        ]
    ):
        events[f"weight_QCDScale_{i}"] = events.weight * events.LHEScaleWeight[:, j]
        variations.register_variation(
            columns=["weight"], variation_name=f"QCDScale_{i}"
        )

    # Pdf Weights
    nVariations = len(events.LHEPdfWeight[0])
    for i, j in enumerate(range(nVariations)):
        events[f"weight_PDFWeight_{i}"] = events.weight * events.LHEPdfWeight[:, j]
        variations.register_variation(
            columns=["weight"], variation_name=f"PDFWeight_{i}"
        )
    return events, variations
