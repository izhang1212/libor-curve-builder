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
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

from conventions.daycount import DayCount, year_fraction
from conventions.compunding import zero_from_df

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


def _truncate_rows(rows, head=2, tail=2, fill="..."):
    """Collapse a long row list to head + ellipsis + tail so tables stay a fixed size."""
    if len(rows) <= head + tail + 1:
        return rows
    ellipsis_row = [fill] * len(rows[0])
    return rows[:head] + [ellipsis_row] + rows[-tail:]


EQ_SIZE = 15
CARD_FILL = "#f6f6f4"
CARD_EDGE = "#dddad2"

# Shared geometry for every "process" card (table -> equations -> result),
# in real inches -- kept as one set of constants so every process-style plot
# (bootstrap steps, forward-rate derivation, swap cashflow pricing) reads as
# one consistent visual family rather than each having its own tuning.
PROC_TITLE_H = 0.32
PROC_ARROW_H = 0.24
PROC_TABLE_ROW_H = 0.32
PROC_EQ_TOP_PAD = 0.10
PROC_EQ_LINE_H = 0.62      # physical gap between equation-line centers
PROC_RESULT_H = 0.65       # tall enough that the highlight box comfortably fits the headline font
PROC_CARD_PAD = 0.14
PROC_OUTER_MARGIN = 0.7


def _draw_step_table(ax, col_labels, rows, color, highlight="last"):
    """Small node/quote table for one step of the process plot. `bbox=[0,0,1,1]`
    stretches whatever rows exist to fill the whole given axes height -- so a
    table with fewer real rows (deposit) still reaches the same bottom edge as
    a sibling table with more rows (futures), just with taller row bands,
    instead of leaving dead space below a short, fixed-height table."""
    ax.patch.set_alpha(0)
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    n_rows = len(rows)
    table = ax.table(cellText=rows, colLabels=col_labels, cellLoc="center",
                      loc="lower center", bbox=[0, 0, 1, 1])
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 1.5)

    for (row, _col), cell in table.get_celld().items():
        cell.set_edgecolor("#dddddd")
        if row == 0:
            cell.set_facecolor(color)
            cell.set_text_props(color="white", weight="bold")
        elif highlight == "all" or (highlight == "last" and row == n_rows):
            cell.set_facecolor(color)
            cell.set_alpha(0.18)
        else:
            cell.set_facecolor("white")


def _draw_equations(ax, lines, sizes, pitch):
    """Stack mathtext equation lines as a tight block, vertically centered.
    `pitch` is the gap between line centers as a fraction of the axes height,
    and must be supplied by the caller sized in real inches (see EQ_LINE_H) --
    tall mathtext glyphs (summation limits, stacked fractions) are much taller
    than plain text, so a fraction that looks fine for short text collides for
    those unless the *physical* gap is held fixed regardless of line count."""
    ax.patch.set_alpha(0)
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    n = len(lines)
    top = 0.5 + (n - 1) * pitch / 2
    for i, (line, size) in enumerate(zip(lines, sizes)):
        ax.text(0.5, top - i * pitch, line, ha="center", va="center", fontsize=size)


def _draw_result(ax, headline, color, w_in, h_in):
    """`w_in`/`h_in` are this axes' real physical size in inches. Rounded-box
    corners drawn with `pad`/`rounding_size` in axes-fraction (0..1) come out
    as ellipses, not circles, whenever the axes itself isn't square -- which
    this one never is (it's short and wide). Setting the data limits to the
    axes' own inch dimensions makes 1 data-unit equal in both directions, so
    a box drawn in those units rounds evenly regardless of the axes' aspect."""
    ax.patch.set_alpha(0)
    ax.axis("off")
    ax.set_xlim(0, w_in)
    ax.set_ylim(0, h_in)

    # the box must be tall enough in real inches to hold the headline's font
    # size with room to spare -- a box sized as a small fraction of a short
    # axes can end up physically shorter than the text it's meant to hold,
    # which is what sliced the box edge straight through the numbers.
    box_x, box_w = 0.05 * w_in, 0.9 * w_in
    box_y, box_h = 0.16 * h_in, 0.68 * h_in
    box = FancyBboxPatch((box_x, box_y), box_w, box_h,
                          boxstyle="round,pad=0,rounding_size=0.08",
                          transform=ax.transData, facecolor=color, alpha=0.15,
                          edgecolor=color, linewidth=1.6)
    ax.add_patch(box)
    ax.text(w_in / 2, box_y + box_h * 0.52, headline, ha="center", va="center",
            fontsize=17, fontweight="bold", color=color)


