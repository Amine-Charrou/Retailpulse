"""Unit tests for the synthetic customer generator."""

from retailpulse.configuration import load_settings
from retailpulse.data_generation.customers import generate_customers


def test_customer_generator_returns_configured_count() -> None:
    customers = generate_customers()
    settings = load_settings()

    assert len(customers) == settings.generator.customer_count


def test_customer_ids_are_unique() -> None:
    customers = generate_customers()

    assert customers["customer_id"].is_unique


def test_customer_generator_is_reproducible() -> None:
    first = generate_customers()
    second = generate_customers()

    assert first.equals(second)


def test_customer_cities_are_expected() -> None:
    customers = generate_customers()

    assert set(customers["city"]).issubset(
        {"Casablanca", "Rabat", "Marrakech", "Agadir", "Tangier"}
    )


def test_customer_registration_dates_are_in_configured_range() -> None:
    customers = generate_customers()
    settings = load_settings()

    assert customers["registration_date"].min() >= settings.generator.start_date
    assert customers["registration_date"].max() <= settings.generator.end_date


def test_customer_records_have_required_columns() -> None:
    customers = generate_customers()

    expected_columns = {
        "customer_id",
        "customer_name",
        "segment",
        "city",
        "loyalty_status",
        "registration_date",
        "is_active",
    }

    assert expected_columns.issubset(customers.columns)
