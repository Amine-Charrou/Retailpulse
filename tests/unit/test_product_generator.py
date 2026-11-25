"""Unit tests for the synthetic product generator."""

from retailpulse.configuration import load_settings
from retailpulse.data_generation.products import generate_products


def test_product_generator_returns_configured_number_of_products() -> None:
    products = generate_products()
    settings = load_settings()

    assert len(products) == settings.generator.product_count


def test_product_ids_and_skus_are_unique() -> None:
    products = generate_products()

    assert products["product_id"].is_unique
    assert products["sku"].is_unique


def test_product_generator_is_reproducible() -> None:
    first = generate_products()
    second = generate_products()

    assert first.equals(second)


def test_product_prices_and_costs_are_positive() -> None:
    products = generate_products()

    assert (products["unit_price_mad"] > 0).all()
    assert (products["unit_cost_mad"] > 0).all()


def test_product_cost_is_below_selling_price() -> None:
    products = generate_products()

    assert (products["unit_cost_mad"] < products["unit_price_mad"]).all()


def test_product_categories_cover_catalog() -> None:
    products = generate_products()

    assert set(products["category"]) == {
        "Grocery",
        "Beverages",
        "Dairy",
        "Personal Care",
        "Household",
        "Fresh Food",
    }