def _vertical_arrow(fig, ax_top, ax_bottom, color="#999999"):
    a = ax_top.get_position()
    b = ax_bottom.get_position()
    x = (a.x0 + a.x1) / 2
    fig.add_artist(FancyArrowPatch((x, a.y0), (x, b.y1), transform=fig.transFigure,
                                    arrowstyle="-|>", mutation_scale=16,
                                    color=color, lw=1.4, shrinkA=2, shrinkB=2))


def _draw_card(fig, axes_in_row, fig_w_in, fig_h_in, pad_x=0.012, pad_y=0.03):
    """A single rounded background panel behind a whole row's axes, so the
    table / equation / result read as one grouped step instead of three
    separate floating pieces. Drawn on its own low-zorder axes -- a bare
    figure patch draws *after* (on top of) sibling axes and hides them.

    The card is wide and short, so a corner radius specified in axes-fraction
    (0..1) would come out as an ellipse, not a circle -- `fig_w_in`/`fig_h_in`
    (the full figure's physical size) let us convert the card's own bounding
    box to inches and set the data limits to match, making the rounding
    isotropic regardless of the card's aspect ratio."""
    boxes = [ax.get_position() for ax in axes_in_row]
    x0 = min(b.x0 for b in boxes) - pad_x
    x1 = max(b.x1 for b in boxes) + pad_x
    y0 = min(b.y0 for b in boxes) - pad_y
    y1 = max(b.y1 for b in boxes) + pad_y

    w_in = (x1 - x0) * fig_w_in
    h_in = (y1 - y0) * fig_h_in

    ax_bg = fig.add_axes((x0, y0, x1 - x0, y1 - y0), zorder=0)
    ax_bg.set_xlim(0, w_in)
    ax_bg.set_ylim(0, h_in)
    ax_bg.set_xticks([])
    ax_bg.set_yticks([])
    for spine in ax_bg.spines.values():
        spine.set_visible(False)
    ax_bg.patch.set_alpha(0)
    card = FancyBboxPatch((0.0, 0.0), w_in, h_in,
                           boxstyle="round,pad=0,rounding_size=0.14",
                           transform=ax_bg.transData, facecolor=CARD_FILL,
                           edgecolor=CARD_EDGE, linewidth=1.0)
    ax_bg.add_patch(card)

    for ax in axes_in_row:
        ax.set_zorder(2)
    return x0, x1, y0, y1


def _content_heights(step, eq_line_h=PROC_EQ_LINE_H):
    table_h = (len(step["table_rows"]) + 1) * PROC_TABLE_ROW_H
    eq_h = PROC_EQ_TOP_PAD + len(step["eq_lines"]) * eq_line_h
    content_h = table_h + PROC_ARROW_H + eq_h + PROC_ARROW_H + PROC_RESULT_H
    return table_h, eq_h, PROC_RESULT_H, content_h


def _draw_process_step(fig, step, x_left, x_right, top_y, table_h, eq_h, result_h,
                        fig_w, total_h, eq_line_h=PROC_EQ_LINE_H):
    """One table -> equations -> result card, used by every process plot."""
    def fx(v):
        return v / fig_w

    def fy(v):
        return v / total_h

    fig.text(fx((x_left + x_right) / 2), fy(top_y), step["title"],
              fontsize=14, fontweight="bold", color=step["color"],
              transform=fig.transFigure, ha="center", va="top")
    y = top_y - PROC_TITLE_H

    y -= PROC_CARD_PAD
    table_bottom = y - table_h
    eq_top = table_bottom - PROC_ARROW_H
    eq_bottom = eq_top - eq_h
    res_top = eq_bottom - PROC_ARROW_H
    res_bottom = res_top - result_h
    card_bottom = res_bottom - PROC_CARD_PAD

    w = x_right - x_left
    ax_table = fig.add_axes((fx(x_left), fy(table_bottom), fx(w), fy(table_h)))
    ax_eq = fig.add_axes((fx(x_left), fy(eq_bottom), fx(w), fy(eq_h)))
    res_w = w * 0.55
    ax_res = fig.add_axes((fx(x_left + (w - res_w) / 2), fy(res_bottom),
                            fx(res_w), fy(result_h)))

    _draw_step_table(ax_table, step["col_labels"], step["table_rows"],
                      step["color"], step["highlight"])
    eq_pitch = eq_line_h / eq_h
    _draw_equations(ax_eq, step["eq_lines"], step["eq_sizes"], eq_pitch)
    _draw_result(ax_res, step["result_headline"], step["color"], res_w, result_h)

    _draw_card(fig, [ax_table, ax_eq, ax_res], fig_w, total_h,
               pad_x=fx(0.15), pad_y=fy(PROC_CARD_PAD))
    _vertical_arrow(fig, ax_table, ax_eq, step["color"])
    _vertical_arrow(fig, ax_eq, ax_res, step["color"])

    return card_bottom


