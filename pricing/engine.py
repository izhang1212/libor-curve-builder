# Build swap pricing
    # Build swap -> price -> build report

import os
from pricing.swap import Swap
from pricing.price import price
from pricing.report import write_csv
from conventions.dates import year_fraction_to

def _build_swap(terms):
    return Swap(
        notional=terms["notional"],
        fixed_rate=terms["fixed_rate"],
        freq=terms["frequency"],
        start=terms["start"],
        end=terms["end"],
        pov=terms["pov"],
    )


# Price swap against curve and write it to the csv
def price_swap(curve, terms, valuation, path="output/swap.csv"):
    swap = _build_swap(terms)
    rows, summary = price(swap, curve, valuation)

    os.makedirs(os.path.dirname(path), exist_ok=True)
    write_csv(rows, summary, path)
    return rows, summary


# (payment date, zero rate, discount factor, forward rate) at each of the
# swap's own payment dates -- lets a table follow this specific trade's
# schedule instead of the full, unrelated list of bootstrapped curve nodes.
# The forward rate uses the same simple-rate convention as the floating leg
# in pricing/price.py, so it matches the CSV's "floating rate" column exactly.
def swap_schedule(curve, terms, valuation):
    swap = _build_swap(terms)
    rows = []
    for period in swap.periods(valuation):
        t_start = year_fraction_to(valuation, period["start"])
        t_end = period["t_pay"]
        rows.append((
            period["end"].isoformat(),
            curve.zero(t_end),
            curve.df(t_end),
            curve.forward(t_start, t_end),
        ))
    return rows


# Raw per-period schedule info (dates + year-fractions + accrual), independent
# of any curve/pricing -- lets a caller pick one period and get everything
# needed to demonstrate the forward-rate derivation and cashflow calc for it.
def swap_periods(terms, valuation):
    swap = _build_swap(terms)
    periods = []
    for p in swap.periods(valuation):
        periods.append({
            "start": p["start"],
            "end": p["end"],
            "t_start": year_fraction_to(valuation, p["start"]),
            "t_end": p["t_pay"],
            "tau": p["tau"],
        })
    return periods