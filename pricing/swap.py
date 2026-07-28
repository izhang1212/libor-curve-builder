# Define swap terms and its payment scheule
    # Holds notional, fixed rate, payment freq, start and end dates, and POV


from datetime import date
from conventions.dates import accrual_fraction, year_fraction_to


class Swap:
    def __init__(self, notional, fixed_rate, freq, start, end, pov="payer"):
        self.notional = notional
        self.fixed_rate = fixed_rate
        self.frequency = freq        
        self.start = start
        self.end = end
        self.pov = pov                    

    # Returns all information of swap (start, end, accural frac of period, and list of payment times) 
    def periods(self, valuation):
        # list of period edges
        boundaries = self.schedule_dates()
        # pair these dates together with start, end, and other information
        out = []
        for start, end in zip(boundaries, boundaries[1:]):
            if end <= valuation:
                continue
            out.append({
                "start": start,
                "end": end,
                "tau": accrual_fraction(start, end),
                "t_pay": year_fraction_to(valuation, end),
            })
        # we get an array of dicts, each of which has a start date, end date, and day info
        return out

    # Takes our start date, end date, and freq, create a list of payment dates for this swap
    def schedule_dates(self):
        step = 12 // self.frequency       # months per period
        dates = [self.start]
        n = 1
        while True:
            nxt = add_months(self.start, step * n)
            # If we hit the last date, add it and stop
            if nxt >= self.end:
                dates.append(self.end)
                break
            dates.append(nxt)
            n += 1
        return dates

# Takes a date, d, and shifts it forward by a whole number of months landing it on the same day-of-month when that day exists
    # e.g. given d = (1/31/2026) and months = 1, we shift forward by one month to get 2/28/2026
def add_months(d, months):
    m = d.month - 1 + months
    year = d.year + m // 12
    month = m % 12 + 1
    # clamp day to the last valid day of the target month
    day = min(d.day, days_in_month(year, month))
    return date(year, month, day)

# Given a month and a year, returns number of days in that month
def days_in_month(year, month):
    # handle speical case of december so it doesn't roll over to next year
    if month == 12:
        return 31
    return (date(year, month + 1, 1) - date(year, month, 1)).days