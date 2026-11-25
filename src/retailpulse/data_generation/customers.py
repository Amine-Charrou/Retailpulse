"""Generate synthetic customer master data for RetailPulse."""

from __future__ import annotations

import random
from datetime import timedelta

import pandas as pd

from retailpulse.configuration import AppSettings, load_settings

FIRST_NAMES = [
    "Amine", "Salma", "Youssef", "Lina", "Omar",
    "Sara", "Mehdi", "Nour", "Karim", "Aya",
    "Hassan", "Meryem", "Adam", "Imane", "Anas",
    "Khadija", "Rayan", "Hiba", "Sami", "Leila",
]

LAST_NAMES = [
    "Alaoui", "Bennani", "Idrissi", "Amrani", "Tazi",
    "Fassi", "El Mansouri", "Berrada", "Chraibi", "Lahlou",
    "Ziani", "Kettani", "Benali", "Saidi", "Tahiri",
]

CUSTOMER_CITIES = [
    "Casablanca",
    "Rabat",
    "Marrakech",
    "Agadir",
    "Tangier",
]

CUSTOMER_SEGMENTS = ["Standard", "Silver", "Gold", "Premium"]
LOYALTY_STATUSES = ["Not Enrolled", "Enrolled"]


def generate_customers(settings: AppSettings | None = None) -> pd.DataFrame:
    """Generate reproducible synthetic customer records."""
    settings = settings or load_settings()
    rng = random.Random(settings.generator.seed + 2)

    start_date = settings.generator.start_date
    end_date = settings.generator.end_date
    date_range_days = (end_date - start_date).days

    rows = []

    for customer_number in range(1, settings.generator.customer_count + 1):
        registration_date = start_date + timedelta(
            days=rng.randint(0, date_range_days)
        )

        rows.append(
            {
                "customer_id": f"CUST-{customer_number:06d}",
                "customer_name": (
                    f"{rng.choice(FIRST_NAMES)} "
                    f"{rng.choice(LAST_NAMES)}"
                ),
                "segment": rng.choices(
                    CUSTOMER_SEGMENTS,
                    weights=[60, 22, 13, 5],
                    k=1,
                )[0],
                "city": rng.choice(CUSTOMER_CITIES),
                "loyalty_status": rng.choices(
                    LOYALTY_STATUSES,
                    weights=[35, 65],
                    k=1,
                )[0],
                "registration_date": registration_date,
                "is_active": rng.choices(
                    [True, False],
                    weights=[95, 5],
                    k=1,
                )[0],
            }
        )

    return pd.DataFrame(rows)
