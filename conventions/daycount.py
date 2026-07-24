# Daycount conventions used by instruments

from enum import Enum


class DayCount(Enum):
    # Used by money-market legs (deposits, futures)
    ACT_360 = "ACT/360"
    # Swap fixed legs
    THIRTY_360 = "30/360"


_SCALING = {
    DayCount.ACT_360: 365.0 / 360.0,
    DayCount.THIRTY_360: 1.0,
}

# Accrual factor for the span [t_start, t_end], both in years
def year_fraction(t_start: float, t_end: float, convention: DayCount) -> float:
    return (t_end - t_start) * _SCALING[convention]