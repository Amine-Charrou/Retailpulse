"""Generate synthetic store master data for RetailPulse."""

from __future__ import annotations

import random
from datetime import date, timedelta

import pandas as pd

from retailpulse.configuration import AppSettings, load_settings

CITIES = {
    "Casablanca": "Casablanca-Settat",
    "Rabat": "Rabat-Salé-Kénitra",
    "Marrakech": "Marrakech-Safi",
    "Agadir": "Souss-Massa",
    "Tangier": "Tanger-Tétouan-Al Hoceïma",
}

STORE_TYPES = ("Supermarket", "Express", "Hypermarket")


def generate_stores(settings: AppSettings | None = None) -> pd.DataFrame:
    """Generate reproducible synthetic store records."""
    settings = settings or load_settings()
    rng = random.Random(settings.generator.seed)

    rows = []
    city_names = list(CITIES)

    for store_number in range(1, settings.generator.store_count + 1):
        city = city_names[(store_number - 1) % len(city_names)]
        opening_start = date(2018, 1, 1)
        opening_end = date(2025, 1, 1)
        days_between = (opening_end - opening_start).days
        opening_date = opening_start + timedelta(
            days=rng.randint(0, days_between)
        )

        rows.append(
            {
                "store_id": f"STORE-{store_number:03d}",
                "store_name": f"RetailPulse {city} {store_number:02d}",
                "city": city,
                "region": CITIES[city],
                "store_type": rng.choice(STORE_TYPES),
                "opening_date": opening_date,
                "is_active": True,
            }
        )

    return pd.DataFrame(rows)
