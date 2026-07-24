from bootstrap.curve import ZeroCurve
from bootstrap.deposit import add_deposit
from bootstrap.future import add_futures
from bootstrap.swap import add_swaps

# Bootstrap top to bottom
def bootstrap(deposits, futures, swaps):
    curve = ZeroCurve()
    add_deposit(curve, deposits)
    add_futures(curve, futures)
    add_swaps(curve, swaps)

    return curve
