# HungerLib's simple snap scheduler
from datetime import datetime, timedelta

def snapSchedule(minimumMinutes=30, snapMinutes=(0, 30)):
    now = datetime.now()
    minimum = now + timedelta(minutes=minimumMinutes)
    snapMinutes = sorted(snapMinutes)

    for snap in snapMinutes:
        if minimum.minute < snap:
            scheduled = minimum.replace(minute=snap, second=0, microsecond=0)
            break
    else:
        scheduled = (minimum.replace(minute=0, second=0, microsecond=0)
                     + timedelta(hours=1))

    return {
        "now": now,
        "minimum": minimum,
        "scheduled": scheduled,
        "formatted": scheduled.strftime("%I:%M %p")
    }


def secsUntil(target):
    now = datetime.now()
    return int((target - now).total_seconds())


def minsUntil(target):
    now = datetime.now()
    return int((target - now).total_seconds()) // 60
