"""Unit tests for the synthetic supplier generator."""

from retailpulse.configuration import load_settings
from retailpulse.data_generation.suppliers import generate_suppliers


def test_supplier_generator_returns_configured_count() -> None:
    suppliers = generate_suppliers()
    settings = load_settings()

    assert len(suppliers) == settings.generator.supplier_count


def test_supplier_ids_are_unique() -> None:
    suppliers = generate_suppliers()

    assert suppliers["supplier_id"].is_unique


def test_supplier_generator_is_reproducible() -> None:
    first = generate_suppliers()
    second = generate_suppliers()

    assert first.equals(second)


def test_supplier_categories_are_valid() -> None:
    suppliers = generate_suppliers()

    expected_categories = {
        "Grocery",
        "Beverages",
        "Dairy",
        "Personal Care",
        "Household",
        "Fresh Food",
    }

    assert set(suppliers["product_category"]).issubset(expected_categories)


def test_supplier_lead_times_and_payment_terms_are_valid() -> None:
    suppliers = generate_suppliers()

    assert suppliers["lead_time_days"].between(1, 14).all()
    assert suppliers["payment_terms_days"].isin([15, 30, 45, 60]).all()


def test_supplier_records_have_required_columns() -> None:
    suppliers = generate_suppliers()

    expected_columns = {
        "supplier_id",
        "supplier_name",
        "city",
        "product_category",
        "payment_terms_days",
        "lead_time_days",
        "is_active",
    }

    assert expected_columns.issubset(suppliers.columns)
