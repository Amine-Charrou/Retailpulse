"""Generate synthetic supplier master data for RetailPulse."""

from __future__ import annotations

import random

import pandas as pd

from retailpulse.configuration import AppSettings, load_settings

SUPPLIER_CITIES = [
    "Casablanca",
    "Rabat",
    "Marrakech",
    "Agadir",
    "Tangier",
    "Fes",
    "Meknes",
    "Oujda",
]

PRODUCT_CATEGORIES = [
    "Grocery",
    "Beverages",
    "Dairy",
    "Personal Care",
    "Household",
    "Fresh Food",
]

SUPPLIER_PREFIXES = [
    "Atlas",
    "Maghreb",
    "Sahara",
    "Rif",
    "Oasis",
    "Medina",
    "Amazigh",
    "Coastal",
    "Royal",
    "Green",
    "Central",
    "Northern",
    "Southern",
    "Premium",
    "Golden",
]

SUPPLIER_SUFFIXES = [
    "Distribution",
    "Trading",
    "Foods",
    "Wholesale",
    "Supply",
    "Products",
    "Industries",
    "Logistics",
]


def generate_suppliers(settings: AppSettings | None = None) -> pd.DataFrame:
    """Generate reproducible synthetic supplier records."""
    settings = settings or load_settings()
    rng = random.Random(settings.generator.seed + 3)

    rows = []

    for supplier_number in range(1, settings.generator.supplier_count + 1):
        rows.append(
            {
                "supplier_id": f"SUP-{supplier_number:04d}",
                "supplier_name": (
                    f"{rng.choice(SUPPLIER_PREFIXES)} "
                    f"{rng.choice(SUPPLIER_SUFFIXES)} "
                    f"{supplier_number:03d}"
                ),
                "city": rng.choice(SUPPLIER_CITIES),
                "product_category": rng.choice(PRODUCT_CATEGORIES),
                "payment_terms_days": rng.choice([15, 30, 45, 60]),
                "lead_time_days": rng.randint(1, 14),
                "is_active": rng.choices(
                    [True, False],
                    weights=[95, 5],
                    k=1,
                )[0],
            }
        )

    return pd.DataFrame(rows)
