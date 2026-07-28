"""
Bootstrap the LIBOR zero curve from the seed quotes, check that the inputs
reprice, walk through the process in a set of plots, and price a swap
against the resulting curve.
"""

import os
from data.seed_data import DEPOSITS, FUTURES, SWAPS, SWAP, VALUATION_DATE
from bootstrap.engine import bootstrap
from pricing.engine import price_swap, swap_schedule, swap_periods
from plots.plot import (
    plot_curve, plot_forward_curve, plot_process, plot_table,
    plot_forward_process, plot_swap_cashflow_process,
)

OUTPUT_DIR = "output"


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


def reset_output_dir():
    """Every run starts from a clean output/ so nothing stale lingers."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for name in os.listdir(OUTPUT_DIR):
        file_path = os.path.join(OUTPUT_DIR, name)
        if os.path.isfile(file_path):
            os.remove(file_path)


def main():
    reset_output_dir()

    curve = bootstrap(DEPOSITS, FUTURES, SWAPS)

    print(f"{'maturity':>10} {'zero %':>10} {'DF':>12}")
    for t, z in curve.nodes:
        print(f"{t:>10.3f} {z * 100:>10.4f} {curve.df(t):>12.6f}")

    worst = reprice_check(curve)
    print(f"\nworst input repricing error: {worst:.2e}")

    # 1. the bootstrapped zero curve
    curve_path = plot_curve(curve, DEPOSITS, FUTURES, SWAPS,
                             path=f"{OUTPUT_DIR}/1.Curve.png")
    print(f"\n1. curve plot written to {curve_path}")

    # 2. the forward curve it implies
    forward_path = plot_forward_curve(curve, path=f"{OUTPUT_DIR}/2.Forward.png")
    print(f"2. forward plot written to {forward_path}")

    # 3. one worked bootstrap example per instrument
    process_path = plot_process(curve, DEPOSITS, FUTURES, SWAPS,
                                 path=f"{OUTPUT_DIR}/3.Process.png")
    print(f"3. process plot written to {process_path}")

    # 4. the priced swap's own payment schedule read off the curve
    table_rows = swap_schedule(curve, SWAP, VALUATION_DATE)
    table_path = plot_table(table_rows, path=f"{OUTPUT_DIR}/4.Table.png",
                             title="Swap payment schedule", label_col="Payment date")
    print(f"4. table written to {table_path}")

    # price the swap now so steps 5-6 can walk through one real period of it
    swap_csv_path = f"{OUTPUT_DIR}/7.Swap_Pricing.csv"
    rows, summary = price_swap(curve, SWAP, VALUATION_DATE, path=swap_csv_path)
    periods = swap_periods(SWAP, VALUATION_DATE)
    demo_idx = len(periods) // 2
    demo_period = periods[demo_idx]
    demo_row = rows[demo_idx]

    # 5. zero curve -> forward rate, for that same period
    forward_process_path = plot_forward_process(
        curve, demo_period["t_start"], demo_period["t_end"],
        demo_period["start"].isoformat(), demo_period["end"].isoformat(),
        path=f"{OUTPUT_DIR}/5.Forward_Process.png")
    print(f"5. forward process plot written to {forward_process_path}")

    # 6. price that one period's fixed & floating cashflows and net them
    swap_process_path = plot_swap_cashflow_process(
        demo_row, demo_period["tau"], curve.df(demo_period["t_end"]), SWAP["notional"],
        path=f"{OUTPUT_DIR}/6.Swap_Process.png")
    print(f"6. swap cashflow process plot written to {swap_process_path}")

    # 7. the full priced schedule
    print(f"\nswap priced: {len(rows)} periods")
    print(f"  fixed leg PV   : {summary['fixed_pv']:15,.2f}")
    print(f"  floating leg PV: {summary['floating_pv']:15,.2f}")
    print(f"  net ({summary['pov']}): {summary['net']:15,.2f}")
    print(f"7. swap pricing written to {swap_csv_path}")


if __name__ == "__main__":
    main()
