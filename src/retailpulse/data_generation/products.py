"""Generate synthetic product master data for RetailPulse."""

from __future__ import annotations

import random
from datetime import date, timedelta

import pandas as pd

from retailpulse.configuration import AppSettings, load_settings

PRODUCT_CATALOG = {
    "Grocery": {
        "subcategories": ["Rice", "Pasta", "Canned Food", "Cooking Oil"],
        "brands": ["Atlas Foods", "Mina", "Dari", "Safi"],
        "price_range": (5.0, 80.0),
    },
    "Beverages": {
        "subcategories": ["Water", "Juice", "Soda", "Coffee"],
        "brands": ["Sirocco", "Oasis", "Nespresso", "Coca-Cola"],
        "price_range": (3.0, 45.0),
    },
    "Dairy": {
        "subcategories": ["Milk", "Yogurt", "Cheese", "Butter"],
        "brands": ["Jaouda", "Centrale Danone", "Jibal", "Président"],
        "price_range": (4.0, 60.0),
    },
    "Personal Care": {
        "subcategories": ["Shampoo", "Soap", "Oral Care", "Skin Care"],
        "brands": ["Nivea", "Dove", "Colgate", "Garnier"],
        "price_range": (8.0, 120.0),
    },
    "Household": {
        "subcategories": ["Laundry", "Cleaning", "Paper Products", "Kitchen"],
        "brands": ["Ariel", "Omo", "Sanytol", "Mouchoirs"],
        "price_range": (6.0, 150.0),
    },
    "Fresh Food": {
        "subcategories": ["Fruit", "Vegetables", "Meat", "Bakery"],
        "brands": ["Local Supplier", "Farm Fresh", "RetailPulse Fresh"],
        "price_range": (4.0, 100.0),
    },
}

UNIT_BY_SUBCATEGORY = {
    "Fruit": "kg",
    "Vegetables": "kg",
    "Meat": "kg",
    "Bakery": "unit",
}


def generate_products(settings: AppSettings | None = None) -> pd.DataFrame:
    """Generate reproducible synthetic product records."""
    settings = settings or load_settings()
    rng = random.Random(settings.generator.seed + 1)

    categories = list(PRODUCT_CATALOG)
    rows = []

    for product_number in range(1, settings.generator.product_count + 1):
        category = categories[(product_number - 1) % len(categories)]
        catalog = PRODUCT_CATALOG[category]

        subcategory = rng.choice(catalog["subcategories"])
        brand = rng.choice(catalog["brands"])

        min_price, max_price = catalog["price_range"]
        unit_price = round(rng.uniform(min_price, max_price), 2)

        cost_ratio = rng.uniform(0.55, 0.85)
        unit_cost = round(unit_price * cost_ratio, 2)
        gross_margin_pct = round(
            ((unit_price - unit_cost) / unit_price) * 100,
            2,
        )

        launch_start = date(2020, 1, 1)
        launch_end = date(2025, 1, 1)
        launch_days = (launch_end - launch_start).days
        launch_date = launch_start + timedelta(
            days=rng.randint(0, launch_days)
        )

        rows.append(
            {
                "product_id": f"PROD-{product_number:05d}",
                "sku": f"SKU-{product_number:06d}",
                "product_name": f"{subcategory} {brand} {product_number:03d}",
                "category": category,
                "subcategory": subcategory,
                "brand": brand,
                "unit_of_measure": UNIT_BY_SUBCATEGORY.get(subcategory, "unit"),
                "unit_price_mad": unit_price,
                "unit_cost_mad": unit_cost,
                "gross_margin_pct": gross_margin_pct,
                "launch_date": launch_date,
                "is_active": True,
            }
        )

    return pd.DataFrame(rows)
