# RetailPulse — Data Contracts

**Version:** 1.0
**Status:** Proposed
**Platform:** Databricks Lakehouse
**Data formats:** CSV, JSON
**Storage format:** Delta Lake

## 1. Purpose

This document defines the data contracts governing the exchange of data between RetailPulse source systems and its ingestion pipelines.

Each contract specifies:

- Dataset identification and ownership.
- File format and expected structure.
- Field names and physical data types.
- Required and optional attributes.
- Primary business identifiers.
- Schema validation rules.
- Business constraints.
- Data quality expectations.
- Schema evolution policies.
- Error handling and quarantine requirements.

The objective is to ensure consistent, reliable, traceable, and reproducible data ingestion.

## 2. Source Systems

RetailPulse simulates six logical source domains.

| Source ID | Source system | Description | Initial format |
|---|---|---|---|
| SRC-01 | POS | Sales transactions and product returns | CSV / JSON |
| SRC-02 | Product Management | Product catalog and pricing | CSV |
| SRC-03 | Store Management | Store locations and classifications | CSV |
| SRC-04 | Customer Management | Loyalty customer information | CSV |
| SRC-05 | Inventory Management | Inventory movements and stock records | CSV / JSON |
| SRC-06 | Procurement | Suppliers, purchase orders, and deliveries | CSV |

The POS domain additionally produces incremental JSON events for streaming ingestion.

All source data is synthetically generated for the RetailPulse business scenario.

## 3. General Contract Standards

### 3.1 Naming conventions

- Dataset names use lowercase snake_case.
- Column names use lowercase snake_case.
- Business identifiers use descriptive `_id` suffixes.
- Timestamps use descriptive `_timestamp` suffixes.
- Dates use descriptive `_date` suffixes.
- Boolean attributes use `is_` or `has_` prefixes.

### 3.2 Supported data types

| Logical type | Physical representation | Example |
|---|---|---|
| Identifier | STRING | TXN-001 |
| Integer | INT / BIGINT | 1001 |
| Decimal | DECIMAL(18,2) | 125.50 |
| Quantity | DECIMAL(18,3) | 12.500 |
| Date | DATE | 2026-11-24 |
| Timestamp | TIMESTAMP | 2026-11-24T10:30:00Z |
| Boolean | BOOLEAN | TRUE |
| Text | STRING | Beverages |

### 3.3 Date and timestamp conventions

- Business dates follow the `YYYY-MM-DD` format.
- Event timestamps must include an explicit timezone or UTC indicator.
- Timestamps are normalized to UTC during ingestion.
- Moroccan business dates are derived using the `Africa/Casablanca` timezone.
- Invalid date and timestamp values are rejected or quarantined.

### 3.4 Monetary conventions

- Currency: MAD.
- Monetary values use `DECIMAL(18,2)`.
- Floating-point types must not be used for financial calculations.
- VAT and discounts must be represented separately.
- Sales and returns must follow the signed amount conventions defined in the data dictionary.

### 3.5 Contract metadata

Every dataset contract must document:

| Attribute | Description |
|---|---|
| contract_id | Unique contract identifier |
| contract_version | Contract schema version |
| source_id | Originating source system |
| dataset_name | Logical dataset name |
| file_format | CSV or JSON |
| schema_definition | Expected fields and types |
| primary_business_key | Business identifier and uniqueness scope |
| required_fields | Mandatory fields |
| validation_rules | Structural and business constraints |
| schema_evolution_policy | Rules governing schema changes |

### 3.6 Schema evolution

RetailPulse follows controlled schema evolution.

- Adding an optional field requires a documented contract update.
- Adding a required field requires a version change and migration plan.
- Renaming or removing a field is a breaking change.
- Changing a field's physical data type requires compatibility assessment.
- Unknown fields must not be silently interpreted as valid business attributes.
- Every accepted schema version must remain documented.

### 3.7 Data rejection and quarantine

Records failing structural or business validation must be handled according to their severity.

| Severity | Example | Action |
|---|---|---|
| Critical | Missing transaction identifier | Reject and quarantine |
| Critical | Invalid monetary value | Reject and quarantine |
| Critical | Invalid required timestamp | Reject and quarantine |
| Warning | Optional customer city missing | Accept with warning |
| Warning | Unknown optional descriptive attribute | Apply documented evolution policy |

Rejected records must retain:

- Original source payload.
- Source dataset.
- Source record identifier, when available.
- Contract version.
- Ingestion timestamp.
- Pipeline run identifier.
- Rejection reason.
- Validation rule identifier.

No invalid record may be silently discarded.


## 4. SRC-01 — Point of Sale (POS): Sales and Returns

### 4.1 Contract Overview

| Attribute | Definition |
|---|---|
| Contract ID | SRC-01 |
| Source system | Point of Sale (POS) |
| Business domain | Sales and Returns |
| Batch format | CSV |
| Streaming format | JSON Lines (JSONL) |
| Batch dataset | `pos_sales` |
| Streaming dataset | `pos_sales_events` |
| Business grain | One product line per transaction |
| Primary business key | `source_system + transaction_id + transaction_line_id` |
| Streaming idempotency key | `event_id` |
| Target layer | Bronze, then Silver |
| Target Gold model | `fact_sales` |

**Purpose:** Capture historical and incremental POS transactions, including sales and product returns, while preserving transaction-level traceability.

Both ingestion paths must produce a consistent Silver transaction-line representation.

### 4.2 Historical Batch Contract — CSV

**File naming convention:**

`pos_sales_YYYYMMDD.csv`

**Encoding:** UTF-8
**Delimiter:** Comma
**Header:** Required
**Date format:** `YYYY-MM-DD`
**Timestamp format:** ISO 8601 with an explicit timezone.

#### CSV Schema

| Field | Data type | Required | Description |
|---|---|---|---|
| `source_record_id` | STRING | Yes | Unique identifier of the source record |
| `transaction_id` | STRING | Yes | POS transaction identifier |
| `transaction_line_id` | STRING | Yes | Unique line identifier within the transaction |
| `transaction_type` | STRING | Yes | `SALE` or `RETURN` |
| `original_sale_line_id` | STRING | Conditional | Globally unambiguous reference to the original sale line, formatted as original_transaction_id:original_transaction_line_id |
| `store_id` | STRING | Yes | Store business identifier |
| `product_id` | STRING | Yes | Product business identifier |
| `customer_id` | STRING | No | Loyalty customer identifier; null for anonymous purchases |
| `transaction_timestamp` | TIMESTAMP | Yes | Time at which the transaction occurred |
| `quantity` | DECIMAL(18,3) | Yes | Signed quantity |
| `unit_price` | DECIMAL(18,2) | Yes | Unit selling price, expressed as a positive value |
| `gross_amount` | DECIMAL(18,2) | Yes | Signed amount before discount and tax |
| `discount_amount` | DECIMAL(18,2) | Yes | Signed discount amount |
| `tax_amount` | DECIMAL(18,2) | Yes | Signed tax amount |
| `net_sales_amount` | DECIMAL(18,2) | Yes | Signed net sales amount |
| `currency` | STRING | Yes | Transaction currency; expected value `MAD` |
| `source_system` | STRING | Yes | Source identifier; expected value `POS` |

#### Example CSV

```csv
source_record_id,transaction_id,transaction_line_id,transaction_type,original_sale_line_id,store_id,product_id,customer_id,transaction_timestamp,quantity,unit_price,gross_amount,discount_amount,tax_amount,net_sales_amount,currency,source_system
POS-REC-001,TXN-1001,LINE-001,SALE,,STORE-CAS-01,PROD-001,CUST-100,2026-11-20T10:30:00+01:00,2.000,25.00,50.00,5.00,7.65,52.65,MAD,POS
POS-REC-002,TXN-1002,LINE-001,RETURN,LINE-001,STORE-CAS-01,PROD-001,CUST-100,2026-11-21T14:15:00+01:00,-1.000,25.00,-25.00,-2.50,-3.83,-26.33,MAD,POS
```

*Illustrative records only. The return references the original sale line; production-style synthetic data must use globally unambiguous source line identifiers.*

### 4.3 Incremental Streaming Contract — JSON Lines

The streaming source represents incremental POS transaction-line events.

**File naming convention:**

`pos_events_YYYYMMDD_HHMMSS.json`

**Format:** JSON Lines (JSONL), with one independent JSON object per line.
**Encoding:** UTF-8.

Each event represents one recorded sale line or return line.

#### JSON Event Schema

