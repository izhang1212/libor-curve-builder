# data/seed_data.py
"""
Synthetic market quotes in the spirit of Hull's bootstrapping example.
"""
from datetime import date

# LIBOR deposits: (maturity in years, simple annual rate, Act/360)
DEPOSITS = [
    (1 / 12, 0.0450),
    (3 / 12, 0.0460),
]

# Eurodollar futures: (accrual start, accrual end, quoted price)
# Contiguous 3M contracts picking up where the 3M deposit ends.
FUTURES = [
    (0.25, 0.50, 95.30),
    (0.50, 0.75, 95.20),
    (0.75, 1.00, 95.10),
    (1.00, 1.25, 95.05),
    (1.25, 1.50, 95.00),
    (1.50, 1.75, 94.97),
    (1.75, 2.00, 94.95),
]

# Par swap rates: (maturity in years, par rate, payments per year)
SWAPS = [
    (3.0, 0.0500, 2),
    (4.0, 0.0505, 2),
    (5.0, 0.0510, 2),
    (7.0, 0.0515, 2),
    (10.0, 0.0520, 2),
]

VALUATION_DATE = date(2026, 1, 1)

SWAP = {
    "notional": 10_000_000.0,     # 10mm
    "fixed_rate": 0.0520,         # the fixed leg's rate (annual)
    "frequency": 2,               # payments per year (semiannual)
    "start": date(2026, 1, 1),    # accrual begins
    "end": date(2031, 1, 1),      # 5-year swap
    "pov": "payer",               # "payer" pays fixed / receives floating; sets the sign of the net
}