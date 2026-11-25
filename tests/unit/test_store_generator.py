"""Unit tests for the synthetic store generator."""

from retailpulse.configuration import load_settings
from retailpulse.data_generation.stores import generate_stores


def test_store_generator_returns_configured_number_of_stores() -> None:
    stores = generate_stores()

    settings = load_settings()

    assert len(stores) == settings.generator.store_count


def test_store_ids_are_unique() -> None:
    stores = generate_stores()

    assert stores["store_id"].is_unique


def test_stores_use_expected_cities() -> None:
    stores = generate_stores()

    expected_cities = {
        "Casablanca",
        "Rabat",
        "Marrakech",
        "Agadir",
        "Tangier",
    }

    assert set(stores["city"]) == expected_cities


def test_store_generator_is_reproducible() -> None:
    first = generate_stores()
    second = generate_stores()

    assert first.equals(second)


def test_store_records_have_required_columns() -> None:
    stores = generate_stores()

    expected_columns = {
        "store_id",
        "store_name",
        "city",
        "region",
        "store_type",
        "opening_date",
        "is_active",
    }

    assert expected_columns.issubset(stores.columns)