| Field | Data type | Required | Description |
|---|---|---|---|
| `schema_version` | STRING | Yes | Event schema version, initially `1.0` |
| `event_id` | STRING | Yes | Globally unique immutable event identifier |
| `event_type` | STRING | Yes | `SALE_LINE_RECORDED` or `RETURN_LINE_RECORDED` |
| `transaction_id` | STRING | Yes | POS transaction identifier |
| `transaction_line_id` | STRING | Yes | Transaction line identifier |
| `transaction_type` | STRING | Yes | `SALE` or `RETURN` |
| `original_sale_line_id` | STRING | Conditional | Globally unambiguous reference to the original sale line, formatted as original_transaction_id:original_transaction_line_id, which must identify exactly one original sale line. |
| `store_id` | STRING | Yes | Store business identifier |
| `product_id` | STRING | Yes | Product business identifier |
| `customer_id` | STRING | No | Loyalty customer identifier; null for anonymous purchases |
| `event_timestamp` | TIMESTAMP | Yes | Time the POS event occurred |
| `quantity` | DECIMAL(18,3) | Yes | Signed quantity |
| `unit_price` | DECIMAL(18,2) | Yes | Positive unit selling price |
| `gross_amount` | DECIMAL(18,2) | Yes | Signed gross amount |
| `discount_amount` | DECIMAL(18,2) | Yes | Signed discount amount |
| `tax_amount` | DECIMAL(18,2) | Yes | Signed tax amount |
| `net_sales_amount` | DECIMAL(18,2) | Yes | Signed net sales amount |
| `currency` | STRING | Yes | Expected value `MAD` |
| `source_system` | STRING | Yes | Expected value `POS` |

The pipeline adds `ingestion_timestamp` and `pipeline_run_id`. These are ingestion metadata, not source event fields.

#### Example JSON Events

```json
{"schema_version":"1.0","event_id":"EVT-000002","event_type":"RETURN_LINE_RECORDED","transaction_id":"TXN-2002","transaction_line_id":"LINE-002","transaction_type":"RETURN","original_sale_line_id":"TXN-2001:LINE-001","store_id":"STORE-RAB-01","product_id":"PROD-015","customer_id":null,"event_timestamp":"2026-11-24T11:30:00Z","quantity":-1.000,"unit_price":15.00,"gross_amount":-15.00,"discount_amount":0.00,"tax_amount":-2.25,"net_sales_amount":-17.25,"currency":"MAD","source_system":"POS"}
```

### 4.4 Business Rules

| Rule ID | Rule | Expected behavior |
|---|---|---|
| POS-BR-01 | Transaction type | Only `SALE` and `RETURN` are accepted |
| POS-BR-02 | Sale quantity | Must be strictly positive |
| POS-BR-03 | Return quantity | Must be strictly negative |
| POS-BR-04 | Unit price | Must be greater than or equal to zero |
| POS-BR-05 | Monetary consistency | `net_sales_amount = gross_amount - discount_amount + tax_amount` |
| POS-BR-06 | Gross amount | Must equal `quantity × unit_price`, subject to two-decimal rounding |
| POS-BR-07 | Return reference | Whenever the original sale is available, a return must reference it using the composite transaction and line identifier in the format original_transaction_id:original_transaction_line_id. The reference must uniquely identify exactly one original sale line. If the original sale is available but the reference is missing or invalid, the return must be rejected or quarantined until corrected. |
| POS-BR-08 | Currency | Only `MAD` is accepted in the initial project scope |
| POS-BR-09 | Customer identification | Null customer identifiers are valid and map to the anonymous customer dimension member |
| POS-BR-10 | Event uniqueness | An `event_id` must not be processed more than once |
| POS-BR-11 | Transaction uniqueness | A source transaction line must not be duplicated |
| POS-BR-12 | Event semantics | `event_type` must agree with `transaction_type` |

**Financial sign convention:**

- Sales: quantity, gross amount, discount amount, tax amount and net sales amount are positive or zero, with quantity strictly positive.
- Returns: quantity, gross amount, discount amount, tax amount and net sales amount are negative or zero, with quantity strictly negative.
- Unit price remains non-negative for both sales and returns.
- The net sales formula is applied consistently to both transaction types.

A return reverses the corresponding sales value in `fact_sales`. Actual cash or card refund settlement is outside the initial scope of this contract.

### 4.5 Data Quality and Validation Rules

| Rule ID | Validation | Severity | Failure handling |
|---|---|---|---|
| POS-DQ-01 | Required fields are present | Critical | Reject and quarantine |
| POS-DQ-02 | `source_record_id` is unique within the batch source | Critical | Reject duplicate |
| POS-DQ-03 | `event_id` is unique for streaming events | Critical | Deduplicate and record duplicate |
| POS-DQ-04 | Transaction line business key is unique | Critical | Reject duplicate |
| POS-DQ-05 | Transaction type is valid | Critical | Reject and quarantine |
| POS-DQ-06 | Quantity sign matches transaction type | Critical | Reject and quarantine |
| POS-DQ-07 | Monetary values satisfy the financial formula | Critical | Reject and quarantine |
| POS-DQ-08 | Store identifier exists in the store reference dataset | Critical | Quarantine unresolved record |
| POS-DQ-09 | Product identifier exists in the product reference dataset | Critical | Quarantine unresolved record |
| POS-DQ-10 | Customer identifier resolves when provided | Warning | Apply documented customer-resolution policy |
| POS-DQ-11 | Currency equals `MAD` | Critical | Reject and quarantine |
| POS-DQ-12 | Timestamp is parseable and timezone-aware | Critical | Reject and quarantine |
| POS-DQ-13 | Return references an existing original sale when a reference is supplied | Warning | Flag for reconciliation |
| POS-DQ-14 | Event schema version is supported | Critical | Quarantine unsupported version |

### 4.6 Processing and Traceability Requirements

1. Preserve the original source record in Bronze without silently modifying its business values.
2. Add ingestion metadata, including ingestion timestamp and pipeline run identifier.
3. Normalize timestamps to UTC while retaining the ability to derive the Moroccan business date using `Africa/Casablanca`.
4. Apply schema validation before transforming records into the Silver transaction-line structure.
5. Resolve `store_id`, `product_id` and `customer_id` to their corresponding dimension surrogate keys.
6. Map missing customer identifiers to `customer_key = 0`.
7. Deduplicate streaming events using `event_id` and the configured checkpointing strategy.
8. Preserve invalid records and their rejection reasons in quarantine.
9. Maintain enough source identifiers to trace every Silver transaction line back to its original source record or event.

### 4.7 Mapping to the Silver and Gold Layers

| Source field | Silver field | Gold destination |
|---|---|---|
| `transaction_id` | `transaction_id` | `fact_sales.transaction_id` |
| `transaction_line_id` | `transaction_line_id` | `fact_sales.transaction_line_id` |
| `transaction_type` | `transaction_type` | `fact_sales.transaction_type` |
| `original_sale_line_id` | `original_sale_line_id` | `fact_sales.original_sale_line_id` |
| `store_id` | `store_id` | Resolved to `store_key` |
| `product_id` | `product_id` | Resolved to `product_key` |
| `customer_id` | `customer_id` | Resolved to `customer_key` |
| `transaction_timestamp` / `event_timestamp` | `transaction_timestamp` | Used to derive `date_key` |
| `quantity` | `quantity` | `fact_sales.quantity` |
| `unit_price` | `unit_price` | `fact_sales.unit_price` |
| `gross_amount` | `gross_amount` | `fact_sales.gross_amount` |
| `discount_amount` | `discount_amount` | `fact_sales.discount_amount` |
| `tax_amount` | `tax_amount` | `fact_sales.tax_amount` |
| `net_sales_amount` | `net_sales_amount` | `fact_sales.net_sales_amount` |

**Important:** Natural business identifiers are used for source-to-dimension resolution. Gold fact tables store dimension surrogate keys, not source business identifiers as foreign keys.

### 4.8 Acceptance Criteria

The SRC-01 contract is accepted when:

- Historical CSV records can be parsed according to the declared schema.
- JSONL events can be parsed independently and validated against the event schema.
- Both ingestion paths produce the same normalized Silver structure.
- Duplicate events cannot create duplicate transaction lines.
- Sales and returns follow the signed-value conventions.
- Invalid records are quarantined with traceable rejection reasons.
- Valid records can be resolved to the appropriate Gold dimension keys.
- Source records remain traceable throughout the pipeline.


## 5. SRC-02 — Product Management

### 5.1 Contract Overview

| Attribute | Definition |
|---|---|
| Contract ID | SRC-02 |
| Source system | Product Management |
| Business domain | Product Catalog and Pricing |
| Batch format | CSV |
| Dataset | `products` |
| Business grain | One product per source record and effective version |
| Primary business key | `product_id` |
| Target layer | Bronze, then Silver |
| Target Gold model | `dim_product` |

**Purpose:** Provide a consistent product catalog containing product identity, classification, pricing, cost, unit of measure, and activation status.

Product changes must be historically traceable to support accurate reporting and SCD Type 2 processing.

### 5.2 Batch Contract — CSV

**File naming convention:**

`products_YYYYMMDD.csv`

**Encoding:** UTF-8
**Delimiter:** Comma
**Header:** Required
**Date format:** `YYYY-MM-DD`

#### CSV Schema

| Field | Data type | Required | Description |
|---|---|---|---|
| `product_id` | STRING | Yes | Unique product business identifier |
| `product_name` | STRING | Yes | Product display name |
| `category` | STRING | Yes | Main product category |
| `subcategory` | STRING | No | Product subcategory |
| `brand` | STRING | No | Product brand |
| `unit_of_measure` | STRING | Yes | Unit used to measure the product |
| `unit_cost` | DECIMAL(18,2) | Yes | Product acquisition or procurement cost per unit |
| `selling_price` | DECIMAL(18,2) | Yes | Standard selling price per unit |
| `is_active` | BOOLEAN | Yes | Indicates whether the product is available for sale |
| `effective_start_date` | DATE | Yes | Date from which this product version is valid |
| `source_updated_at` | TIMESTAMP | Yes | Source-system timestamp of the latest change |
| `source_system` | STRING | Yes | Expected value `PRODUCT_MGMT` |

