# libor-curve-builder

## Overview

**Inspiration**: Inspired by the bootstrapping example in Hull's *Options, Futures, and Other Derivatives* — building a single zero curve out of three different types of market quotes.

**Goal**: Take LIBOR deposit rates, Eurodollar futures prices, and par swap rates, and bootstrap one continuous zero curve that reprices all three instrument types back to (nearly) their quoted values.

## Methodology

The curve is built **sequentially, shortest maturity to longest**. Each instrument's discount factor is solved using only the discount factors already on the curve from earlier, shorter-maturity instruments — that's what makes it "bootstrapping" rather than a single global fit.

Solved points are stored as (maturity, continuously-compounded zero rate) nodes. Between nodes, zero rates are linearly interpolated; before the first node and after the last, the rate is held flat.

## Instruments

**LIBOR deposits** (short end, out to ~3 months) — simple-interest cash deposits quoted Act/360. Each deposit converts directly to a discount factor: `DF = 1 / (1 + rate * tau)`. These seed the first nodes on the curve.

**Eurodollar futures** (middle, 3 months to ~2 years) — each contract quotes a 3-month forward rate over `[t1, t2]` as `(100 - price) / 100`. Since `DF(t1)` is already known from an earlier node, the forward rate chains it forward: `DF(t2) = DF(t1) / (1 + forward_rate * tau)`.

**Swap rates** (long end, 2+ years) — par swap rates imply the discount factor at each swap's maturity given all the earlier discount factors on its fixed-leg payment schedule (the "known annuity"). Solving the par-rate equation for the one remaining unknown discount factor extends the curve out to the swap's maturity.
