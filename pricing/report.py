# Build the CSV output
    # One row per payment date, with both legs' rate, cf, discouted cf, and net

import csv

COLUMNS = [
    ("payment_date", "payment date"),
    ("fixed_rate", "fixed rate"),
    ("fixed_cf", "fixed cf"),
    ("fixed_disc_cf", "fixed disc cf"),
    ("floating_rate", "floating rate"),
    ("floating_cf", "floating cf"),
    ("floating_disc_cf", "floating disc cf"),
    ("difference", "difference (float - fixed)"),
]


def _fmt(key, value):
    if key == "payment_date":
        return value.isoformat()
    if key.endswith("_rate"):
        return f"{value*100:.4f}%"
    return f"{value:.2f}"


def write_csv(rows, summary, path):
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(label for _, label in COLUMNS)
        for r in rows:
            w.writerow(_fmt(key, r[key]) for key, _ in COLUMNS)

        w.writerow([])
        w.writerow(["fixed leg PV", f"{summary['fixed_pv']:.2f}"])
        w.writerow(["floating leg PV", f"{summary['floating_pv']:.2f}"])
        w.writerow([f"net ({summary['pov']})", f"{summary['net']:.2f}"])
    return path