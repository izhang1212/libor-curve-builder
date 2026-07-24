"""
Bootstrap the LIBOR zero curve from the seed quotes, check that the inputs
reprice, print the curve, and plot it.
"""

import os
from data.seed_data import DEPOSITS, FUTURES, SWAPS
from bootstrap.engine import bootstrap
from plots.plot import plot_curve, plot_forward_curve, plot_table


def reprice_check(curve):
    """Largest absolute error when repricing each input off the solved curve."""
    worst = 0.0

    # deposits: model simple rate vs quote
    for maturity, rate in DEPOSITS:
        tau = maturity * 365 / 360
        model = (1 / curve.df(maturity) - 1) / tau
        worst = max(worst, abs(model - rate))

    # futures: model forward vs quoted forward
    for t1, t2, price in FUTURES:
        tau = (t2 - t1) * 365 / 360
        model = (curve.df(t1) / curve.df(t2) - 1) / tau
        worst = max(worst, abs(model - (100 - price) / 100))

    # swaps: model par rate vs quote
    for maturity, rate, freq in SWAPS:
        tau = 1 / freq
        n = round(maturity * freq)
        times = [i * tau for i in range(1, n + 1)]
        annuity = sum(tau * curve.df(t) for t in times)
        model = (1 - curve.df(maturity)) / annuity
        worst = max(worst, abs(model - rate))

    return worst


def main():
    curve = bootstrap(DEPOSITS, FUTURES, SWAPS)

    print(f"{'maturity':>10} {'zero %':>10} {'DF':>12}")
    for t, z in curve.nodes:
        print(f"{t:>10.3f} {z*100:>10.4f} {curve.df(t):>12.6f}")

    worst = reprice_check(curve)
    print(f"\nworst input repricing error: {worst:.2e}")

    os.makedirs("output", exist_ok=True)
    path = plot_curve(curve, DEPOSITS, FUTURES, SWAPS)
    print(f"plot written to {path}")

    fwd_path = plot_forward_curve(curve)
    print(f"forward plot written to {fwd_path}")

    table_path = plot_table(curve)
    print(f"table written to {table_path}")

    from bootstrap.curve import ZeroCurve
    c = ZeroCurve()
    c.add_node(1.0, 0.048)
    c.add_node(2.0, 0.050)
    print(c.zero(1.0), c.zero(1.5), c.zero(2.0))


if __name__ == "__main__":
    main()