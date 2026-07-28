# libor-curve-builder

## Overview

**Inspiration**: Inspired by the bootstrapping example in Hull's *Options, Futures, and Other Derivatives*, building a single zero curve out of three different types of market quotes. We then use this yield curve to price a fixed-for-floating IR swap.

**Goal**: Take LIBOR deposit rates, Eurodollar futures prices, and par swap rates, and bootstrap one continuous zero curve that reprices all three instrument types back to (nearly) their quoted values.

## Methodology

The curve is built **sequentially, shortest maturity to longest**. Each instrument's discount factor is solved using only the discount factors already on the curve from earlier, shorter-maturity instruments — that's what makes it "bootstrapping" rather than a single global fit.

Solved points are stored as (maturity, continuously-compounded zero rate) nodes. Between nodes, zero rates are linearly interpolated; before the first node and after the last, the rate is held flat.

## Instruments

**LIBOR deposits** (short end, out to ~3 months) — simple-interest cash deposits quoted Act/360. Each deposit converts directly to a discount factor: `DF = 1 / (1 + rate * tau)`. These seed the first nodes on the curve.

**Eurodollar futures** (middle, 3 months to ~2 years) — each contract quotes a 3-month forward rate over `[t1, t2]` as `(100 - price) / 100`. Since `DF(t1)` is already known from an earlier node, the forward rate chains it forward: `DF(t2) = DF(t1) / (1 + forward_rate * tau)`.

**Swap rates** (long end, 2+ years) — par swap rates imply the discount factor at each swap's maturity given all the earlier discount factors on its fixed-leg payment schedule (the "known annuity"). Solving the par-rate equation for the one remaining unknown discount factor extends the curve out to the swap's maturity.

## Pricing

Once the curve is built, it's used to price an actual fixed-for-floating interest rate swap (`data/seed_data.py`'s `SWAP`: notional, fixed rate, start/end dates, payment frequency, and point of view). `pricing/` builds the payment schedule between those dates, then for each period computes both legs off the same curve:

- **Fixed leg** — the trade's fixed rate is constant every period; cashflow = `notional * rate * tau`.
- **Floating leg** — no future LIBOR fixing exists yet, so each period uses the curve's own implied forward rate for that period (`curve.forward(t1, t2)`) as the no-arbitrage projection of what that fixing will be.

Both legs' cashflows are discounted with the same curve (`curve.df(t)`) — this project only ever builds one curve, so it does double duty as both the discounting and forecasting curve, per the single-curve convention this whole project is based on. Each period's fixed PV, floating PV, and their difference are written to a CSV, along with the two legs' total PV and the swap's net value from the chosen point of view.

## Output

Everything below is rewritten from scratch on every run (`main.py` clears `output/` first), numbered in the order the pipeline produces them:

1. **`1.Curve.png`** — the bootstrapped zero curve, colored by which instrument (deposit / futures / swap) solved each segment.
2. **`2.Forward.png`** — the continuous forward curve implied by the zero curve. Its "sawtooth" shape is expected: linear-on-zero-rate interpolation keeps the zero curve continuous but kinks its slope at every node, and the forward rate depends on that slope, so it jumps wherever segment spacing changes.
3. **`3.Process.png`** — one worked example per bootstrap instrument (a deposit, a Eurodollar future, a swap), showing the known inputs, the textbook equation, and the solved zero rate for each.
4. **`4.Table.png`** — the priced swap's own payment schedule: maturity, zero rate, discount factor, and forward rate at each of its payment dates.
5. **`5.Forward_Process.png`** — one worked example deriving a single period's forward rate from the two zero-curve points either side of it — the calculation the floating leg needs for every period.
6. **`6.Swap_Process.png`** — one worked example pricing that same period's fixed and floating cashflows side by side, then netting them.
7. **`7.Swap_Pricing.csv`** — the full priced schedule: every period's fixed/floating rate, cashflow, and discounted cashflow, plus each leg's total PV and the swap's net value.