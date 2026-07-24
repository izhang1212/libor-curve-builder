# Middle of curve
    # Eurodollar futures fixes a forward rate over its accural window [t1, t2]
    # futures rate = (100 - price) / 100, and uses the DC convention ACT/360
# Eurodollar futures are determined and settled at t1, but payed as if they were at t2 (discounting to PV)

from conventions.daycount import DayCount, year_fraction

def add_futures(curve, futures):

    for t1, t2, price in futures:
        f_rate = (100.0 - price) / 100
        tau = year_fraction(t1, t2, DayCount.ACT_360)
        # Bootstrapping step; read previous rate from curve to get this one
        df_t2 = curve.df(t1) / (1.0 + f_rate * tau)
        curve.add_node_from_df(t2, df_t2)