
# RetailPulse

**An end-to-end retail data engineering and analytics platform built with Databricks.**

RetailPulse is a portfolio project simulating the data infrastructure of a Moroccan retail chain. Its goal is to demonstrate how raw retail data can be ingested, transformed, validated, and converted into reliable business insights.

## Business Context

The simulated retail company operates across multiple Moroccan cities, including Casablanca, Rabat, Marrakech, Agadir, and Tangier.

The platform will integrate:

- Point-of-sale transactions
- Product and customer information
- Store inventory
- Suppliers and purchase orders
- Historical and real-time sales events

## Planned Architecture

The project follows the Medallion Architecture:

- **Bronze:** Raw data ingestion.
- **Silver:** Cleaning, validation, deduplication, and integration.
- **Gold:** Business-ready analytical models and KPIs.

Both batch and streaming processing will be implemented.

## Technology Stack

| Area | Technologies |
|---|---|
| Data platform | Databricks |
| Processing | Apache Spark, PySpark, Spark SQL |
| Storage | Delta Lake |
| Ingestion | Batch processing, Auto Loader |
| Streaming | Spark Structured Streaming |
| Data generation | Python, Faker, NumPy |
| Testing | pytest |
| Code quality | Ruff |
| Version control | Git, GitHub |

## Key Business Metrics

The platform is designed to support analysis of:

- Revenue and sales growth
- Average basket value
- Inventory turnover
- Stockout rate
- Supplier delivery performance

## Project Status

**Current stage:** Development environment and repository foundation.

The architecture, data contracts, ingestion pipelines, transformations, and analytics layers are planned for implementation.

## Repository Structure

```text
retailpulse/
├── config/
├── dashboards/
├── data_generator/
├── docs/
├── notebooks/
├── pipelines/
├── sql/
├── src/
└── tests/
```

## Project Goals

This project aims to demonstrate practical data engineering skills through reproducible data generation, reliable pipelines, data quality controls, and business-oriented analytics.