def _render_two_top_one_bottom(steps, main_title, path, fig_w=12.5):
    """Two cards side by side on top, one centered below -- a horizontal flow
    instead of one long vertical strip. The two top cards only line up if
    they're the same height; if their equation/result blocks already match,
    the one variable is table row count, so both are given the *same* table
    axes height (sized to the taller table's row count) and
    `_draw_step_table`'s bbox-fit stretches the shorter table's real rows to
    fill it, rather than padding with dead space below a short, fixed table."""
    max_top_rows = max(len(steps[0]["table_rows"]), len(steps[1]["table_rows"]))

    MARGIN_TOP, MARGIN_BOTTOM = 0.5, 0.15
    ROW_GAP = 0.55            # gap between the top row and the bottom card
    COL_GAP = 0.5             # gap between the two top cards
    CONTENT_W = fig_w - 2 * PROC_OUTER_MARGIN
    TOP_CARD_W = (CONTENT_W - COL_GAP) / 2

    _, eq_h_top, result_h_top, _ = _content_heights(steps[0])  # eq/result already match steps[1]
    table_h_top = (max_top_rows + 1) * PROC_TABLE_ROW_H
    top_layout = (table_h_top, eq_h_top, result_h_top,
                  table_h_top + PROC_ARROW_H + eq_h_top + PROC_ARROW_H + result_h_top)
    bottom_layout = _content_heights(steps[2])
    top_card_h = top_layout[3] + 2 * PROC_CARD_PAD
    bottom_card_h = bottom_layout[3] + 2 * PROC_CARD_PAD

    total_h = (MARGIN_TOP + MARGIN_BOTTOM + ROW_GAP
               + 2 * PROC_TITLE_H + top_card_h + bottom_card_h)

    with plt.rc_context({"mathtext.fontset": "cm", "font.family": "serif"}):
        fig = plt.figure(figsize=(fig_w, total_h))
        fig.suptitle(main_title, fontsize=16, y=1 - (MARGIN_TOP * 0.35) / total_h)

        for i, step in enumerate(steps):
            step["title"] = f"Step {i + 1} · {step['name']}"

        top_y = total_h - MARGIN_TOP
        table_h, eq_h, result_h, _ = top_layout
        left_bottom = _draw_process_step(
            fig, steps[0], PROC_OUTER_MARGIN, PROC_OUTER_MARGIN + TOP_CARD_W,
            top_y, table_h, eq_h, result_h, fig_w, total_h)
        _draw_process_step(
            fig, steps[1], PROC_OUTER_MARGIN + TOP_CARD_W + COL_GAP,
            PROC_OUTER_MARGIN + CONTENT_W, top_y, table_h, eq_h, result_h, fig_w, total_h)

        bottom_y = left_bottom - ROW_GAP
        table_h, eq_h, result_h, _ = bottom_layout
        _draw_process_step(
            fig, steps[2], PROC_OUTER_MARGIN, PROC_OUTER_MARGIN + CONTENT_W,
            bottom_y, table_h, eq_h, result_h, fig_w, total_h)

        fig.savefig(path, dpi=130)
    return path


