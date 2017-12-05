from time import time

__all__ = ["is_enough_time_passed"]
timestamp = time()
_interval = 0.01


def is_enough_time_passed() -> bool:
    global timestamp
    if time() - timestamp < _interval:
        return False
    else:
        timestamp = time()
        return True