#### Example CSV

```csv
product_id,product_name,category,subcategory,brand,unit_of_measure,unit_cost,selling_price,is_active,effective_start_date,source_updated_at,source_system
PROD-001,Whole Milk 1L,Dairy,Milk,Jaouda,UNIT,7.50,9.90,true,2026-01-01,2026-01-01T08:00:00Z,PRODUCT_MGMT
PROD-002,Olive Oil 1L,Grocery,Oil,Lesieur,LITER,42.00,55.00,true,2026-01-01,2026-01-01T08:15:00Z,PRODUCT_MGMT
PROD-003,Orange Juice 1L,Beverages,Juice,Local Brand,UNIT,8.00,12.50,true,2026-02-01,2026-02-01T09:00:00Z,PRODUCT_MGMT
```

*Illustrative synthetic records. Product names and brands are examples, not claims about actual supplier relationships.*

### 5.3 Business Rules

| Rule ID | Rule | Expected behavior |
|---|---|---|
| PROD-BR-01 | Product identification | Every product must have a stable, non-null `product_id` |
| PROD-BR-02 | Product name | Product name cannot be empty |
| PROD-BR-03 | Product category | Every product must belong to a valid category |
| PROD-BR-04 | Unit of measure | Must belong to the approved unit-of-measure reference list |
| PROD-BR-05 | Unit cost | Must be greater than or equal to zero |
| PROD-BR-06 | Selling price | Must be greater than or equal to zero |
| PROD-BR-07 | Product activation | Inactive products cannot be used for new sales after their effective deactivation date |
| PROD-BR-08 | Product history | Changes to tracked attributes must create a new SCD Type 2 version |
| PROD-BR-09 | Effective dates | Effective start date must not be later than the end date of the same version |
| PROD-BR-10 | Source updates | Older source updates must not overwrite newer product information |

**Unit-of-measure examples:**

- `UNIT`: individual item.
- `KG`: kilogram.
- `G`: gram.
- `LITER`: liter.
- `ML`: milliliter.
- `PACK`: packaged quantity.

The approved reference list will be maintained in project configuration.

### 5.4 Data Quality and Validation Rules

| Rule ID | Validation | Severity | Failure handling |
|---|---|---|---|
| PROD-DQ-01 | Required fields are present | Critical | Reject and quarantine |
| PROD-DQ-02 | `product_id` is not null or empty | Critical | Reject and quarantine |
| PROD-DQ-03 | Product identifier is unique within a source snapshot | Critical | Reject duplicate |
| PROD-DQ-04 | Product name is not empty | Critical | Reject and quarantine |
| PROD-DQ-05 | Category belongs to the approved reference list | Critical | Reject and quarantine |
| PROD-DQ-06 | Unit of measure is valid | Critical | Reject and quarantine |
| PROD-DQ-07 | Unit cost is non-negative | Critical | Reject and quarantine |
| PROD-DQ-08 | Selling price is non-negative | Critical | Reject and quarantine |
| PROD-DQ-09 | `is_active` contains a valid boolean value | Critical | Reject and quarantine |
| PROD-DQ-10 | Effective start date is valid | Critical | Reject and quarantine |
| PROD-DQ-11 | Source update timestamp is valid and timezone-aware | Critical | Reject and quarantine |
| PROD-DQ-12 | No overlapping SCD Type 2 validity periods exist for one product | Critical | Reject or flag affected history |
| PROD-DQ-13 | Selling price below unit cost | Warning | Accept and flag for review |

A selling price below unit cost is not automatically invalid because promotional or clearance pricing may intentionally produce a loss.

### 5.5 SCD Type 2 Requirements

The product dimension uses Slowly Changing Dimension Type 2 to preserve historical product attributes.

**Tracked attributes:**

- `product_name`
- `category`
- `subcategory`
- `brand`
- `unit_cost`
- `selling_price`
- `is_active`

**Required SCD Type 2 metadata:**

- `effective_start_date`
- `effective_end_date`
- `is_current`
- `record_hash`

When a tracked attribute changes:

1. Identify the existing current product record.
2. Compare the incoming tracked attributes with the existing version.
3. If no tracked attribute changes, do not create a new version.
4. If a tracked attribute changes, expire the existing version.
5. Insert a new current version with the updated attributes.
6. Preserve the previous version for historical analysis.

The implementation must use deterministic change detection and prevent overlapping validity periods.

### 5.6 Processing and Traceability Requirements

1. Preserve the original product source records in Bronze.
2. Validate the product schema and business rules before Silver processing.
3. Normalize text values and approved categories without losing the original Bronze values.
4. Validate product identifiers and effective dates.
5. Apply SCD Type 2 processing in the product dimension.
6. Maintain source update timestamps for change tracking.
7. Record rejected records and validation outcomes in the monitoring layer.
8. Preserve historical product versions needed to interpret past sales correctly.

### 5.7 Mapping to the Silver and Gold Layers

| Source field | Silver field | Gold destination |
|---|---|---|
| `product_id` | `product_id` | Business identifier in `dim_product` |
| `product_name` | `product_name` | `dim_product.product_name` |
| `category` | `category` | `dim_product.category` |
| `subcategory` | `subcategory` | `dim_product.subcategory` |
| `brand` | `brand` | `dim_product.brand` |
| `unit_of_measure` | `unit_of_measure` | Silver reference attribute |
| `unit_cost` | `unit_cost` | `dim_product.unit_cost` |
| `selling_price` | `selling_price` | `dim_product.selling_price` |
| `is_active` | `is_active` | `dim_product.is_active` |
| `effective_start_date` | `effective_start_date` | SCD Type 2 validity |
| `source_updated_at` | `source_updated_at` | Source lineage and change tracking |

**Important:** Sales records must resolve to the product dimension version valid at the transaction timestamp. This preserves historical product classification and pricing context.

### 5.8 Acceptance Criteria

The SRC-02 contract is accepted when:

- Product CSV files can be parsed using the declared schema.
- Product identifiers are unique within each source snapshot.
- Invalid product records are rejected or quarantined with clear reasons.
- Product category and unit-of-measure values are validated.
- Price and cost values are stored using decimal precision.
- Changes to tracked attributes create new SCD Type 2 versions.
- Unchanged product records do not generate unnecessary versions.
- Historical sales can resolve to the appropriate product dimension version.
- Product records remain traceable from Bronze through Gold.


## 6. SRC-03 — Store Management

### 6.1 Contract Overview

| Attribute | Definition |
|---|---|
| Contract ID | SRC-03 |
| Source system | Store Management |
| Business domain | Store Locations and Operations |
| Batch format | CSV |
| Dataset | `stores` |
| Business grain | One store per source record and effective version |
| Primary business key | `store_id` |
| Target layer | Bronze, then Silver |
| Target Gold model | `dim_store` |

**Purpose:** Maintain a consistent reference dataset describing supermarket locations, geographic attributes, store classifications, and operational status.

The initial synthetic retail network contains 15 stores distributed across five Moroccan cities.

### 6.2 Batch Contract — CSV

**File naming convention:**

`stores_YYYYMMDD.csv`

**Encoding:** UTF-8
**Delimiter:** Comma
**Header:** Required
**Date format:** `YYYY-MM-DD`

#### CSV Schema

| Field | Data type | Required | Description |
|---|---|---|---|
| `store_id` | STRING | Yes | Unique store business identifier |
| `store_name` | STRING | Yes | Official store display name |
| `city` | STRING | Yes | City where the store is located |
| `region` | STRING | Yes | Moroccan administrative region |
| `store_type` | STRING | Yes | Store classification |
| `address` | STRING | No | Store street address or location description |
| `postal_code` | STRING | No | Postal code, stored as text |
| `latitude` | DECIMAL(9,6) | No | Geographic latitude |
| `longitude` | DECIMAL(9,6) | No | Geographic longitude |
| `opening_date` | DATE | Yes | Date the store began operating |
| `is_active` | BOOLEAN | Yes | Indicates whether the store is operational |
| `effective_start_date` | DATE | Yes | Date from which this record version is valid |
| `source_updated_at` | TIMESTAMP | Yes | Source-system update timestamp |
| `source_system` | STRING | Yes | Expected value `STORE_MGMT` |

#### Example CSV

