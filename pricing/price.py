# Walk schedule, compute both legs' cashflows from curve, and assemble rows

from conventions.dates import year_fraction_to

# Returns (rows, summary), where rows = one dict per period, with both legs' rate, cf, and discounted cf
def price(swap, curve, valuation):
    rows = []
    fixed_pv = 0.0
    floating_pv = 0.0

    # Go through each period and calculate respective legs
    for p in swap.periods(valuation):
        df = curve.df(p["t_pay"])

        # period start/end on the curve axis, for the forward rate
        t_start = year_fraction_to(valuation, p["start"])
        t_end = year_fraction_to(valuation, p["end"])

        # fixed leg
        fixed_rate = swap.fixed_rate
        fixed_cf = fixed_rate * swap.notional * p["tau"]
        fixed_disc = fixed_cf * df

        # floating leg: forward rate implied by the curve over the period
        floating_rate = curve.forward(t_start, t_end)
        floating_cf = floating_rate * swap.notional * p["tau"]
        floating_disc = floating_cf * df

        fixed_pv += fixed_disc
        floating_pv += floating_disc

        rows.append({
            "payment_date": p["end"],
            "fixed_rate": fixed_rate,
            "fixed_cf": fixed_cf,
            "fixed_disc_cf": fixed_disc,
            "floating_rate": floating_rate,
            "floating_cf": floating_cf,
            "floating_disc_cf": floating_disc,
            "difference": floating_disc - fixed_disc,
        })

    # net from the swap's point of view: a payer pays fixed, receives floating
    if swap.pov == "payer":
        net = floating_pv - fixed_pv
    else:
        net = fixed_pv - floating_pv

    summary = {
        "fixed_pv": fixed_pv,
        "floating_pv": floating_pv,
        "net": net,
        "pov": swap.pov,
    }
    return rows, summary