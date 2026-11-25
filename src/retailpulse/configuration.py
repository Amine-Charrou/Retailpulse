
from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config" / "settings.toml"


@dataclass(frozen=True)
class GeneratorSettings:
    seed: int
    start_date: date
    end_date: date
    store_count: int
    product_count: int
    customer_count: int
    supplier_count: int


@dataclass(frozen=True)
class DataSettings:
    root: Path
    raw: Path
    processed: Path
    generated: Path


@dataclass(frozen=True)
class DatabricksSettings:
    catalog: str
    bronze_schema: str
    silver_schema: str
    gold_schema: str


@dataclass(frozen=True)
class AppSettings:
    project_name: str
    environment: str
    generator: GeneratorSettings
    data: DataSettings
    databricks: DatabricksSettings


def _resolve_path(value: str, project_root: Path) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = project_root / path
    return path.resolve()


def load_settings(
    config_path: Path = DEFAULT_CONFIG_PATH,
) -> AppSettings:
    """Load application settings from TOML and environment overrides."""
    with config_path.open("rb") as config_file:
        raw: dict[str, Any] = tomllib.load(config_file)

    project = raw["project"]
    data = raw["data"]
    generator = raw["generator"]
    databricks = raw["databricks"]

    project_root = config_path.resolve().parent.parent

    environment = os.getenv(
        "RETAILPULSE_ENV",
        project["environment"],
    )

    data_root_value = os.getenv(
        "RETAILPULSE_DATA_ROOT",
        data["root"],
    )
    data_root = _resolve_path(data_root_value, project_root)

    start_date = date.fromisoformat(generator["start_date"])
    end_date = date.fromisoformat(generator["end_date"])

    if start_date > end_date:
        raise ValueError("Generator start_date must be on or before end_date")

    counts = {
        "store_count": int(generator["store_count"]),
        "product_count": int(generator["product_count"]),
        "customer_count": int(generator["customer_count"]),
        "supplier_count": int(generator["supplier_count"]),
    }

    if any(value <= 0 for value in counts.values()):
        raise ValueError("All generator counts must be positive integers")

    return AppSettings(
        project_name=project["name"],
        environment=environment,
        generator=GeneratorSettings(
            seed=int(generator["seed"]),
            start_date=start_date,
            end_date=end_date,
            **counts,
        ),
        data=DataSettings(
            root=data_root,
            raw=_resolve_path(data["raw"], project_root),
            processed=_resolve_path(data["processed"], project_root),
            generated=_resolve_path(data["generated"], project_root),
        ),
        databricks=DatabricksSettings(
            catalog=os.getenv(
                "RETAILPULSE_DATABRICKS_CATALOG",
                databricks["catalog"],
            ),
            bronze_schema=databricks["bronze_schema"],
            silver_schema=databricks["silver_schema"],
            gold_schema=databricks["gold_schema"],
        ),
    )