def _render_single_step(step, main_title, path, fig_w=9.5, eq_line_h=PROC_EQ_LINE_H):
    """One table -> equations -> result card, full width -- the single-step
    counterpart to `_render_two_top_one_bottom`, for a process with only one
    thing to show (e.g. deriving one forward rate from the zero curve).
    `eq_line_h` lets a caller with unusually tall equations (nested fractions)
    ask for extra vertical breathing room between lines without affecting
    every other process plot, which share the same default spacing."""
    MARGIN_TOP, MARGIN_BOTTOM = 0.5, 0.15
    table_h, eq_h, result_h, content_h = _content_heights(step, eq_line_h)
    card_h = content_h + 2 * PROC_CARD_PAD
    total_h = MARGIN_TOP + MARGIN_BOTTOM + PROC_TITLE_H + card_h

    with plt.rc_context({"mathtext.fontset": "cm", "font.family": "serif"}):
        fig = plt.figure(figsize=(fig_w, total_h))
        fig.suptitle(main_title, fontsize=16, y=1 - (MARGIN_TOP * 0.35) / total_h)

        step["title"] = ""  # the suptitle alone is enough for a single card
        top_y = total_h - MARGIN_TOP
        _draw_process_step(fig, step, PROC_OUTER_MARGIN, fig_w - PROC_OUTER_MARGIN,
                            top_y, table_h, eq_h, result_h, fig_w, total_h, eq_line_h)

        fig.savefig(path, dpi=130)
    return path


def plot_process(curve, deposits, futures, swaps, path="output/process.png"):
    """Flowchart-style walkthrough of the bootstrap: for one example per
    instrument, show the known curve values feeding in, the textbook equation
    solved for the zero rate R, and the resulting node."""

    steps = []

    # ---------------------------------------------------------------- deposit
    maturity, rate = deposits[-1]
    tau = year_fraction(0.0, maturity, DayCount.ACT_360)
    df = 1.0 / (1.0 + rate * tau)
    zero = zero_from_df(df, maturity)
    steps.append(dict(
        name="Deposit", color=SEGMENT_COLORS["deposit"], target_t=maturity,
        col_labels=["Maturity", "LIBOR"],
        table_rows=[[f"{m * 12:.0f}M", f"{r * 100:.2f}%"] for m, r in deposits],
        highlight="last",
        eq_lines=[
            r"$DF(t)=\dfrac{1}{1+r\tau}\quad\Rightarrow\quad R(t)=\dfrac{\ln(1+r\tau)}{t}$",
            r"$R=\dfrac{\ln(1+%.4f\times%.4f)}{%.2f}$" % (rate, tau, maturity),
        ],
        eq_sizes=[EQ_SIZE, EQ_SIZE],
        result_headline="$R(%.2f)=%.3f$" % (maturity, zero * 100) + "%",
    ))

    # ---------------------------------------------------------------- futures
    t1, t2, price = min(futures, key=lambda f: abs(f[1] - 2.0))
    f_rate = (100.0 - price) / 100.0
    tau = year_fraction(t1, t2, DayCount.ACT_360)
    r1 = curve.zero(t1)
    zero_t2 = zero_from_df(curve.df(t1) / (1.0 + f_rate * tau), t2)
    nodes_before = [(t, z) for t, z in curve.nodes if t <= t1 + 1e-9]
    steps.append(dict(
        name="Eurodollar future", color=SEGMENT_COLORS["future"], target_t=t2,
        col_labels=["Maturity", "Zero %", "DF"],
        table_rows=_truncate_rows(
            [[f"{t:.3f}", f"{z * 100:.4f}%", f"{curve.df(t):.4f}"] for t, z in nodes_before]),
        highlight="last",
        eq_lines=[
            r"$DF(t_2)=\dfrac{DF(t_1)}{1+F\tau}\quad\Rightarrow\quad "
            r"R_{t_2}=\dfrac{R_{t_1}\,t_1+\ln(1+F\tau)}{t_2}$",
            r"$R_{%.2f}=\dfrac{%.4f\times%.2f+\ln(1+%.4f\times%.4f)}{%.2f}$"
            % (t2, r1, t1, f_rate, tau, t2),
        ],
        eq_sizes=[EQ_SIZE, EQ_SIZE],
        result_headline="$R(%.2f)=%.3f$" % (t2, zero_t2 * 100) + "%",
    ))

    # ------------------------------------------------------------------ swap
    maturity, rate, freq = min(swaps, key=lambda s: abs(s[0] - 5.0))
    tau = 1.0 / freq
    n = round(maturity * freq)
    pay_times = [i * tau for i in range(1, n + 1)]
    known_times = pay_times[:-1]
    coupon = 100.0 * rate * tau
    known_sum = coupon * sum(curve.df(t) for t in known_times)
    final_pay = 100.0 + coupon
    df_n = (100.0 - known_sum) / final_pay
    zero_n = zero_from_df(df_n, maturity)

    terms = [r"%.2fe^{-%.4f\times%.1f}" % (coupon, curve.zero(t), t) for t in known_times]
    shown_terms = [terms[0], r"\cdots", terms[-1]] if len(terms) > 3 else terms
    eq_sub = "$" + "+".join(shown_terms) + r"+%.2fe^{-R\times%.1f}=100$" % (final_pay, maturity)

    steps.append(dict(
        name="Swap", color=SEGMENT_COLORS["swap"], target_t=maturity,
        col_labels=["Maturity", "Zero %", "DF"],
        table_rows=_truncate_rows(
            [[f"{t:.2f}", f"{curve.zero(t) * 100:.4f}%", f"{curve.df(t):.4f}"] for t in known_times]),
        highlight="all",
        eq_lines=[
            r"$\sum_{i=1}^{n-1} C\,e^{-r_i t_i}\;+\;(100+C)\,e^{-RT}=100,\quad C=100R_{swap}\tau$",
            eq_sub,
            r"$R=-\dfrac{1}{%.2f}\ln\!\left(\dfrac{100-%.4f}{%.4f}\right)$"
            % (maturity, known_sum, final_pay),
        ],
        eq_sizes=[EQ_SIZE, EQ_SIZE, EQ_SIZE],
        result_headline="$R(%.2f)=%.3f$" % (maturity, zero_n * 100) + "%",
    ))

    return _render_two_top_one_bottom(
        steps, "Bootstrapping in action: one worked example per instrument", path)