```csv
store_id,store_name,city,region,store_type,address,postal_code,latitude,longitude,opening_date,is_active,effective_start_date,source_updated_at,source_system
STORE-CAS-01,Casablanca Maarif,Casablanca,Casablanca-Settat,SUPERMARKET,Maarif,20000,33.5866,-7.6320,2022-03-01,true,2026-01-01,2026-01-01T08:00:00Z,STORE_MGMT
STORE-RAB-01,Rabat Agdal,Rabat,Rabat-Sale-Kenitra,SUPERMARKET,Agdal,10000,34.0050,-6.8530,2022-06-15,true,2026-01-01,2026-01-01T08:15:00Z,STORE_MGMT
STORE-MAR-01,Marrakech Gueliz,Marrakech,Marrakech-Safi,SUPERMARKET,Gueliz,40000,31.6340,-8.0080,2023-01-10,true,2026-01-01,2026-01-01T09:00:00Z,STORE_MGMT
STORE-AGA-01,Agadir Centre,Agadir,Souss-Massa,SUPERMARKET,Centre Ville,80000,30.4200,-9.5980,2023-04-01,true,2026-01-01,2026-01-01T09:30:00Z,STORE_MGMT
STORE-TNG-01,Tangier Centre,Tangier,Tanger-Tetouan-Al Hoceima,SUPERMARKET,Centre Ville,90000,35.7760,-5.8030,2023-08-01,true,2026-01-01,2026-01-01T10:00:00Z,STORE_MGMT
```

*Illustrative synthetic records. Coordinates and addresses are representative examples, not verified physical store locations.*

### 6.3 Reference Values

#### Cities and Regions

The initial network uses the following city-to-region mapping:

| City | Region |
|---|---|
| Casablanca | Casablanca-Settat |
| Rabat | Rabat-Sale-Kenitra |
| Marrakech | Marrakech-Safi |
| Agadir | Souss-Massa |
| Tangier | Tanger-Tetouan-Al Hoceima |

City and region values must be standardized using project reference data.

#### Store Types

| Value | Description |
|---|---|
| `SUPERMARKET` | Standard supermarket |
| `HYPERMARKET` | Large-format retail store |
| `EXPRESS` | Small-format convenience store |

The initial synthetic network may use `SUPERMARKET` for all 15 locations, with other types available for future scenarios.

### 6.4 Business Rules

| Rule ID | Rule | Expected behavior |
|---|---|---|
| STORE-BR-01 | Store identification | Every store must have a stable, non-null `store_id` |
| STORE-BR-02 | Store name | Store name cannot be empty |
| STORE-BR-03 | Geographic consistency | City must map to its correct region |
| STORE-BR-04 | Store classification | Store type must belong to the approved reference list |
| STORE-BR-05 | Opening date | Opening date cannot be later than the effective start date of the initial store record |
| STORE-BR-06 | Operational status | Inactive stores must not receive new sales with a business timestamp on or after their effective closure date. Valid historical sales dated before closure must still be accepted. |
| STORE-BR-07 | Store history | Changes to tracked attributes must create a new SCD Type 2 version |
| STORE-BR-08 | Geographic coordinates | Coordinates must fall within valid latitude and longitude ranges |
| STORE-BR-09 | Source updates | Older source updates must not overwrite newer store information |
| STORE-BR-10 | Store identity | A store identifier must never be reassigned to a different physical store |

### 6.5 Data Quality and Validation Rules

| Rule ID | Validation | Severity | Failure handling |
|---|---|---|---|
| STORE-DQ-01 | Required fields are present | Critical | Reject and quarantine |
| STORE-DQ-02 | `store_id` is not null or empty | Critical | Reject and quarantine |
| STORE-DQ-03 | Store identifier is unique within a source snapshot | Critical | Reject duplicate |
| STORE-DQ-04 | Store name is not empty | Critical | Reject and quarantine |
| STORE-DQ-05 | City belongs to the approved city reference list | Critical | Reject and quarantine |
| STORE-DQ-06 | City and region mapping is valid | Critical | Reject and quarantine |
| STORE-DQ-07 | Store type is valid | Critical | Reject and quarantine |
| STORE-DQ-08 | Opening date is valid | Critical | Reject and quarantine |
| STORE-DQ-09 | `is_active` contains a valid boolean value | Critical | Reject and quarantine |
| STORE-DQ-10 | Effective start date is valid | Critical | Reject and quarantine |
| STORE-DQ-11 | Source update timestamp is valid and timezone-aware | Critical | Reject and quarantine |
| STORE-DQ-12 | Latitude is between -90 and 90 | Critical | Reject and quarantine |
| STORE-DQ-13 | Longitude is between -180 and 180 | Critical | Reject and quarantine |
| STORE-DQ-14 | No overlapping SCD Type 2 validity periods exist for one store | Critical | Reject or flag affected history |

Coordinates are optional. Coordinate validation applies only when a coordinate value is provided. If either latitude or longitude is supplied, both must be supplied.

### 6.6 SCD Type 2 Requirements

The store dimension uses Slowly Changing Dimension Type 2 to preserve historical store information.

**Tracked attributes:**

- `store_name`
- `city`
- `region`
- `store_type`
- `is_active`

**Required SCD Type 2 metadata:**

- `effective_start_date`
- `effective_end_date`
- `is_current`
- `record_hash`

When a tracked attribute changes:

1. Identify the current store version.
2. Compare the incoming tracked attributes with the current version.
3. If no tracked attribute changes, do not create a new version.
4. Expire the previous version when a tracked attribute changes.
5. Insert the updated version with the appropriate effective start date.
6. Preserve the previous version for historical reporting.

Store identity remains stable across versions. Changes to addresses or coordinates may be captured in the source and Silver layer, but they are not SCD Type 2 tracked attributes in the initial Gold model.

### 6.7 Processing and Traceability Requirements

1. Preserve original store records in Bronze.
2. Validate identifiers, city-region mappings, store types, and effective dates.
3. Standardize city and region names in Silver.
4. Validate optional geographic coordinates when provided.
5. Apply SCD Type 2 processing to tracked attributes.
6. Prevent overlapping validity periods for the same store.
7. Record rejected records and validation results in the monitoring layer.
8. Preserve source update timestamps for change tracking.

### 6.8 Mapping to the Silver and Gold Layers

| Source field | Silver field | Gold destination |
|---|---|---|
| `store_id` | `store_id` | Business identifier in `dim_store` |
| `store_name` | `store_name` | `dim_store.store_name` |
| `city` | `city` | `dim_store.city` |
| `region` | `region` | `dim_store.region` |
| `store_type` | `store_type` | `dim_store.store_type` |
| `address` | `address` | Silver reference attribute |
| `postal_code` | `postal_code` | Silver reference attribute |
| `latitude` | `latitude` | Silver reference attribute |
| `longitude` | `longitude` | Silver reference attribute |
| `opening_date` | `opening_date` | Store lifecycle attribute |
| `is_active` | `is_active` | `dim_store.is_active` |
| `effective_start_date` | `effective_start_date` | SCD Type 2 validity |
| `source_updated_at` | `source_updated_at` | Source lineage and change tracking |

**Important:** The Gold `dim_store` model must remain consistent with the existing data dictionary. Address, postal code, coordinates, and opening date are initially source/Silver attributes; they must not be added to Gold without updating the data model and dictionary.

### 6.9 Acceptance Criteria

The SRC-03 contract is accepted when:

- Store CSV files can be parsed using the declared schema.
- Store identifiers are unique within each source snapshot.
- City and region combinations are validated.
- Store types are validated against approved reference values.
- Invalid coordinates are rejected when provided.
- Changes to tracked store attributes create new SCD Type 2 versions.
- Unchanged store records do not generate unnecessary versions.
- Historical sales resolve to the correct store dimension version.
- All store records remain traceable from Bronze through Gold.


## 7. SRC-04 — Customer Management

### 7.1 Contract Overview

| Attribute | Definition |
|---|---|
| Contract ID | SRC-04 |
| Source system | Customer Management |
| Business domain | Customer and Loyalty |
| Batch format | CSV |
| Dataset | `customers` |
| Business grain | One loyalty customer per source record and effective version |
| Primary business key | `customer_id` |
| Target layer | Bronze, then Silver |
| Target Gold model | `dim_customer` |

**Purpose:** Maintain customer loyalty information and customer segmentation attributes for retail analytics.

The contract supports identified loyalty customers and anonymous purchases without requiring personal information for every transaction.

### 7.2 Batch Contract — CSV

**File naming convention:**

`customers_YYYYMMDD.csv`

**Encoding:** UTF-8
**Delimiter:** Comma
**Header:** Required
**Date format:** `YYYY-MM-DD`

#### CSV Schema

| Field | Data type | Required | Description |
|---|---|---|---|
| `customer_id` | STRING | Yes | Unique customer business identifier |
| `customer_segment` | STRING | Yes | Customer segmentation category |
| `city` | STRING | No | Customer city |
| `loyalty_status` | STRING | Yes | Loyalty membership status |
| `registration_date` | DATE | No | Date the customer registered |
| `is_active` | BOOLEAN | Yes | Indicates whether the loyalty account is active |
| `effective_start_date` | DATE | Yes | Date from which this customer version is valid |
| `source_updated_at` | TIMESTAMP | Yes | Source-system update timestamp |
| `source_system` | STRING | Yes | Expected value `CUSTOMER_MGMT` |

The initial contract deliberately excludes customer names, email addresses, phone numbers, and other direct personal identifiers. Customer records use synthetic business identifiers.

#### Example CSV

```csv
customer_id,customer_segment,city,loyalty_status,registration_date,is_active,effective_start_date,source_updated_at,source_system
CUST-001,PREMIUM,Casablanca,ACTIVE,2025-02-10,true,2026-01-01,2026-01-01T08:00:00Z,CUSTOMER_MGMT
CUST-002,REGULAR,Rabat,ACTIVE,2025-06-15,true,2026-01-01,2026-01-01T08:15:00Z,CUSTOMER_MGMT
CUST-003,OCCASIONAL,Agadir,ACTIVE,2026-01-20,true,2026-01-01,2026-01-01T09:00:00Z,CUSTOMER_MGMT
```

