# Long end of the curve, solved from par swap rates

def add_swaps(curve, swaps):
    for maturity, rate, freq in swaps:
        tau = 1.0 / freq
        n = round(maturity * freq)
        pay_times = [i * tau for i in range(1, n + 1)]

        # Bootstrapping step; read previous rate from curve to get this one
        annuity_known = sum(tau * curve.df(t) for t in pay_times[:-1])
        df_n = (1.0 - rate * annuity_known) / (1.0 + rate * tau)
        curve.add_node_from_df(maturity, df_n)