def plot_forward_process(curve, t1, t2, date1, date2, path="output/forward_process.png"):
    """One worked example: derive the forward rate for a single accrual
    period from the two zero-curve points either side of it -- the same
    calculation the floating leg needs for every period of a swap."""
    df1, df2 = curve.df(t1), curve.df(t2)
    fwd = curve.forward(t1, t2)

    step = dict(
        name="Zero curve -> forward rate",
        color=SEGMENT_COLORS["future"],
        col_labels=["Date", "Zero %", "DF"],
        table_rows=[
            [date1, f"{curve.zero(t1) * 100:.4f}%", f"{df1:.6f}"],
            [date2, f"{curve.zero(t2) * 100:.4f}%", f"{df2:.6f}"],
        ],
        highlight="all",
        eq_lines=[
            r"$F(t_1,\,t_2)\;=\;\dfrac{DF(t_1)\,/\,DF(t_2)\,-\,1}{\,t_2-t_1\,}$",
            r"$F\;=\;\dfrac{%.6f\,/\,%.6f\,-\,1}{\,%.4f-%.4f\,}$" % (df1, df2, t2, t1),
        ],
        eq_sizes=[EQ_SIZE, EQ_SIZE],
        result_headline="$F=%.4f$" % (fwd * 100) + "%",
    )
    # this plot's fractions run a bit taller than most, so it gets a little
    # extra vertical gap between lines relative to the shared default
    return _render_single_step(step, "From the zero curve to a forward rate", path,
                                eq_line_h=PROC_EQ_LINE_H * 1.3)


def _money(x):
    return f"{x:,.2f}"


