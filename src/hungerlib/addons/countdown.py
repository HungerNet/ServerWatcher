import time
from datetime import datetime

# Special use case helper functions that operate on server objects
def runCountdownEvents(
    target_time,
    minute_callbacks=None,
    second_callbacks=None,
    tick_interval=1
):
    """
    A simple, readable countdown engine.

    - Counts down until `target_time`
    - When the countdown hits a configured minute mark, it runs that callback
    - When the countdown hits a configured second mark, it runs that callback

    Parameters:
        target_time (datetime):
            The time we are counting down to.

        minute_callbacks (dict[int, callable]):
            Example: {5: func, 1: func}

        second_callbacks (dict[int, callable]):
            Example: {10: func, 5: func, 1: func}

        tick_interval (int):
            How often to check the countdown (in seconds).
    """

    # Default to empty dicts if none provided
    minute_callbacks = minute_callbacks or {}
    second_callbacks = second_callbacks or {}

    # Track which events we've already fired
    fired_minutes = set()
    fired_seconds = set()

    while True:
        now = datetime.now()
        seconds_left = int((target_time - now).total_seconds())
        minutes_left = seconds_left // 60

        # Countdown finished
        if seconds_left <= 0:
            return

        # Fire minute-based events
        if minutes_left in minute_callbacks and minutes_left not in fired_minutes:
            fired_minutes.add(minutes_left)
            minute_callbacks[minutes_left]()

        # Fire second-based events
        if seconds_left in second_callbacks and seconds_left not in fired_seconds:
            fired_seconds.add(seconds_left)
            second_callbacks[seconds_left]()

        time.sleep(tick_interval)





# ============================================================
# SERVER STATE HELPERS
# ============================================================

def waitForOnline(server, timeout=60, interval=2):
    """
    Wait until the server reports status 'running'.
    Returns True if online before timeout.
    """
    elapsed = 0
    while elapsed < timeout:
        if server.isOnline():
            return True
        time.sleep(interval)
        elapsed += interval
    return False


def waitForOffline(server, timeout=60, interval=2):
    """
    Wait until the server reports status 'offline'.
    Returns True if offline before timeout.
    """
    elapsed = 0
    while elapsed < timeout:
        if server.isOffline():
            return True
        time.sleep(interval)
        elapsed += interval
    return False