*Illustrative synthetic records.*

### 7.3 Reference Values

#### Customer Segments

| Value | Description |
|---|---|
| `PREMIUM` | High-value or highly engaged customer |
| `REGULAR` | Customer with recurring purchases |
| `OCCASIONAL` | Customer with infrequent purchases |
| `NEW` | Recently registered customer |
| `UNKNOWN` | Unclassified or unavailable segment |

#### Loyalty Status

| Value | Description |
|---|---|
| `ACTIVE` | Active loyalty membership |
| `INACTIVE` | Inactive loyalty membership |
| `NOT_ENROLLED` | Customer has no loyalty membership |
| `SUSPENDED` | Loyalty membership temporarily suspended |

### 7.4 Business Rules

| Rule ID | Rule | Expected behavior |
|---|---|---|
| CUST-BR-01 | Customer identification | Every loyalty customer must have a stable `customer_id` |
| CUST-BR-02 | Customer segment | Segment must belong to the approved reference list |
| CUST-BR-03 | Loyalty status | Status must belong to the approved reference list |
| CUST-BR-04 | Anonymous purchases | Missing POS customer identifiers must map to the anonymous dimension member |
| CUST-BR-05 | Customer history | Changes to tracked attributes must create a new SCD Type 2 version |
| CUST-BR-06 | Registration date | Registration date cannot be later than the effective start date of the initial customer record |
| CUST-BR-07 | Account status | Inactive accounts cannot be treated as active loyalty memberships |
| CUST-BR-08 | Customer identity | A customer identifier must never be reassigned to another customer |
| CUST-BR-09 | Source updates | Older source updates must not overwrite newer customer information |
| CUST-BR-10 | Data minimization | Direct personal identifiers are excluded from the initial project scope |

### 7.5 Anonymous Customer Handling

Anonymous purchases are valid POS transactions and must not be rejected solely because the customer is unidentified.

#### Anonymous Customer Resolution

When `customer_id` is null or unavailable:

1. Do not reject the sales record.
2. Do not create a new customer dimension record.
3. Resolve the transaction to the permanent anonymous customer dimension member.
4. Use `customer_key = 0`.
5. Use `customer_id = ANONYMOUS`, `customer_segment = UNKNOWN`, and `loyalty_status = NOT_ENROLLED` for that member.
6. Preserve the original null customer identifier in source lineage.

The anonymous member is a predefined dimension record. It is not part of the customer source snapshot and is not subject to ordinary SCD Type 2 updates.

#### Unresolved Customer References

When a POS transaction contains a non-null `customer_id` that cannot be found in the customer dimension:

1. Do not automatically map the transaction to the anonymous customer member.
2. Record the unresolved customer reference.
3. Quarantine the affected transaction for investigation or retry after customer data is available.
4. Preserve the original transaction and customer identifiers for traceability.

A supplied but unknown customer identifier may indicate missing customer master data or a referential integrity issue. It must be handled separately from a genuinely anonymous purchase.

### 7.6 Data Quality and Validation Rules

| Rule ID | Validation | Severity | Failure handling |
|---|---|---|---|
| CUST-DQ-01 | Required fields are present | Critical | Reject and quarantine |
| CUST-DQ-02 | `customer_id` is not null or empty | Critical | Reject and quarantine |
| CUST-DQ-03 | Customer identifier is unique within a source snapshot | Critical | Reject duplicate |
| CUST-DQ-04 | Customer segment belongs to the approved reference list | Critical | Reject and quarantine |
| CUST-DQ-05 | Loyalty status belongs to the approved reference list | Critical | Reject and quarantine |
| CUST-DQ-06 | Registration date is valid when provided | Critical | Reject and quarantine |
| CUST-DQ-07 | `is_active` contains a valid boolean value | Critical | Reject and quarantine |
| CUST-DQ-08 | Effective start date is valid | Critical | Reject and quarantine |
| CUST-DQ-09 | Source update timestamp is valid and timezone-aware | Critical | Reject and quarantine |
| CUST-DQ-10 | Customer city belongs to the approved city reference list when provided | Warning | Accept and flag for review |
| CUST-DQ-11 | No overlapping SCD Type 2 validity periods exist for one customer | Critical | Reject or flag affected history |
| CUST-DQ-12 | Customer identifier does not conflict with reserved anonymous identifier | Critical | Reject and quarantine |

### 7.7 SCD Type 2 Requirements

The customer dimension uses Slowly Changing Dimension Type 2.

**Tracked attributes:**

- `customer_segment`
- `city`
- `loyalty_status`

**Required SCD Type 2 metadata:**

- `effective_start_date`
- `effective_end_date`
- `is_current`
- `record_hash`

When a tracked attribute changes:

1. Identify the existing current customer version.
2. Compare the incoming tracked attributes.
3. If no tracked attribute changes, do not create a new version.
4. Expire the previous version when a tracked attribute changes.
5. Insert a new version with updated attributes.
6. Preserve previous versions for historical customer analytics.

`is_active` is maintained as a source attribute and used for account-status validation. It is not a tracked Gold dimension attribute in the initial model. If this changes, the data dictionary must be updated.

### 7.8 Processing and Traceability Requirements

1. Preserve original customer records in Bronze.
2. Validate customer identifiers and reference values.
3. Normalize segment, city, and loyalty status values in Silver.
4. Exclude the reserved anonymous member from ordinary customer ingestion.
5. Apply SCD Type 2 processing to tracked customer attributes.
6. Resolve POS customer identifiers against the customer dimension.
7. Map missing customer identifiers to `customer_key = 0`.
8. Apply the documented unresolved-customer policy when a supplied identifier cannot be found.
9. Record rejected records and validation results in the monitoring layer.
10. Avoid collecting or exposing unnecessary personal information.

### 7.9 Mapping to the Silver and Gold Layers

| Source field | Silver field | Gold destination |
|---|---|---|
| `customer_id` | `customer_id` | Business identifier in `dim_customer` |
| `customer_segment` | `customer_segment` | `dim_customer.customer_segment` |
| `city` | `city` | `dim_customer.city` |
| `loyalty_status` | `loyalty_status` | `dim_customer.loyalty_status` |
| `registration_date` | `registration_date` | Silver reference attribute |
| `is_active` | `is_active` | Silver operational attribute |
| `effective_start_date` | `effective_start_date` | SCD Type 2 validity |
| `source_updated_at` | `source_updated_at` | Source lineage and change tracking |

**Important:** The initial Gold customer dimension contains the agreed tracked attributes and SCD Type 2 metadata. Registration date and account activation status remain in the source/Silver layer unless the dimensional model is formally extended.

### 7.10 Acceptance Criteria

The SRC-04 contract is accepted when:

- Customer CSV files can be parsed according to the declared schema.
- Customer identifiers are unique within each source snapshot.
- Customer segment and loyalty status are validated.
- Anonymous purchases are accepted without creating individual anonymous customer records.
- Missing customer identifiers resolve to `customer_key = 0`.
- Changes to tracked attributes create new SCD Type 2 versions.
- Unchanged records do not generate unnecessary versions.
- Unresolved supplied customer identifiers are handled according to the documented policy.
- Customer data remains traceable from Bronze through Gold.


## 8. SRC-05 — Inventory Management

### 8.1 Contract Overview

| Attribute | Definition |
|---|---|
| Contract ID | SRC-05 |
| Source system | Inventory Management |
| Business domain | Inventory and Stock Movements |
| Batch formats | CSV and JSON |
| Datasets | `inventory_movements`, `inventory_snapshots` |
| Movement grain | One stock movement per product and store |
| Snapshot grain | One product-store-business-date record |
| Movement primary business key | `movement_id` |
| Snapshot primary business key | `store_id + product_id + snapshot_date` |
| Target layer | Bronze, then Silver |
| Target Gold model | `fact_inventory_snapshot` |

**Purpose:** Capture stock movements and inventory positions for each product and store, enabling stock reconciliation, inventory monitoring, and stockout analysis.

The contract separates movement events from daily stock snapshots. Movements explain stock changes; snapshots represent the resulting stock position.

### 8.2 Dataset A — Inventory Movements (CSV)

**File naming convention:**

`inventory_movements_YYYYMMDD.csv`

**Encoding:** UTF-8
**Delimiter:** Comma
**Header:** Required
**Timestamp format:** ISO 8601 with an explicit timezone.

#### CSV Schema

| Field | Data type | Required | Description |
|---|---|---|---|
| `movement_id` | STRING | Yes | Unique inventory movement identifier |
| `store_id` | STRING | Yes | Store business identifier |
| `product_id` | STRING | Yes | Product business identifier |
| `movement_type` | STRING | Yes | Type of stock movement |
| `movement_timestamp` | TIMESTAMP | Yes | Time at which the movement occurred |
| `quantity` | DECIMAL(18,3) | Yes | Signed stock quantity change |
| `reference_id` | STRING | No | Related sale, return, delivery, or adjustment identifier |
| `reason_code` | STRING | No | Reason for the movement |
| `source_system` | STRING | Yes | Expected value `INVENTORY_MGMT` |