def plot_swap_cashflow_process(row, tau, df, notional, path="output/swap_process.png"):
    """One worked example: price a single swap period's fixed and floating
    cashflows off the curve, side by side, and net them -- the same
    computation `pricing/price.py` repeats for every row of the CSV."""
    fixed_step = dict(
        name="Fixed leg", color=SEGMENT_COLORS["deposit"],
        col_labels=["Known", "Value"],
        table_rows=[
            ["Notional", _money(notional)],
            ["Fixed rate", f"{row['fixed_rate'] * 100:.4f}%"],
            [r"$\tau$ (Act/360)", f"{tau:.4f}"],
        ],
        highlight="none",
        eq_lines=[
            r"$CF=N\,R\,\tau\quad\Rightarrow\quad PV=CF\times DF$",
            r"$PV=(%s\times%.4f\times%.4f)\times%.6f$"
            % (_money(notional), row["fixed_rate"], tau, df),
        ],
        eq_sizes=[EQ_SIZE, EQ_SIZE],
        result_headline="$PV=%s$" % _money(row["fixed_disc_cf"]),
    )

    floating_step = dict(
        name="Floating leg", color=SEGMENT_COLORS["future"],
        col_labels=["Known", "Value"],
        table_rows=[
            ["Notional", _money(notional)],
            ["Forward rate (curve)", f"{row['floating_rate'] * 100:.4f}%"],
            [r"$\tau$ (Act/360)", f"{tau:.4f}"],
        ],
        highlight="none",
        eq_lines=[
            r"$CF=N\,F\,\tau\quad\Rightarrow\quad PV=CF\times DF$",
            r"$PV=(%s\times%.4f\times%.4f)\times%.6f$"
            % (_money(notional), row["floating_rate"], tau, df),
        ],
        eq_sizes=[EQ_SIZE, EQ_SIZE],
        result_headline="$PV=%s$" % _money(row["floating_disc_cf"]),
    )

    net_step = dict(
        name="Net for this period", color=SEGMENT_COLORS["swap"],
        col_labels=["Leg", "PV"],
        table_rows=[
            ["Fixed leg", _money(row["fixed_disc_cf"])],
            ["Floating leg", _money(row["floating_disc_cf"])],
        ],
        highlight="none",
        eq_lines=[
            r"$\mathrm{Difference}=PV_{float}-PV_{fixed}$",
            r"$=%s-%s=%s$" % (_money(row["floating_disc_cf"]), _money(row["fixed_disc_cf"]),
                               _money(row["difference"])),
        ],
        eq_sizes=[EQ_SIZE, EQ_SIZE],
        result_headline=r"$\mathrm{Diff}=%s$" % _money(row["difference"]),
    )

    steps = [fixed_step, floating_step, net_step]
    title = f"Pricing one swap period ({row['payment_date']}) -- full schedule in the output CSV"
    return _render_two_top_one_bottom(steps, title, path)


def plot_table(rows, path="output/table.png", title="Bootstrapped curve nodes",
               label_col="Maturity (yrs)"):
    """Render label / zero rate / discount factor / forward rate for a list
    of curve points.

    `rows` is any iterable of (label, zero_rate_fraction, discount_factor,
    forward_rate_fraction) -- label is rendered as-is, so callers can pass
    either a float maturity or a payment date string (a specific swap's
    schedule)."""
    rows = list(rows)
    n_rows = len(rows) + 1  # + header

    # Size the figure to the table's actual content instead of relying on
    # loc="center" (which centers the table inside a much taller axes,
    # leaving equal dead space above and below it) -- here the axes is built
    # to exactly the table's height, so there's nothing left to be empty.
    row_h = 0.34
    title_h = 0.55
    margin_top, margin_bottom = 0.12, 0.12
    margin_left, margin_right = 0.7, 0.7
    table_w = 7.0

    fig_w = table_w + margin_left + margin_right
    table_h = n_rows * row_h
    fig_h = title_h + table_h + margin_top + margin_bottom

    fig = plt.figure(figsize=(fig_w, fig_h))
    ax = fig.add_axes((margin_left / fig_w, margin_bottom / fig_h,
                        table_w / fig_w, table_h / fig_h))
    ax.axis("off")

    col_labels = [label_col, "Zero rate (%)", "Discount factor", "Forward rate (%)"]
    cell_text = [[str(label), f"{z * 100.0:.4f}", f"{df:.6f}", f"{fwd * 100.0:.4f}"]
                 for label, z, df, fwd in rows]

    table = ax.table(
        cellText=cell_text,
        colLabels=col_labels,
        cellLoc="center",
        loc="center",
        bbox=[0, 0, 1, 1],
    )
    table.auto_set_font_size(False)
    table.set_fontsize(9)

    for (row, _col), cell in table.get_celld().items():
        cell.set_edgecolor("#dddddd")
        if row == 0:
            cell.set_facecolor("#1f4e79")
            cell.set_text_props(color="white", weight="bold")
        else:
            cell.set_facecolor("#f2f2f2" if row % 2 == 0 else "white")

    fig.suptitle(title, y=(margin_bottom + table_h + title_h * 0.55) / fig_h, fontsize=13)
    fig.savefig(path, dpi=130)
    return path
