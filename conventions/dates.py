# Convert calender date (1/1/2026) to general, which can then be used to find fractions

from datetime import date

# Years from valuation to target
def year_fraction_to(valuation: date, target: date) -> float:
    return (target - valuation).days / 360.0

# Length, in years, of accural period [start, end]
def accrual_fraction(start: date, end: date) -> float:
    return (end - start).days / 360.0
