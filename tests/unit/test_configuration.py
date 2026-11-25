
from pathlib import Path

import pytest

from retailpulse.configuration import load_settings


def test_load_default_settings() -> None:
    settings = load_settings()

    assert settings.project_name == "RetailPulse"
    assert settings.generator.seed == 42
    assert settings.generator.store_count == 15
    assert settings.generator.start_date.isoformat() == "2025-01-01"
    assert settings.generator.end_date.isoformat() == "2026-11-24"
    assert settings.databricks.bronze_schema == "bronze"


def test_load_settings_with_environment_override(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setenv("RETAILPULSE_ENV", "test")
    monkeypatch.setenv("RETAILPULSE_DATA_ROOT", str(tmp_path / "retail_data"))

    settings = load_settings()

    assert settings.environment == "test"
    assert settings.data.root == (tmp_path / "retail_data").resolve()


def test_invalid_date_range_raises_error(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "settings.toml"
    config_path.write_text(
        """
[project]
name = "RetailPulse"
environment = "local"

[data]
root = "data"
raw = "data/raw"
processed = "data/processed"
generated = "data/generated"

[generator]
seed = 42
start_date = "2026-11-24"
end_date = "2025-01-01"
store_count = 15
product_count = 500
customer_count = 10000
supplier_count = 50

[databricks]
catalog = "retailpulse"
bronze_schema = "bronze"
silver_schema = "silver"
gold_schema = "gold"
""",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="start_date"):
        load_settings(config_path)
