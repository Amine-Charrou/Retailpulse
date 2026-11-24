# RetailPulse — Business Case

**Project:** RetailPulse
**Version:** 1.0
**Status:** Initial business definition
**Industry:** Retail / Supermarket
**Market:** Morocco

## 1. Executive Summary

RetailPulse is an end-to-end retail data engineering and analytics platform designed around a simulated Moroccan supermarket chain operating across multiple cities.

The platform aims to consolidate data from different operational domains, process historical and near-real-time information, enforce data quality, and transform raw operational records into reliable analytical datasets.

The project will use a modern Lakehouse architecture based on Databricks, Apache Spark, PySpark and Delta Lake.

## 2. Business Scenario

The simulated company operates 15 supermarket stores across five Moroccan cities:

- Casablanca
- Rabat
- Marrakech
- Agadir
- Tangier

Its operations generate data from point-of-sale transactions, inventory management, product catalogs, customer records, suppliers and purchase orders.

As the company grows, management needs a centralized analytical platform to understand business performance across stores and operational domains.

RetailPulse will simulate this environment using reproducible synthetic data.

## 3. Business Problems

The company faces several analytical challenges:

1. **Fragmented data:** Information is distributed across different operational sources.
2. **Limited sales visibility:** Management lacks a unified view of revenue and sales performance.
3. **Inventory inefficiency:** Stock shortages and excess inventory are difficult to identify consistently.
4. **Supplier performance:** Delivery delays and supplier reliability need systematic measurement.
5. **Limited customer insights:** Purchasing patterns, customer frequency and retention are not sufficiently analyzed.
6. **Delayed reporting:** Historical reporting alone cannot provide timely visibility into recent business activity.
7. **Data reliability:** Inconsistent records, duplicates and missing values can undermine business decisions.

## 4. Project Objectives

RetailPulse aims to:

- Centralize retail data in a Lakehouse platform.
- Implement reliable batch and streaming ingestion.
- Establish Bronze, Silver and Gold data layers.
- Improve data quality through automated validation.
- Build analytical models for sales, inventory, suppliers and customers.
- Enable consistent business KPI calculation.
- Support reproducible processing and pipeline monitoring.

## 5. Analytical Domains

### 5.1 Sales Analytics — Core

Analyze revenue, transactions, average basket value, product performance, store performance and seasonal sales patterns.

### 5.2 Inventory Analytics — Core

Analyze stock levels, stockout rates, inventory turnover, inventory availability and replenishment needs.

### 5.3 Supplier Analytics — Core

Measure supplier delivery performance, purchase order fulfillment, delivery delays and lead times.

### 5.4 Customer Analytics — Secondary

Understand purchasing behavior through customer segmentation, RFM analysis, purchase frequency, retention and estimated customer lifetime value.

Customer records will be synthetically generated. No real personal customer information will be required.

## 6. Stakeholders

| Stakeholder | Main interest |
|---|---|
| Executive management | Overall business performance |
| Sales managers | Revenue and sales trends |
| Store managers | Store performance and inventory |
| Inventory managers | Stock availability and replenishment |
| Procurement managers | Supplier and purchase order performance |
| Marketing analysts | Customer behavior and segmentation |
| Data engineering team | Reliable ingestion and transformation |
| Data analysts | Trusted analytical datasets |

## 7. Business KPIs

| KPI | Definition |
|---|---|
| Net Revenue | Sales revenue after discounts and returns, under the agreed accounting convention |
| Transaction Count | Number of qualifying completed transactions |
| Average Basket Value | Net revenue divided by qualifying transaction count |
| Stockout Rate | Stockout observations divided by eligible inventory observations |
| Inventory Turnover | Cost of goods sold divided by average inventory value |
| Days of Inventory | Average inventory value divided by average daily cost of goods sold |
| On-Time Delivery Rate | Purchase order lines delivered on or before the expected date divided by eligible delivered lines |
| Average Lead Time | Average elapsed time between purchase order placement and delivery |
| Customer Purchase Frequency | Average qualifying transactions per identified customer |
| Customer Retention Rate | Percentage of eligible customers returning within a defined measurement period |

All KPI formulas, treatment of returns, cancellations, taxes and missing records will be formally defined in the technical and functional specifications.

## 8. Project Scope

### In Scope

- Synthetic Moroccan retail data generation.
- Historical batch processing.
- Incremental streaming simulation.
- Bronze, Silver and Gold architecture.
- Delta Lake storage.
- Data quality validation and quarantine.
- Dimensional modeling.
- Sales, inventory, supplier and customer analytics.
- Pipeline monitoring and automated tests.
- Business-oriented dashboards.

### Out of Scope

- Replacing operational POS systems.
- Managing real payment transactions.
- Production inventory management.
- Processing real customer personal information.
- Deploying a production ERP system.

## 9. Success Criteria

The project will be considered successful when it demonstrates:

1. Reproducible synthetic retail data generation.
2. Successful historical batch ingestion.
3. Incremental streaming ingestion with checkpointing and recovery.
4. Reliable Bronze-to-Silver-to-Gold transformations.
5. Automated data quality controls and rejected-record handling.
6. Consistent analytical models and documented KPIs.
7. Automated tests and pipeline monitoring.
8. Reproducible setup and comprehensive technical documentation.

## 10. Key Assumptions

- The retail business and its operational records are simulated.
- Synthetic data will follow realistic retail business rules.
- The platform will initially be developed within the capabilities of Databricks Free Edition, subject to feature availability.
- Historical and streaming workloads will share consistent data contracts.
- The architecture will favor modularity, reproducibility and maintainability.

## 11. Expected Outcome

RetailPulse will demonstrate how a modern Lakehouse platform can transform fragmented retail operational data into reliable, business-oriented analytical information.

The project is intended to showcase advanced data engineering practices through a realistic Moroccan retail business scenario.
