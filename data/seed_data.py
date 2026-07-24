# data/seed_data.py
"""
Synthetic market quotes in the spirit of Hull's bootstrapping example.
"""

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