# Short end of the curve, built from LIBOR cash deposits

from conventions.daycount import DayCount, year_fraction

# Extend curve with a node per deposit
    # deposists: iterable of (maturity_in_years, simple_rate)
def add_deposit(curve, deposits):
    # For each LIBOR deposit
    for maturity, rate in deposits:
        # tau = year fraction conversion of life span
        tau = year_fraction(0.0, maturity, DayCount.ACT_360)
        # Calculate discount factor
        df = 1.0 / (1.0 + rate * tau)
        curve.add_node_from_df(maturity, df) 