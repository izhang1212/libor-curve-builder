# Continuous-compounding conversions between zero rates and discount factors.

import math

# Discount factor or a zero rate (continously compounding)
    # df = e^(-r*t)
def df_from_zero(rate: float, t: float) -> float:
    return math.exp(-rate * t)

# Continously compounded zero rate implied by a discount factor
    # r = - ln(df) / t
def zero_from_df(df: float, t: float) -> float:
    """Continuously compounded zero rate implied by a discount factor."""
    return -math.log(df) / t