#### Movement Type Reference

| Value | Description | Expected quantity sign |
|---|---|---|
| `RECEIPT` | Goods received from a supplier | Positive |
| `SALE` | Stock reduction from a sale | Negative |
| `RETURN` | Sellable product returned to inventory | Positive |
| `ADJUSTMENT_IN` | Positive inventory correction | Positive |
| `ADJUSTMENT_OUT` | Negative inventory correction | Negative |
| `DAMAGE` | Damaged or unsellable stock removed | Negative |
| `TRANSFER_IN` | Stock received from another store | Positive |
| `TRANSFER_OUT` | Stock sent to another store | Negative |

**Important:** A customer return does not automatically increase sellable inventory. Only products accepted back into sellable stock generate a positive `RETURN` movement. Damaged or unsellable returned products must be represented by an appropriate negative adjustment or damage movement.

#### Example CSV

```csv
movement_id,store_id,product_id,movement_type,movement_timestamp,quantity,reference_id,reason_code,source_system
MOV-001,STORE-CAS-01,PROD-001,RECEIPT,2026-11-20T08:00:00Z,100.000,PO-1001,SUPPLIER_DELIVERY,INVENTORY_MGMT
MOV-002,STORE-CAS-01,PROD-001,SALE,2026-11-20T10:30:00Z,-2.000,TXN-1001,POS_SALE,INVENTORY_MGMT
MOV-003,STORE-CAS-01,PROD-001,RETURN,2026-11-21T14:15:00Z,1.000,TXN-1002,SELLABLE_RETURN,INVENTORY_MGMT
MOV-004,STORE-CAS-01,PROD-001,DAMAGE,2026-11-21T15:00:00Z,-1.000,ADJ-001,DAMAGED_PRODUCT,INVENTORY_MGMT
```

*Illustrative synthetic records.*

### 8.3 Dataset B — Daily Inventory Snapshots (CSV)

**File naming convention:**

`inventory_snapshots_YYYYMMDD.csv`

**Encoding:** UTF-8
**Delimiter:** Comma
**Header:** Required
**Date format:** `YYYY-MM-DD`

#### CSV Schema

| Field | Data type | Required | Description |
|---|---|---|---|
| `store_id` | STRING | Yes | Store business identifier |
| `product_id` | STRING | Yes | Product business identifier |
| `snapshot_date` | DATE | Yes | Moroccan business date of the snapshot |
| `opening_stock` | DECIMAL(18,3) | Yes | Sellable stock at the start of the business date |
| `received_quantity` | DECIMAL(18,3) | Yes | Quantity received during the business date |
| `sold_quantity` | DECIMAL(18,3) | Yes | Positive quantity sold during the business date |
| `returned_quantity` | DECIMAL(18,3) | Yes | Sellable quantity returned during the business date |
| `adjustment_quantity` | DECIMAL(18,3) | Yes | Signed inventory adjustment during the business date |
| `minimum_available_stock` | DECIMAL(18,3) | Yes | Minimum sellable available stock reached during the business date |
| `closing_stock` | DECIMAL(18,3) | Yes | Sellable stock at the end of the business date |
| `reserved_quantity` | DECIMAL(18,3) | Yes | Quantity reserved and unavailable for new sales |
| `reorder_level` | DECIMAL(18,3) | Yes | Stock threshold that triggers replenishment |
| `source_updated_at` | TIMESTAMP | Yes | Source-system update timestamp |
| `source_system` | STRING | Yes | Expected value `INVENTORY_MGMT` |

**Quantity conventions:** Snapshot quantities are non-negative. `adjustment_quantity` is signed. `sold_quantity` and `returned_quantity` are positive magnitudes, not signed movement values.

#### Example CSV

```csv
store_id,product_id,snapshot_date,opening_stock,received_quantity,sold_quantity,returned_quantity,adjustment_quantity,minimum_available_stock,closing_stock,reserved_quantity,reorder_level,source_updated_at,source_system
STORE-CAS-01,PROD-001,2026-11-20,50.000,100.000,20.000,0.000,0.000,30.000,130.000,5.000,25.000,2026-11-20T23:00:00Z,INVENTORY_MGMT
STORE-RAB-01,PROD-002,2026-11-20,15.000,0.000,12.000,1.000,0.000,2.000,4.000,0.000,10.000,2026-11-20T23:00:00Z,INVENTORY_MGMT
```

*Illustrative synthetic records. The first example follows the stock reconciliation formula: 50 + 100 - 20 + 0 + 0 = 130.*

### 8.4 Business Rules

| Rule ID | Rule | Expected behavior |
|---|---|---|
| INV-BR-01 | Movement identification | Every movement must have a unique `movement_id` |
| INV-BR-02 | Movement type | Only approved movement types are accepted |
| INV-BR-03 | Movement sign | Quantity sign must match movement type |
| INV-BR-04 | Stock snapshot grain | One record per product, store, and business date |
| INV-BR-05 | Opening stock | Must be non-negative |
| INV-BR-06 | Closing stock | Must be non-negative |
| INV-BR-07 | Stock reconciliation | Closing stock must reconcile with opening stock and movements |
| INV-BR-08 | Sellable returns | Only sellable returned products increase available inventory |
| INV-BR-09 | Minimum available stock | Must not exceed the opening stock plus cumulative positive stock movements at any point during the day |
| INV-BR-10 | Stockout detection | A stockout occurs when minimum available stock is less than or equal to zero |
| INV-BR-11 | Reserved quantity | Must not exceed closing stock |
| INV-BR-12 | Reorder level | Must be non-negative |
| INV-BR-13 | Business date | Snapshot date must follow the `Africa/Casablanca` business calendar |
| INV-BR-14 | Movement traceability | Related sales, returns, receipts, and adjustments should retain their source reference identifiers |

**Stock reconciliation formula:**

`closing_stock = opening_stock + received_quantity + returned_quantity - sold_quantity + adjustment_quantity`

The formula must hold for every valid daily inventory snapshot.

`minimum_available_stock` represents the minimum sellable stock reached at any point during the business date, after applying movements in event-time order.

A snapshot with `minimum_available_stock <= 0` is considered a stockout, even if `closing_stock` is positive.

### 8.5 Data Quality and Validation Rules

| Rule ID | Validation | Severity | Failure handling |
|---|---|---|---|
| INV-DQ-01 | Required fields are present | Critical | Reject and quarantine |
| INV-DQ-02 | `movement_id` is unique | Critical | Reject duplicate |
| INV-DQ-03 | Store identifier exists | Critical | Quarantine unresolved record |
| INV-DQ-04 | Product identifier exists | Critical | Quarantine unresolved record |
| INV-DQ-05 | Movement type is valid | Critical | Reject and quarantine |
| INV-DQ-06 | Movement quantity sign matches movement type | Critical | Reject and quarantine |
| INV-DQ-07 | Movement timestamp is valid and timezone-aware | Critical | Reject and quarantine |
| INV-DQ-08 | Snapshot business key is unique | Critical | Reject duplicate |
| INV-DQ-09 | Snapshot date is valid | Critical | Reject and quarantine |
| INV-DQ-10 | Stock quantity fields are non-negative | Critical | Reject and quarantine |
| INV-DQ-11 | Adjustment quantity is valid and signed | Critical | Reject and quarantine |
| INV-DQ-12 | Stock reconciliation formula is satisfied | Critical | Reject or flag snapshot |
| INV-DQ-13 | Minimum available stock is not greater than opening stock plus cumulative positive movements | Critical | Reject or flag snapshot |
| INV-DQ-14 | Reserved quantity does not exceed closing stock | Warning | Accept and flag for review |
| INV-DQ-15 | Reorder level is non-negative | Critical | Reject and quarantine |
| INV-DQ-16 | Source update timestamp is valid and timezone-aware | Critical | Reject and quarantine |

### 8.6 Processing and Traceability Requirements

1. Preserve original movement and snapshot records in Bronze.
2. Validate movement types, signs, identifiers, and timestamps.
3. Normalize movement timestamps to UTC.
4. Derive Moroccan business dates using `Africa/Casablanca`.
5. Resolve store and product identifiers against their reference dimensions.
6. Aggregate inventory movements by product, store, and business date.
7. Reconcile movement-derived closing stock against supplied daily snapshots.
8. Calculate `minimum_available_stock` from ordered movements when sufficient event-time data is available.
9. Identify stockouts using the minimum available stock rather than closing stock alone.
10. Preserve discrepancies between calculated and reported inventory in the data quality monitoring layer.
11. Retain source movement identifiers and references for auditability.

### 8.7 Mapping to the Silver and Gold Layers

#### Inventory Movements

| Source field | Silver field | Gold usage |
|---|---|---|
| `movement_id` | `movement_id` | Lineage and reconciliation |
| `store_id` | `store_id` | Resolved to `store_key` |
| `product_id` | `product_id` | Resolved to `product_key` |
| `movement_type` | `movement_type` | Movement classification |
| `movement_timestamp` | `movement_timestamp` | Derive business date |
| `quantity` | `quantity` | Stock movement aggregation |
| `reference_id` | `reference_id` | Source traceability |

