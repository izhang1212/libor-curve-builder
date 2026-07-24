"""
Plots of the bootstrapped curve.

  Zero curve      the continuously-compounded zero rate at each node, linearly
                  interpolated -- the direct output of the bootstrap. Colored
                  by which instrument built each segment (deposit / futures /
                  swap) since that sequential, segment-by-segment solve is the
                  whole point of "bootstrapping".

  Forward curve   the instantaneous-ish forward implied between adjacent
                  sample points. This is the more revealing plot: because we
                  interpolate linearly on zero rates, the forward curve comes
                  out jagged, with a kink at every node. That sawtooth is not
                  an error -- it is exactly what linear-on-zeros produces, and
                  it is the visual argument for smoother interpolation if you
                  ever need a clean forward curve.
"""

import numpy as np
import matplotlib.pyplot as plt

SEGMENT_COLORS = {
    "deposit": "#1f4e79",
    "future": "#e07b00",
    "swap": "#2e8b57",
}
SEGMENT_LABELS = {
    "deposit": "Deposits",
    "future": "Eurodollar futures",
    "swap": "Swaps",
}


def plot_curve(curve, deposits, futures, swaps, path="output/curve.png"):
    node_t = np.array([t for t, _ in curve.nodes])
    node_z = np.array([z for _, z in curve.nodes]) * 100.0

    # classify each node by which instrument produced it, so the curve can be
    # colored segment-by-segment to show how bootstrapping stitches it together
    deposit_times = {round(m, 6) for m, _ in deposits}
    futures_times = {round(t2, 6) for _, t2, _ in futures}
    swap_times = {round(m, 6) for m, _, _ in swaps}

    def classify(t):
        r = round(t, 6)
        if r in deposit_times:
            return "deposit"
        if r in futures_times:
            return "future"
        if r in swap_times:
            return "swap"
        return "deposit"

    node_src = [classify(t) for t in node_t]

    deposit_end = max(deposit_times)
    futures_end = max(futures_times) if futures_times else deposit_end

    segments = [
        ("deposit", node_t[0], deposit_end),
        ("future", deposit_end, futures_end),
        ("swap", futures_end, node_t[-1]),
    ]

    fig, ax = plt.subplots(figsize=(7.5, 5.5))

    for name, start, end in segments:
        if end <= start:
            continue
        grid = np.linspace(start, end, 200)
        grid_z = np.array([curve.zero(t) for t in grid]) * 100.0
        ax.plot(grid, grid_z, color=SEGMENT_COLORS[name], lw=1.8,
                 label=SEGMENT_LABELS[name], zorder=1)

    node_colors = [SEGMENT_COLORS[s] for s in node_src]
    ax.scatter(node_t, node_z, s=32, c=node_colors, edgecolors="black",
                linewidths=0.6, zorder=2)

    ax.set_title("Zero curve, segmented by bootstrap instrument")
    ax.set_xlabel("maturity (years)")
    ax.set_ylabel("zero rate (%)")
    ax.legend(frameon=False)
    ax.grid(alpha=0.25)

    fig.tight_layout()
    fig.savefig(path, dpi=130)
    return path


def plot_forward_curve(curve, path="output/forward.png"):
    node_t = np.array([t for t, _ in curve.nodes])

    # forwards from discount factors on a fine grid:
    #   f(t1,t2) = ln(DF(t1)/DF(t2)) / (t2 - t1)   (continuous)
    fg = np.linspace(node_t[0], node_t[-1], 400)
    dfs = np.array([curve.df(t) for t in fg])
    fwd = np.log(dfs[:-1] / dfs[1:]) / (fg[1:] - fg[:-1]) * 100.0
    fwd_t = 0.5 * (fg[:-1] + fg[1:])

    fig, ax = plt.subplots(figsize=(7.5, 5))

    ax.plot(fwd_t, fwd, color="#548235", lw=1.4)
    ax.set_title("Implied forward curve")
    ax.set_xlabel("maturity (years)")
    ax.set_ylabel("forward rate (%)")
    ax.grid(alpha=0.25)

    fig.tight_layout()
    fig.savefig(path, dpi=130)
    return path


def plot_table(curve, path="output/table.png"):
    """Render maturity / zero rate / discount factor at each bootstrapped node."""
    rows = [(t, z * 100.0, curve.df(t)) for t, z in curve.nodes]

    fig, ax = plt.subplots(figsize=(5.5, 0.45 * len(rows) + 1))
    ax.axis("off")

    col_labels = ["Maturity (yrs)", "Zero rate (%)", "Discount factor"]
    cell_text = [[f"{t:.3f}", f"{z:.4f}", f"{df:.6f}"] for t, z, df in rows]

    table = ax.table(
        cellText=cell_text,
        colLabels=col_labels,
        cellLoc="center",
        loc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 1.4)

    for (row, _col), cell in table.get_celld().items():
        cell.set_edgecolor("#dddddd")
        if row == 0:
            cell.set_facecolor("#1f4e79")
            cell.set_text_props(color="white", weight="bold")
        else:
            cell.set_facecolor("#f2f2f2" if row % 2 == 0 else "white")

    ax.set_title("Bootstrapped curve nodes", pad=12)
    fig.tight_layout()
    fig.savefig(path, dpi=130, bbox_inches="tight")
    return path
