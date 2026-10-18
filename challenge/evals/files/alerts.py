# Fictional late-parcel alert job for Parcel Pal.
from datetime import timedelta

LATE_THRESHOLD = timedelta(hours=4)


def find_late(parcels, now):
    return [p for p in parcels if now - p["expected_at"] > LATE_THRESHOLD and not p["received"]]


def run(parcels, now, notify):
    for p in find_late(parcels, now):
        notify(f"Parcel {p['tracking']} ({p['carrier']}) is late")
