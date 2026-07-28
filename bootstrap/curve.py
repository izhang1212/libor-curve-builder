# Zero Curve being built
    # Stores (time, zero-rate) nodes
    # Iterate thorugh instruments (deposit, futures, swaps) to add to it

from conventions.compunding import df_from_zero, zero_from_df

class ZeroCurve:
    def __init__(self):
        # time, zero rate pairs stored in ascending order of time
        self.times = []
        self.zeros = []

    # Insert node while keeping list sorted
    def add_node(self, t, zero_rate):
        i = self.insertion_index(t)
        self.times.insert(i, t)
        self.zeros.insert(i, zero_rate)

    # Add node given discount factor; convert discount factor into zero rate
    def add_node_from_df(self, t, df):
        self.add_node(t, zero_from_df(df, t))

    # Get Cont. Compounded zero rate at time t (use interp since t can be any time, even between nodes)
    def zero(self, t):
        return self.interp_zero(t)

    # Get discount factor at time t
    def df(self, t):
        return df_from_zero(self.interp_zero(t), t)

    # Solved pairs in ascending time
    @property
    def nodes(self):
        return list(zip(self.times, self.zeros))
    
    ######## HELPER METHODS ######################

    # Binary search to find insertion index given t
    def insertion_index(self, t):
        lo, hi = 0, len(self.times)
        while lo < hi:
            mid = (lo + hi) // 2
            if self.times[mid] < t:
                lo = mid + 1
            else:
                hi = mid

        return lo

    # LESSON: Nodes are discrete. However, since the zero-curve is a curve, we connect these nodes under 2 main assumptions:
        # 1. The rate before the first node and after the last node are constant (equal to first node rate before first node, equal to last node rate past last node)
        # 2. The rate between two nodes is linear, with the end points being the two nodes on the left and right
    # We use this so that given any time (even times between nodes like 1.35 is between 1 and 1.5), we can find the zero rate for that time
    def interp_zero(self, t):
        times, zeros = self.times, self.zeros

        # at or beyond ends, hold nearest node flat (assume before first and after last is constant horizontal line)
        if t <= times[0]:
            return zeros[0]
        if t >= times[-1]:
            return zeros[-1]

        # for times between, solve linear
        i = self.insertion_index(t)
        t0, t1 = times[i-1], times[i]
        z0, z1 = zeros[i-1], zeros[i]
        w = (t - t0) / (t1 - t0)
        return z0 + w * (z1-z0)

    # Forward rate over [t1, t2] from discount factors f = (DF(t1) / DF(t2) - 1) / (t2 - t1)
    def forward(self, t1, t2):
        return (self.df(t1) / self.df(t2) - 1.0) / (t2 - t1)