#### Daily Inventory Snapshots

| Source field | Silver field | Gold destination |
|---|---|---|
| `store_id` | `store_id` | Resolved to `store_key` |
| `product_id` | `product_id` | Resolved to `product_key` |
| `snapshot_date` | `snapshot_date` | Resolved to `date_key` |
| `opening_stock` | `opening_stock` | `fact_inventory_snapshot.opening_stock` |
| `received_quantity` | `received_quantity` | `fact_inventory_snapshot.received_quantity` |
| `sold_quantity` | `sold_quantity` | `fact_inventory_snapshot.sold_quantity` |
| `returned_quantity` | `returned_quantity` | `fact_inventory_snapshot.returned_quantity` |
| `adjustment_quantity` | `adjustment_quantity` | `fact_inventory_snapshot.adjustment_quantity` |
| `minimum_available_stock` | `minimum_available_stock` | `fact_inventory_snapshot.minimum_available_stock` |
| `closing_stock` | `closing_stock` | `fact_inventory_snapshot.closing_stock` |
| `reserved_quantity` | `reserved_quantity` | `fact_inventory_snapshot.reserved_quantity` |
| `reorder_level` | `reorder_level` | `fact_inventory_snapshot.reorder_level` |

**Important:** The movement dataset provides the detailed explanation of stock changes. The daily snapshot dataset provides the measures used by the initial Gold inventory fact. Both must reconcile; they must not be treated as independent sources of truth without a documented reconciliation process.

### 8.8 Acceptance Criteria

The SRC-05 contract is accepted when:

- Inventory movement CSV files can be parsed using the declared schema.
- Daily inventory snapshots can be parsed using the declared schema.
- Movement identifiers and snapshot business keys are unique.
- Movement types and quantity signs are validated.
- Stock reconciliation is performed using the agreed formula.
- Minimum available stock supports intraday stockout detection.
- Sellable and unsellable returns are handled correctly.
- Invalid or inconsistent records are quarantined or flagged with traceable reasons.
- Inventory records can be resolved to product, store, and date dimensions.
- Movement and snapshot records remain traceable from Bronze through Gold.


## 9. SRC-06 — Procurement and Supplier Deliveries

### 9.1 Contract Overview

| Attribute | Definition |
|---|---|
| Contract ID | SRC-06 |
| Source system | Procurement Management |
| Business domain | Suppliers, Purchase Orders, and Deliveries |
| Batch format | CSV |
| Datasets | `suppliers`, `purchase_order_lines`, `purchase_order_deliveries` |
| Supplier grain | One supplier per source record and effective version |
| Purchase order grain | One purchase order line |
| Delivery grain | One delivery against one purchase order line |
| Supplier primary business key | `supplier_id` |
| Purchase order primary business key | `purchase_order_id + purchase_order_line_id` |
| Delivery primary business key | `delivery_id + purchase_order_line_id` |
| Target layer | Bronze, then Silver |
| Target Gold models | `dim_supplier`, `fact_supplier_delivery` |

**Purpose:** Capture supplier information, purchase order commitments, and delivery outcomes to support supplier performance and procurement analytics.

The source separates supplier master data, purchase order lines, and delivery events. The Silver layer combines delivery events into one accumulating record per purchase order line for the initial Gold fact table.

### 9.2 Dataset A — Suppliers (CSV)

**File naming convention:**

`suppliers_YYYYMMDD.csv`

**Encoding:** UTF-8
**Delimiter:** Comma
**Header:** Required

#### CSV Schema

| Field | Data type | Required | Description |
|---|---|---|---|
| `supplier_id` | STRING | Yes | Unique supplier business identifier |
| `supplier_name` | STRING | Yes | Supplier display name |
| `city` | STRING | No | Supplier city |
| `supplier_category` | STRING | Yes | Main supplier category |
| `is_active` | BOOLEAN | Yes | Indicates whether the supplier is active |
| `effective_start_date` | DATE | Yes | Date from which this supplier version is valid |
| `source_updated_at` | TIMESTAMP | Yes | Source-system update timestamp |
| `source_system` | STRING | Yes | Expected value `PROCUREMENT_MGMT` |

#### Example CSV

```csv id="5t0zvc"
supplier_id,supplier_name,city,supplier_category,is_active,effective_start_date,source_updated_at,source_system
SUP-001,Atlas Food Distribution,Casablanca,FOOD,true,2026-01-01,2026-01-01T08:00:00Z,PROCUREMENT_MGMT
SUP-002,Maghreb Fresh Supply,Agadir,PRODUCE,true,2026-01-01,2026-01-01T08:15:00Z,PROCUREMENT_MGMT
SUP-003,North Retail Logistics,Tangier,LOGISTICS,true,2026-01-01,2026-01-01T09:00:00Z,PROCUREMENT_MGMT
```

*Illustrative synthetic records.*

### 9.3 Dataset B — Purchase Order Lines (CSV)

**File naming convention:**

`purchase_order_lines_YYYYMMDD.csv`

**Encoding:** UTF-8
**Delimiter:** Comma
**Header:** Required

#### CSV Schema

| Field | Data type | Required | Description |
|---|---|---|---|
| `purchase_order_id` | STRING | Yes | Purchase order identifier |
| `purchase_order_line_id` | STRING | Yes | Unique line identifier within the purchase order |
| `supplier_id` | STRING | Yes | Supplier business identifier |
| `store_id` | STRING | Yes | Destination store identifier |
| `product_id` | STRING | Yes | Ordered product identifier |
| `order_date` | DATE | Yes | Date the purchase order was placed |
| `expected_delivery_date` | DATE | Yes | Expected delivery date |
| `ordered_quantity` | DECIMAL(18,3) | Yes | Quantity ordered |
| `unit_cost` | DECIMAL(18,2) | Yes | Agreed procurement cost per unit |
| `currency` | STRING | Yes | Expected value `MAD` |
| `purchase_order_status` | STRING | Yes | Current purchase order line status |
| `source_updated_at` | TIMESTAMP | Yes | Source-system update timestamp |
| `source_system` | STRING | Yes | Expected value `PROCUREMENT_MGMT` |

#### Purchase Order Status Reference

| Value | Description |
|---|---|
| `OPEN` | Order placed and awaiting fulfillment |
| `PARTIALLY_RECEIVED` | Some quantity has been received |
| `FULLY_RECEIVED` | All ordered quantity has been received |
| `CANCELLED` | Purchase order line cancelled |
| `OVERDUE` | Expected delivery date passed without complete fulfillment |

#### Example CSV

```csv id="v4xdka"
purchase_order_id,purchase_order_line_id,supplier_id,store_id,product_id,order_date,expected_delivery_date,ordered_quantity,unit_cost,currency,purchase_order_status,source_updated_at,source_system
PO-1001,PO-1001-L01,SUP-001,STORE-CAS-01,PROD-001,2026-11-18,2026-11-20,100.000,7.50,MAD,FULLY_RECEIVED,2026-11-21T08:00:00Z,PROCUREMENT_MGMT
PO-1002,PO-1002-L01,SUP-002,STORE-AGA-01,PROD-002,2026-11-19,2026-11-22,200.000,12.00,MAD,PARTIALLY_RECEIVED,2026-11-22T09:00:00Z,PROCUREMENT_MGMT
```

*Illustrative synthetic records.*

### 9.4 Dataset C — Purchase Order Deliveries (CSV)

**File naming convention:**

`purchase_order_deliveries_YYYYMMDD.csv`

**Encoding:** UTF-8
**Delimiter:** Comma
**Header:** Required

Each record represents one delivery event against a purchase order line. A purchase order line may have multiple delivery records.

#### CSV Schema

| Field | Data type | Required | Description |
|---|---|---|---|
| `delivery_id` | STRING | Yes | Unique delivery event identifier |
| `purchase_order_id` | STRING | Yes | Related purchase order identifier |
| `purchase_order_line_id` | STRING | Yes | Related purchase order line identifier |
| `delivery_timestamp` | TIMESTAMP | Yes | Actual delivery timestamp |
| `received_quantity` | DECIMAL(18,3) | Yes | Quantity physically received |
| `rejected_quantity` | DECIMAL(18,3) | Yes | Quantity rejected during inspection |
| `delivery_status` | STRING | Yes | Delivery event outcome |
| `rejection_reason` | STRING | No | Explanation for rejected quantity |
| `source_updated_at` | TIMESTAMP | Yes | Source-system update timestamp |
| `source_system` | STRING | Yes | Expected value `PROCUREMENT_MGMT` |

#### Delivery Status Reference

| Value | Description |
|---|---|
| `RECEIVED` | Delivery accepted |
| `PARTIALLY_ACCEPTED` | Some received quantity accepted and some rejected |
| `REJECTED` | Entire delivery rejected |
| `CANCELLED` | Delivery event cancelled |

#### Example CSV

```csv
delivery_id,purchase_order_id,purchase_order_line_id,delivery_timestamp,received_quantity,rejected_quantity,delivery_status,rejection_reason,source_updated_at,source_system
DEL-001,PO-1001,PO-1001-L01,2026-11-20T10:00:00Z,100.000,0.000,RECEIVED,,2026-11-20T10:30:00Z,PROCUREMENT_MGMT
DEL-002,PO-1002,PO-1002-L01,2026-11-22T11:00:00Z,80.000,5.000,PARTIALLY_ACCEPTED,DAMAGED_PACKAGING,2026-11-22T12:00:00Z,PROCUREMENT_MGMT
DEL-003,PO-1002,PO-1002-L01,2026-11-23T09:00:00Z,120.000,0.000,RECEIVED,,2026-11-23T09:45:00Z,PROCUREMENT_MGMT
```

*Illustrative synthetic records.*

### 9.5 Business Rules

| Rule ID | Rule | Expected behavior |
|---|---|---|
| PROC-BR-01 | Supplier identification | Every supplier must have a stable `supplier_id` |
| PROC-BR-02 | Supplier classification | Supplier category must belong to the approved reference list |
| PROC-BR-03 | Purchase order identification | A purchase order line is uniquely identified by purchase order ID and line ID |
| PROC-BR-04 | Supplier relationship | Every purchase order line must reference an existing supplier |
| PROC-BR-05 | Store relationship | Every purchase order line must reference an existing destination store |
| PROC-BR-06 | Product relationship | Every purchase order line must reference an existing product |
| PROC-BR-07 | Ordered quantity | Must be strictly positive |
| PROC-BR-08 | Procurement cost | Unit cost must be non-negative |
| PROC-BR-09 | Expected delivery | Expected delivery date cannot precede the order date |
| PROC-BR-10 | Delivery identification | Every delivery event must have a unique `delivery_id` |
| PROC-BR-11 | Delivery quantities | Received and rejected quantities must be non-negative |
| PROC-BR-12 | Delivery aggregation | Multiple deliveries must be aggregated against the same purchase order line |
| PROC-BR-13 | Fulfillment quantity | Total accepted quantity must not exceed ordered quantity without an explicit documented over-delivery exception |
| PROC-BR-14 | Supplier history | Changes to tracked supplier attributes must create a new SCD Type 2 version |
| PROC-BR-15 | Delivery performance | On-time performance is determined using the agreed expected delivery date and completion date |

**Accepted quantity formula:**

`accepted_quantity = received_quantity - rejected_quantity`

**Cumulative fulfillment formula:**

`total_accepted_quantity = SUM(accepted_quantity) across valid delivery events`

The purchase order line must retain the original ordered quantity. Partial deliveries must not duplicate the ordered quantity.

### 9.6 Derived Purchase Order Line Status

The Silver processing layer derives a consolidated line status from the purchase order and delivery records.

| Derived status | Definition |
|---|---|
| `PENDING` | No accepted delivery and expected delivery date has not passed |
| `PARTIALLY_RECEIVED` | Accepted quantity is greater than zero but below ordered quantity |
| `FULLY_RECEIVED` | Accepted quantity equals ordered quantity |
| `PARTIALLY_FULFILLED` | Expected delivery date passed and accepted quantity remains below ordered quantity |
| `CANCELLED` | Purchase order line is cancelled |
| `OVERDUE` | No accepted quantity exists and expected delivery date has passed |

The exact status precedence must be implemented consistently. A cancelled line remains `CANCELLED`; a completed line remains `FULLY_RECEIVED`.

### 9.7 Data Quality and Validation Rules

| Rule ID | Validation | Severity | Failure handling |
|---|---|---|---|
| PROC-DQ-01 | Required fields are present | Critical | Reject and quarantine |
| PROC-DQ-02 | Supplier identifier is unique within a supplier snapshot | Critical | Reject duplicate |
| PROC-DQ-03 | Supplier name is not empty | Critical | Reject and quarantine |
| PROC-DQ-04 | Supplier category belongs to approved values | Critical | Reject and quarantine |
| PROC-DQ-05 | Purchase order line business key is unique | Critical | Reject duplicate |
| PROC-DQ-06 | Supplier identifier exists | Critical | Quarantine unresolved record |
| PROC-DQ-07 | Store identifier exists | Critical | Quarantine unresolved record |
| PROC-DQ-08 | Product identifier exists | Critical | Quarantine unresolved record |
| PROC-DQ-09 | Ordered quantity is strictly positive | Critical | Reject and quarantine |
| PROC-DQ-10 | Unit cost is non-negative | Critical | Reject and quarantine |
| PROC-DQ-11 | Expected delivery date is valid | Critical | Reject and quarantine |
| PROC-DQ-12 | Delivery identifier is unique | Critical | Reject duplicate |
| PROC-DQ-13 | Delivery references an existing purchase order line | Critical | Quarantine unresolved record |
| PROC-DQ-14 | Received and rejected quantities are non-negative | Critical | Reject and quarantine |
| PROC-DQ-15 | Rejected quantity does not exceed received quantity | Critical | Reject and quarantine |
| PROC-DQ-16 | Cumulative accepted quantity does not exceed ordered quantity without an approved exception | Critical | Quarantine or flag for review |
| PROC-DQ-17 | Delivery timestamp is valid and timezone-aware | Critical | Reject and quarantine |
| PROC-DQ-18 | Currency equals `MAD` | Critical | Reject and quarantine |
| PROC-DQ-19 | No overlapping SCD Type 2 validity periods exist for one supplier | Critical | Reject or flag affected history |

### 9.8 SCD Type 2 Requirements — Supplier Dimension

The supplier dimension uses Slowly Changing Dimension Type 2.

**Tracked attributes:**

- `supplier_name`
- `city`
- `supplier_category`
- `is_active`

**Required SCD Type 2 metadata:**

- `effective_start_date`
- `effective_end_date`
- `is_current`
- `record_hash`

When a tracked supplier attribute changes:

1. Identify the current supplier version.
2. Compare incoming tracked attributes.
3. If no tracked attribute changes, do not create a new version.
4. Expire the previous version when a tracked attribute changes.
5. Insert a new current version.
6. Preserve previous versions for historical supplier analytics.

### 9.9 Processing and Traceability Requirements

1. Preserve supplier, purchase order, and delivery source records in Bronze.
2. Validate supplier and purchase order business keys.
3. Resolve supplier, store, and product references.
4. Validate order and delivery dates.
5. Aggregate multiple delivery events by purchase order line.
6. Calculate cumulative accepted and rejected quantities.
7. Derive consolidated delivery status and completion date.
8. Calculate on-time performance only when the delivery is complete.
9. Apply SCD Type 2 processing to supplier attributes.
10. Preserve delivery event identifiers for audit and traceability.
11. Record invalid records and reconciliation discrepancies in the monitoring layer.

### 9.10 Mapping to the Silver and Gold Layers

#### Supplier Dataset

| Source field | Silver field | Gold destination |
|---|---|---|
| `supplier_id` | `supplier_id` | Business identifier in `dim_supplier` |
| `supplier_name` | `supplier_name` | `dim_supplier.supplier_name` |
| `city` | `city` | `dim_supplier.city` |
| `supplier_category` | `supplier_category` | `dim_supplier.supplier_category` |
| `is_active` | `is_active` | `dim_supplier.is_active` |
| `effective_start_date` | `effective_start_date` | SCD Type 2 validity |

#### Purchase Order and Delivery Datasets

| Source field | Silver field | Gold destination |
|---|---|---|
| `purchase_order_id` | `purchase_order_id` | `fact_supplier_delivery.purchase_order_id` |
| `purchase_order_line_id` | `purchase_order_line_id` | `fact_supplier_delivery.purchase_order_line_id` |
| `supplier_id` | `supplier_id` | Resolved to `supplier_key` |
| `store_id` | `store_id` | Resolved to `store_key` |
| `product_id` | `product_id` | Resolved to `product_key` |
| `order_date` | `order_date` | `fact_supplier_delivery.order_date` |
| `expected_delivery_date` | `expected_delivery_date` | `fact_supplier_delivery.expected_delivery_date` |
| `delivery_timestamp` | `delivery_timestamp` | Derive actual completion date |
| `ordered_quantity` | `ordered_quantity` | `fact_supplier_delivery.ordered_quantity` |
| `received_quantity` | `total_received_quantity` | `fact_supplier_delivery.received_quantity` |
| `rejected_quantity` | `total_rejected_quantity` | `fact_supplier_delivery.rejected_quantity` |
| Derived status | `delivery_status` | `fact_supplier_delivery.delivery_status` |
| Derived on-time result | `on_time_flag` | `fact_supplier_delivery.on_time_flag` |

**Important:** The initial Gold fact aggregates partial delivery events into one record per purchase order line. Individual delivery events remain available in Silver for detailed audit and reconciliation.

### 9.11 Acceptance Criteria

The SRC-06 contract is accepted when:

- Supplier CSV files can be parsed according to the declared schema.
- Purchase order lines have unique business keys.
- Delivery events have unique identifiers.
- All supplier, store, and product references are resolved or quarantined.
- Partial deliveries are aggregated without duplicating ordered quantities.
- Accepted and rejected quantities are calculated correctly.
- Consolidated purchase order line statuses are derived consistently.
- On-time performance is calculated only for completed deliveries.
- Supplier attribute changes create SCD Type 2 versions.
- Procurement data remains traceable from Bronze through Gold.
