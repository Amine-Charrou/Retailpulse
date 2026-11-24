# RetailPulse — Data Dictionary

**Version:** 1.0
**Status:** Proposed
**Currency:** Moroccan Dirham (MAD)
**Warehouse:** Databricks Lakehouse
**Storage Format:** Delta Lake

## 1. Purpose

This document defines the physical and business meaning of the columns used in RetailPulse's analytical data model.

It serves as a reference for developers, data engineers, analysts, and other project stakeholders.

For each table, the dictionary specifies:

- Column name and physical data type.
- Business definition.
- Primary and foreign key constraints.
- Nullability.
- Example values.
- Business and data quality rules.

## 2. Naming and Data Type Conventions

### 2.1 Naming conventions

| Element | Convention | Example |
|---|---|---|
| Tables | snake_case | `fact_sales` |
| Columns | snake_case | `transaction_date` |
| Fact tables | `fact_` prefix | `fact_inventory_snapshot` |
| Dimension tables | `dim_` prefix | `dim_product` |
| Surrogate keys | `_key` suffix | `product_key` |
| Natural keys | Source business identifier | `product_id` |
| Boolean attributes | `is_` or `has_` prefix | `is_current` |
| Dates | `_date` suffix | `order_date` |
| Timestamps | `_timestamp` suffix | `event_timestamp` |

### 2.2 Physical data types

| Data category | Databricks / Spark SQL type | Convention |
|---|---|---|
| Surrogate identifiers | BIGINT | Generated warehouse keys |
| Business identifiers | STRING | Source-system identifiers |
| Monetary values | DECIMAL(18,2) | MAD currency |
| Quantities | DECIMAL(18,3) | Supports weighted products |
| Dates | DATE | Business calendar dates |
| Timestamps | TIMESTAMP | Event and processing timestamps |
| Boolean attributes | BOOLEAN | True/false flags |
| Percentages and ratios | DECIMAL(8,4) | Stored as decimal ratios |
| Categorical attributes | STRING | Controlled business values |

### 2.3 Financial conventions

- All monetary amounts are expressed in MAD.
- Financial calculations use DECIMAL rather than floating-point types.
- VAT is represented separately from net sales revenue.
- Returns reverse the corresponding sales quantities and financial amounts.
- Refund settlement amounts are distinct from revenue reversals.
- Rounding is performed consistently at the documented financial calculation stage.

### 2.4 Temporal conventions

- Business dates use the Moroccan business calendar.
- Event timestamps are stored in UTC.
- Local business dates are derived using the `Africa/Casablanca` timezone.
- SCD Type 2 validity dates represent the period during which a dimension version is applicable.

## 3. Fact Tables

### 3.1 fact_sales

**Business purpose:** Stores transactional sales and return line items for sales performance and customer purchasing analytics.

**Grain:** One row per product line within one POS transaction.

**Primary key:** `sales_line_key`

**Foreign keys:**
- `date_key` → `dim_date.date_key`
- `product_key` → `dim_product.product_key`
- `customer_key` → `dim_customer.customer_key`
- `store_key` → `dim_store.store_key`

**Transaction types:**
- `SALE`: Completed sale.
- `RETURN`: Returned product and corresponding financial reversal.

| Column | Data type | Key | Nullable | Description | Example |
|---|---|---|---|---|---|
| sales_line_key | BIGINT | PK | No | Unique warehouse identifier for a sales line | 100001 |
| transaction_id | STRING | — | No | POS transaction identifier | TXN-20261124-001 |
| transaction_line_id | STRING | — | No | Unique source transaction line identifier | LINE-001 |
| transaction_type | STRING | — | No | SALE or RETURN | SALE |
| original_sale_line_id | STRING | — | Yes | Original sale line referenced by a return | LINE-001 |
| date_key | INT | FK | No | Transaction business date | 20261124 |
| product_key | BIGINT | FK | No | Product dimension version | 1001 |
| customer_key | BIGINT | FK | No | Customer dimension version; 0 for anonymous | 0 |
| store_key | BIGINT | FK | No | Store dimension version | 201 |
| quantity | DECIMAL(18,3) | — | No | Signed product quantity | 2.000 |
| unit_price | DECIMAL(18,2) | — | No | Unit selling price in MAD | 50.00 |
| gross_amount | DECIMAL(18,2) | — | No | Signed amount before discounts | 100.00 |
| discount_amount | DECIMAL(18,2) | — | No | Signed discount amount | 10.00 |
| tax_amount | DECIMAL(18,2) | — | No | Signed VAT amount | 15.00 |
| net_sales_amount | DECIMAL(18,2) | — | No | Signed revenue excluding VAT and discounts | 75.00 |

#### Business rules

1. Each `transaction_line_id` must be unique within its source transaction system.
2. `transaction_type` must be either `SALE` or `RETURN`.
3. Sale quantities and financial amounts are positive.
4. Return quantities and corresponding financial reversal amounts are negative.
5. Every fact row must reference valid dimension records.
6. Anonymous transactions reference the designated anonymous customer member.
7. A return should reference its original sale line whenever available.
8. A return must not exceed the remaining eligible quantity of its original sale line.
9. `net_sales_amount = gross_amount - discount_amount - tax_amount`.
10. Duplicate transaction lines must be detected and rejected or deduplicated according to the ingestion rules.

#### Analytical usage

This table supports:

- Gross sales analysis.
- Net revenue analysis.
- Product and category performance.
- Store performance.
- Average transaction value.
- Return rate.
- Customer purchasing behavior.

**Important:** Transaction amounts in this table represent signed sales accounting events, not necessarily the actual cash settlement or refund payment.


### 3.2 fact_inventory_snapshot

**Business purpose:** Stores daily inventory positions for every product at every supermarket store.

**Grain:** One row per product, per store, per business date.

**Primary key:** `snapshot_key`

**Composite business uniqueness:** `date_key + product_key + store_key`

**Foreign keys:**
- `date_key` → `dim_date.date_key`
- `product_key` → `dim_product.product_key`
- `store_key` → `dim_store.store_key`

**Snapshot frequency:** Daily, at the end of the Moroccan business day.

#### Column definitions

| Column | Data type | Key | Nullable | Description | Example |
|---|---|---|---|---|---|
| snapshot_key | BIGINT | PK | No | Unique warehouse snapshot identifier | 500001 |
| date_key | INT | FK | No | Inventory snapshot business date | 20261124 |
| product_key | BIGINT | FK | No | Product dimension version | 1001 |
| store_key | BIGINT | FK | No | Store dimension version | 201 |
| opening_stock | DECIMAL(18,3) | — | No | Available physical stock at start of day | 150.000 |
| received_quantity | DECIMAL(18,3) | — | No | Quantity received from suppliers during the day | 30.000 |
| minimum_available_stock | DECIMAL(18,3) | — | No | Lowest available sellable stock observed during the business day | 0.000 |
| sold_quantity | DECIMAL(18,3) | — | No | Quantity sold during the day, expressed as a positive measure | 20.000 |
| returned_quantity | DECIMAL(18,3) | — | No | Quantity returned to sellable inventory during the day | 2.000 |
| adjustment_quantity | DECIMAL(18,3) | — | No | Net inventory corrections, including shrinkage, damage, and stock corrections | -3.000 |
| closing_stock | DECIMAL(18,3) | — | No | Available physical stock at end of day | 159.000 |
| reserved_quantity | DECIMAL(18,3) | — | No | Quantity reserved and unavailable for new sales | 5.000 |
| reorder_level | DECIMAL(18,3) | — | No | Minimum stock threshold triggering replenishment | 25.000 |
| stockout_flag | BOOLEAN | — | No | Indicates whether available sellable stock reached zero during the day | FALSE |

#### Business rules

1. Each product-store-date combination must be unique.
2. Opening stock must equal the previous valid business day's closing stock, adjusted for documented inventory adjustments between snapshots.
3. Received, sold, and returned quantities must be non-negative measures.
4. `adjustment_quantity` can be positive, negative, or zero.
5. Closing stock must follow the inventory reconciliation formula:

   `closing_stock = opening_stock + received_quantity + returned_quantity - sold_quantity + adjustment_quantity`

6. Every inventory adjustment must have a traceable reason, such as shrinkage, damaged goods, stock correction, or another documented inventory movement.
7. Closing stock must not be negative unless an explicitly documented operational exception is permitted.
8. Reserved stock must not exceed available physical stock.
9. Stockout detection must use the minimum available sellable stock observed during the day, not only the closing stock.
10. `stockout_flag` must be TRUE when `minimum_available_stock` reaches zero or falls below zero during the business day.
11. Missing inventory snapshots must be identified rather than silently interpreted as zero inventory.
12. Snapshot records must reference valid product, store, and date dimension members.

#### KPI definitions

**Stockout rate:**

Percentage of monitored product-store observations with a stockout.

`Stockout rate = Stockout observations / Total monitored observations`

**Days of inventory:**

Estimated number of days current inventory can cover, based on average daily demand.

`Days of inventory = Current stock / Average daily demand`

**Inventory turnover:**

`Inventory turnover = Cost of goods sold / Average inventory value`

The reporting period and average inventory calculation must be consistent.

#### Analytical usage

This table supports:

- Daily inventory monitoring.
- Stockout detection.
- Replenishment analysis.
- Inventory turnover.
- Days of inventory remaining.
- Store-level inventory comparisons.
- Product availability analysis.

**Important:** Inventory snapshots are semi-additive. Quantities can be aggregated across products and stores for a given snapshot date, but daily closing balances must not be summed across different dates.


### 3.3 fact_supplier_delivery

**Business purpose:** Stores purchase order line delivery outcomes to measure supplier reliability, delivery performance, and procurement efficiency.

**Grain:** One row per purchase order line, including the aggregated outcome of all partial deliveries associated with that line.

**Primary key:** `delivery_key`

**Business uniqueness:** `purchase_order_id + purchase_order_line_id`

**Foreign keys:**
- `supplier_key` → `dim_supplier.supplier_key`
- `product_key` → `dim_product.product_key`
- `store_key` → `dim_store.store_key`
- `order_date_key` → `dim_date.date_key`
- `promised_date_key` → `dim_date.date_key`
- `actual_delivery_date_key` → `dim_date.date_key`

**Fact type:** Accumulating snapshot fact.

#### Column definitions

| Column | Data type | Key | Nullable | Description | Example |
|---|---|---|---|---|---|
| delivery_key | BIGINT | PK | No | Unique warehouse identifier for the purchase order line | 700001 |
| purchase_order_id | STRING | — | No | Purchase order identifier from the procurement system | PO-2026-001 |
| purchase_order_line_id | STRING | — | No | Unique line identifier within the purchase order | PO-2026-001-L01 |
| supplier_key | BIGINT | FK | No | Supplier dimension version | 301 |
| product_key | BIGINT | FK | No | Product dimension version | 1001 |
| store_key | BIGINT | FK | No | Destination store dimension version | 201 |
| order_date_key | INT | FK | No | Date the purchase order was created | 20261110 |
| promised_date_key | INT | FK | No | Supplier's promised delivery date | 20261115 |
| actual_delivery_date_key | INT | FK | Yes | Date the final accepted delivery was received | 20261116 |
| ordered_quantity | DECIMAL(18,3) | — | No | Total quantity ordered | 100.000 |
| received_quantity | DECIMAL(18,3) | — | No | Total quantity physically received across all shipments | 95.000 |
| rejected_quantity | DECIMAL(18,3) | — | No | Total quantity rejected during receiving inspections | 2.000 |
| delivery_status | STRING | — | No | Current delivery outcome status | PARTIALLY_RECEIVED |
| on_time_flag | BOOLEAN | — | Yes | Indicates whether the completed delivery met the promised date | FALSE |

#### Allowed delivery statuses

| Status | Definition |
|---|---|
| PENDING | Purchase order has been created but no delivery has been received |
| PARTIALLY_RECEIVED | Some ordered quantity has been received, but the order line is not finalized |
| FULLY_RECEIVED | All accepted ordered quantities have been received |
| PARTIALLY_FULFILLED | Order line has been closed with an accepted quantity below the ordered quantity |
| CANCELLED | Purchase order line has been cancelled |
| OVERDUE | Promised delivery date has passed and the order line remains incomplete |

#### Business rules

1. Each purchase order line must have a unique business identifier.
2. `ordered_quantity` must be greater than zero.
3. `received_quantity` and `rejected_quantity` must be non-negative.
4. Partial deliveries must be aggregated before loading the Gold fact table.
5. Ordered quantity must be stored once per purchase order line.
6. Accepted quantity is calculated as:

   `accepted_quantity = received_quantity - rejected_quantity`

7. Accepted quantity must not exceed ordered quantity unless an explicitly documented over-delivery exception is approved.
8. A purchase order line can only be marked `FULLY_RECEIVED` when its accepted quantity satisfies the agreed fulfillment tolerance.
9. A line closed below the agreed fulfillment tolerance must be classified as `PARTIALLY_FULFILLED`.
10. `actual_delivery_date_key` represents the date of the final accepted delivery for a completed order line.
11. `on_time_flag` is calculated using the final accepted delivery date and the promised delivery date.
12. `on_time_flag` remains NULL while delivery completion has not occurred.
13. Cancelled order lines must not be treated as completed deliveries.
14. Every record must reference valid supplier, product, store, and date dimension members.
15. Changes to open purchase order lines must update the existing fact record rather than create duplicate records.

#### KPI definitions

**Supplier on-time delivery rate:**

`On-time delivery rate = On-time completed order lines / Eligible completed order lines`

Cancelled and still-pending orders are excluded from the denominator.

**Supplier fulfillment rate:**

`Fulfillment rate = Total accepted quantity / Total ordered quantity`

The reporting period and treatment of cancelled quantities must be documented.

**Average delivery delay:**

`Average delay = Average(actual delivery date - promised delivery date)`

Calculated for completed order lines.

**Supplier rejection rate:**

`Rejection rate = Total rejected quantity / Total received quantity`

#### Analytical usage

This table supports:

- Supplier reliability analysis.
- On-time delivery monitoring.
- Purchase order fulfillment.
- Delivery delay analysis.
- Product procurement performance.
- Supplier comparison and ranking.
- Procurement risk identification.

**Important:** This is an accumulating snapshot fact. Its records evolve as purchase order lines move from pending to partial or completed states. Historical changes to open order lines should be auditable through the upstream procurement events and pipeline history.




## 4. Dimension Tables

### 4.1 dim_product

**Business purpose:** Stores descriptive product attributes used for sales, inventory, and procurement analytics.

**Primary key:** `product_key`

**Natural key:** `product_id`

**Historical tracking:** SCD Type 2.

Each product can have multiple historical versions, but only one version can be current at a given time.

#### Column definitions

| Column | Data type | Key | Nullable | Description | Example |
|---|---|---|---|---|---|
| product_key | BIGINT | PK | No | Unique surrogate identifier for a product version | 1001 |
| product_id | STRING | NK | No | Source-system product identifier | P001 |
| product_name | STRING | — | No | Commercial product name | Moroccan Olive Oil 1L |
| category | STRING | — | No | Main product category | Grocery |
| subcategory | STRING | — | Yes | Product subcategory | Cooking Oil |
| brand | STRING | — | Yes | Product brand | Atlas |
| unit_cost | DECIMAL(18,2) | — | No | Standard procurement cost per selling unit in MAD | 45.00 |
| selling_price | DECIMAL(18,2) | — | No | Standard selling price per selling unit in MAD | 59.90 |
| is_active | BOOLEAN | — | No | Indicates whether the product is currently offered | TRUE |
| effective_start_date | DATE | — | No | Date from which this dimension version is valid | 2026-01-01 |
| effective_end_date | DATE | — | No | Date until which this dimension version is valid | 9999-12-31 |
| is_current | BOOLEAN | — | No | Indicates whether this is the current product version | TRUE |
| record_hash | STRING | — | No | Hash of tracked attributes used to detect changes | a1b2c3... |

#### Business rules

1. `product_key` must be unique and generated by the warehouse.
2. `product_id` must be retained as the source business identifier.
3. Only one current dimension version may exist for each `product_id`.
4. A change to a tracked attribute creates a new SCD Type 2 record.
5. Previous versions must remain available for historical reporting.
6. `effective_start_date` must be earlier than or equal to `effective_end_date`.
7. Historical validity periods for the same product must not overlap.
8. `selling_price` and `unit_cost` must be non-negative.
9. Product names and categories must not be null or empty.
10. `record_hash` must be generated consistently using the selected tracked attributes.

#### SCD Type 2 tracked attributes

- `product_name`
- `category`
- `subcategory`
- `brand`
- `unit_cost`
- `selling_price`
- `is_active`

A change to any of these attributes creates a new dimension version.

#### Analytical usage

This dimension supports:

- Revenue by product and category.
- Product profitability analysis.
- Inventory valuation.
- Product performance comparisons.
- Historical price and category analysis.
- Product assortment analysis.

**Important:** Historical sales must reference the product dimension version valid at the transaction date, rather than automatically referencing the latest product version.


### 4.2 dim_customer

**Business purpose:** Stores pseudonymous customer information for loyalty program analytics, customer segmentation, and purchasing behavior analysis.

**Primary key:** `customer_key`

**Natural key:** `customer_id`

**Historical tracking:** SCD Type 2 for identified loyalty customers.

**Customer identification strategy:** Most transactions are anonymous. Only customers associated with the loyalty program have identifiable, pseudonymous customer records.

#### Column definitions

| Column | Data type | Key | Nullable | Description | Example |
|---|---|---|---|---|---|
| customer_key | BIGINT | PK | No | Unique surrogate identifier for a customer dimension version | 2001 |
| customer_id | STRING | NK | No | Pseudonymous customer identifier | CUST-001 |
| customer_segment | STRING | — | No | Customer purchasing segment | REGULAR |
| city | STRING | — | Yes | Customer city, if known | Agadir |
| loyalty_status | STRING | — | No | Loyalty program membership status | ACTIVE |
| effective_start_date | DATE | — | No | Start of the customer version validity period | 2026-01-01 |
| effective_end_date | DATE | — | No | End of the customer version validity period | 9999-12-31 |
| is_current | BOOLEAN | — | No | Indicates whether the version is current | TRUE |
| record_hash | STRING | — | No | Hash used to detect tracked attribute changes | d4e5f6... |

#### Anonymous customer member

RetailPulse uses a dedicated anonymous customer dimension record.

| Attribute | Value |
|---|---|
| customer_key | 0 |
| customer_id | ANONYMOUS |
| customer_segment | UNKNOWN |
| city | NULL |
| loyalty_status | NOT_ENROLLED |
| effective_start_date | 1900-01-01 |
| effective_end_date | 9999-12-31 |
| is_current | TRUE |

This member is permanent and does not participate in SCD Type 2 versioning.

Every anonymous sales transaction references `customer_key = 0`.

Anonymous transactions must not generate fabricated customer identities.

#### Allowed customer segments

| Segment | Meaning |
|---|---|
| NEW | Recently enrolled customer with limited purchase history |
| REGULAR | Customer with recurring purchases |
| HIGH_VALUE | Customer with high purchasing value |
| INACTIVE | Customer with no recent qualifying purchases |
| UNKNOWN | Customer without sufficient information |

Segment thresholds and evaluation periods will be configurable.

#### Allowed loyalty statuses

| Status | Meaning |
|---|---|
| ACTIVE | Customer has an active loyalty account |
| INACTIVE | Customer has an inactive loyalty account |
| SUSPENDED | Customer's loyalty account is temporarily suspended |
| NOT_ENROLLED | Customer is not enrolled in the loyalty program |

#### Business rules

1. `customer_key` must be unique.
2. `customer_id` must be pseudonymous for identified customers.
3. Only one current dimension version may exist for each identified customer.
4. The anonymous customer member must always exist with `customer_key = 0`.
5. Anonymous transactions must reference the anonymous member.
6. The anonymous member must never be included in distinct identified-customer counts.
7. A change to a tracked attribute creates a new SCD Type 2 version.
8. Historical validity periods for the same customer must not overlap.
9. `customer_segment` and `loyalty_status` must use controlled values.
10. Personally identifiable information must not be stored in this analytical dimension.
11. Customer segmentation must use documented evaluation periods and thresholds.
12. Historical transactions must reference the customer dimension version valid at the transaction date.

#### SCD Type 2 tracked attributes

- `customer_segment`
- `city`
- `loyalty_status`

A change to one of these attributes creates a new customer dimension version.

#### Analytical usage

This dimension supports:

- Loyalty customer purchasing behavior.
- Revenue by customer segment.
- Customer retention analysis.
- Identified customer purchase frequency.
- Customer segment evolution.
- Loyalty program performance.

**Important:** Anonymous transactions contribute to overall sales KPIs, but they must not be interpreted as purchases by one individual customer. Customer-level retention, frequency, and lifetime-value metrics apply only to identifiable loyalty customers.


### 4.3 dim_store

**Business purpose:** Stores descriptive information about supermarket locations for geographical and operational performance analysis.

**Primary key:** `store_key`

**Natural key:** `store_id`

**Historical tracking:** SCD Type 2 for selected store attributes.

**Initial scope:** 15 simulated supermarket stores across five Moroccan cities.

#### Column definitions

| Column | Data type | Key | Nullable | Description | Example |
|---|---|---|---|---|---|
| store_key | BIGINT | PK | No | Unique surrogate identifier for a store dimension version | 301 |
| store_id | STRING | NK | No | Source-system store identifier | STORE-001 |
| store_name | STRING | — | No | Commercial store name | RetailPulse Casablanca Maarif |
| city | STRING | — | No | Moroccan city where the store operates | Casablanca |
| region | STRING | — | No | Moroccan administrative region | Casablanca-Settat |
| store_type | STRING | — | No | Store operational classification | SUPERMARKET |
| is_active | BOOLEAN | — | No | Indicates whether the store is operational | TRUE |
| effective_start_date | DATE | — | No | Start of the store version validity period | 2026-01-01 |
| effective_end_date | DATE | — | No | End of the store version validity period | 9999-12-31 |
| is_current | BOOLEAN | — | No | Indicates whether this is the current store version | TRUE |
| record_hash | STRING | — | No | Hash used to detect tracked attribute changes | a7b8c9... |

#### Initial geographical distribution

| City | Administrative region | Planned stores |
|---|---|---:|
| Casablanca | Casablanca-Settat | 5 |
| Rabat | Rabat-Salé-Kénitra | 3 |
| Marrakech | Marrakech-Safi | 3 |
| Agadir | Souss-Massa | 2 |
| Tangier | Tanger-Tétouan-Al Hoceïma | 2 |
| **Total** | | **15** |

This distribution represents the initial synthetic business scenario. It is configurable in the data generator.

#### Allowed store types

| Store type | Description |
|---|---|
| SUPERMARKET | Standard supermarket |
| HYPERMARKET | Large-format retail store |
| EXPRESS | Small-format convenience store |

#### Business rules

1. `store_key` must be unique.
2. `store_id` must be unique as a current business identifier.
3. Store names, cities, regions, and store types must not be null or empty.
4. `store_type` must use an approved classification.
5. `is_active` indicates whether the store currently operates.
6. Changes to tracked attributes create a new SCD Type 2 version.
7. Historical validity periods for the same store must not overlap.
8. Only one current dimension version may exist per `store_id`.
9. Every sales, inventory, and supplier delivery fact must reference a valid store dimension member.
10. Historical facts must retain the store version valid at the corresponding business event date.

#### SCD Type 2 tracked attributes

- `store_name`
- `city`
- `region`
- `store_type`
- `is_active`

A change to one of these attributes creates a new store dimension version.

#### Analytical usage

This dimension supports:

- Revenue by city and store.
- Store performance comparisons.
- Inventory availability by location.
- Regional sales analysis.
- Supplier delivery performance by destination store.
- Store-level growth and operational analysis.

**Important:** The initial 15-store distribution is synthetic. It should not be presented as actual data about a real supermarket chain.


### 4.4 dim_supplier

**Business purpose:** Stores descriptive information about suppliers providing products to the RetailPulse supermarket chain.

**Primary key:** `supplier_key`

**Natural key:** `supplier_id`

**Historical tracking:** SCD Type 2.

**Initial scope:** Between 30 and 100 simulated suppliers.

#### Column definitions

| Column | Data type | Key | Nullable | Description | Example |
|---|---|---|---|---|---|
| supplier_key | BIGINT | PK | No | Unique surrogate identifier for a supplier dimension version | 401 |
| supplier_id | STRING | NK | No | Source-system supplier identifier | SUP-001 |
| supplier_name | STRING | — | No | Commercial supplier name | Atlas Food Distribution |
| city | STRING | — | Yes | Supplier's registered or operational city | Casablanca |
| supplier_category | STRING | — | No | Main supplier business category | FOOD_DISTRIBUTION |
| is_active | BOOLEAN | — | No | Indicates whether the supplier is currently approved and active | TRUE |
| effective_start_date | DATE | — | No | Start of the supplier version validity period | 2026-01-01 |
| effective_end_date | DATE | — | No | End of the supplier version validity period | 9999-12-31 |
| is_current | BOOLEAN | — | No | Indicates whether this is the current supplier version | TRUE |
| record_hash | STRING | — | No | Hash used to detect tracked attribute changes | e1f2a3... |

#### Allowed supplier categories

| Category | Description |
|---|---|
| FOOD_DISTRIBUTION | Suppliers of food products |
| BEVERAGE | Suppliers of drinks and beverages |
| HOUSEHOLD | Household and cleaning products |
| PERSONAL_CARE | Hygiene and personal care products |
| FRESH_PRODUCE | Fresh fruits and vegetables |
| DAIRY | Dairy products |
| OTHER | Other supplier categories |

#### Business rules

1. `supplier_key` must be unique.
2. `supplier_id` must be unique as a current business identifier.
3. Supplier names and categories must not be null or empty.
4. `supplier_category` must use an approved classification.
5. `is_active` indicates whether the supplier is approved for current procurement activities.
6. Changes to tracked attributes create a new SCD Type 2 version.
7. Historical validity periods for the same supplier must not overlap.
8. Only one current dimension version may exist per `supplier_id`.
9. Every supplier delivery fact must reference a valid supplier dimension member.
10. Historical purchase order lines must reference the supplier version valid at the relevant business event date.
11. Supplier identifiers must remain stable across changes in descriptive attributes.

#### SCD Type 2 tracked attributes

- `supplier_name`
- `city`
- `supplier_category`
- `is_active`

A change to one of these attributes creates a new supplier dimension version.

#### Analytical usage

This dimension supports:

- Supplier delivery performance.
- On-time delivery rate by supplier.
- Supplier rejection rate.
- Procurement concentration analysis.
- Supplier category comparisons.
- Supplier reliability rankings.
- Historical supplier classification analysis.

**Important:** The initial supplier population is synthetic and must be generated deterministically for reproducible testing.


### 4.5 dim_date

**Business purpose:** Provides a standardized calendar dimension for all time-based analytical operations.

**Primary key:** `date_key`

**Natural key:** `calendar_date`

**Historical tracking:** Not applicable. The calendar dimension is pre-generated and its attributes are deterministic.

**Calendar coverage:** The dimension should cover the historical simulation period and a configurable future period.

#### Column definitions

| Column | Data type | Key | Nullable | Description | Example |
|---|---|---|---|---|---|
| date_key | INT | PK | No | Integer date identifier in YYYYMMDD format | 20261124 |
| calendar_date | DATE | NK | No | Actual calendar date | 2026-11-24 |
| day | INT | — | No | Day of the month | 24 |
| day_name | STRING | — | No | Full weekday name | Tuesday |
| day_of_week | INT | — | No | ISO weekday number, Monday=1 and Sunday=7 | 2 |
| week | INT | — | No | ISO week number | 48 |
| month | INT | — | No | Calendar month number | 11 |
| month_name | STRING | — | No | Full month name | November |
| quarter | INT | — | No | Calendar quarter | 4 |
| year | INT | — | No | Calendar year | 2026 |
| is_weekend | BOOLEAN | — | No | Indicates Saturday or Sunday | FALSE |
| is_holiday | BOOLEAN | — | No | Indicates an officially recognized Moroccan public holiday | FALSE |
| holiday_name | STRING | — | Yes | Name of the holiday, if applicable | Independence Day |
| is_ramadan | BOOLEAN | — | No | Indicates whether the date falls within Ramadan | FALSE |
| is_summer_season | BOOLEAN | — | No | Indicates whether the date falls within the configured summer season | FALSE |

#### Business rules

1. `date_key` must be unique and follow the YYYYMMDD integer format.
2. `calendar_date` must be unique.
3. Every calendar date in the configured coverage period must exist.
4. `day_of_week` must follow ISO weekday numbering: Monday=1 and Sunday=7.
5. `week` must follow ISO-8601 week numbering.
6. `quarter` must be between 1 and 4.
7. `month` must be between 1 and 12.
8. `is_weekend` must be TRUE for Saturday and Sunday.
9. `is_holiday` must be based on a maintained Moroccan holiday calendar.
10. `holiday_name` must be populated when `is_holiday` is TRUE.
11. `is_ramadan` must be based on a configurable Ramadan calendar.
12. Islamic holiday and Ramadan dates must account for the official Moroccan calendar, which may depend on lunar observation.
13. `is_summer_season` must follow a documented configurable business definition.
14. All fact table date references must resolve to a valid date dimension record.

#### Moroccan business calendar

RetailPulse will use Moroccan business-calendar attributes to support more realistic retail analytics.

Relevant calendar events include:

- New Year's Day.
- Amazigh New Year.
- Labour Day.
- Throne Day.
- Oued Ed-Dahab Day.
- Revolution of the King and the People.
- Youth Day.
- Green March Day.
- Independence Day.
- Eid al-Fitr.
- Eid al-Adha.
- Islamic New Year.
- Prophet's Birthday.
- Ramadan.

Official and lunar-calendar dates must be maintained as reference data rather than permanently hardcoded assumptions.

#### Analytical usage

This dimension supports:

- Daily, weekly, monthly, quarterly, and annual sales trends.
- Year-over-year revenue comparisons.
- Weekend versus weekday purchasing behavior.
- Ramadan sales analysis.
- Holiday sales analysis.
- Seasonal demand forecasting.
- Inventory seasonality.
- Supplier delivery performance over time.

**Important:** `dim_date` is shared across all fact tables. Supplier delivery uses role-playing date relationships for order date, promised date, and actual delivery date. These relationships all reference the same date dimension.

## 5. Slowly Changing Dimensions — Type 2

### 5.1 Purpose

RetailPulse uses Slowly Changing Dimensions Type 2 to preserve historical changes to selected descriptive attributes.

Instead of overwriting an existing dimension record, the pipeline expires the previous version and inserts a new version with a new surrogate key.

### 5.2 Applicable dimensions

| Dimension | SCD Type 2 | Tracked attributes |
|---|---|---|
| dim_product | Yes | Product name, category, subcategory, brand, unit cost, selling price, active status |
| dim_customer | Yes | Customer segment, city, loyalty status |
| dim_store | Yes | Store name, city, region, store type, active status |
| dim_supplier | Yes | Supplier name, city, supplier category, active status |
| dim_date | No | Static calendar attributes |

The anonymous customer member is a permanent special record and does not participate in SCD Type 2 versioning.

### 5.3 Required technical columns

| Column | Data type | Description |
|---|---|---|
| effective_start_date | DATE | First date on which the dimension version is valid |
| effective_end_date | DATE | Last date on which the dimension version is valid |
| is_current | BOOLEAN | Indicates whether the record is the current version |
| record_hash | STRING | Hash of tracked attributes used to detect changes |

### 5.4 Versioning example

Suppose product P001 changes its category.

| product_key | product_id | category | effective_start_date | effective_end_date | is_current |
|---:|---|---|---|---|---|
| 1001 | P001 | Beverages | 2026-01-01 | 2026-06-30 | FALSE |
| 1501 | P001 | Household | 2026-07-01 | 9999-12-31 | TRUE |

The original version remains available for historical reporting.

### 5.5 SCD Type 2 processing rules

1. Identify the natural business key of the incoming record.
2. Compare the incoming tracked attributes against the current dimension version.
3. Calculate a deterministic record hash.
4. If no tracked attributes have changed, do not create a new version.
5. If tracked attributes have changed, expire the previous version.
6. Insert a new version with a new surrogate key.
7. Maintain non-overlapping validity periods.
8. Ensure only one current version exists per natural key.
9. Resolve fact foreign keys using the dimension version valid at the business event date.
10. Handle late-arriving dimension changes through documented historical correction procedures.

### 5.6 Validity period convention

RetailPulse uses inclusive business-date validity:

- `effective_start_date` is inclusive.
- `effective_end_date` is inclusive.
- The current version uses `9999-12-31` as its end date.

A new version starts on the day after the previous version expires, unless the business event requires a documented correction to historical validity.

### 5.7 Technical implementation considerations

- Surrogate key generation must remain unique.
- Hash calculations must use consistent attribute ordering and null normalization.
- Hash inputs must exclude technical columns such as surrogate keys and effective dates.
- SCD2 writes must be idempotent.
- Concurrent updates to the same natural key must be controlled.
- Historical fact records must retain their original dimension version references.

The implementation will use Delta Lake MERGE operations where supported and will include tests for duplicate versions, overlapping periods, and incorrect current-record counts.


## 6. Consolidated KPI Definitions

This section standardizes the business calculations used by RetailPulse dashboards and analytical queries.

### 6.1 Sales KPIs

| KPI | Definition | Calculation |
|---|---|---|
| Gross sales | Total positive sale amount before discounts | Sum of gross amounts for SALE records |
| Discount amount | Total discounts granted, net of reversals | Sum of signed discount amounts |
| Net sales revenue | Revenue excluding VAT, after discounts and returns | Sum of signed net sales amounts |
| Average transaction value | Average net revenue per eligible transaction | Net sales revenue / Number of eligible transactions |
| Return rate | Percentage of sold quantity subsequently returned | Returned quantity / Sold quantity |

### 6.2 Inventory KPIs

| KPI | Definition | Calculation |
|---|---|---|
| Stockout rate | Percentage of monitored product-store observations with a stockout | Stockout observations / Total monitored observations |
| Inventory turnover | Number of times inventory is sold and replenished over a period | Cost of goods sold / Average inventory value |
| Days of inventory | Estimated days of demand covered by available stock | Current stock / Average daily demand |
| Inventory value | Estimated value of inventory at cost | Sum of closing stock × unit cost |

### 6.3 Supplier KPIs

| KPI | Definition | Calculation |
|---|---|---|
| On-time delivery rate | Percentage of eligible completed order lines delivered on time | On-time completed lines / Eligible completed lines |
| Fulfillment rate | Percentage of ordered quantities accepted | Accepted quantity / Ordered quantity |
| Average delivery delay | Average difference between actual and promised delivery dates | Average(actual date − promised date) |
| Rejection rate | Percentage of received quantity rejected | Rejected quantity / Received quantity |

### 6.4 KPI calculation rules

1. All financial KPIs must use MAD.
2. Revenue calculations exclude VAT.
3. Sales and returns must be included with their appropriate signs.
4. Average transaction value must count distinct eligible transactions, not transaction lines.
5. Return rate must use compatible product and transaction-date scopes.
6. Inventory turnover must use cost of goods sold rather than sales revenue.
7. Inventory KPIs must respect snapshot-date semantics.
8. Supplier delivery KPIs must exclude cancelled and incomplete orders when calculating completed delivery performance.
9. Division-by-zero cases must return NULL or an explicitly documented not-applicable result.
10. KPI definitions must be implemented consistently across SQL queries and dashboards.

**Important:** Revenue, refund settlement, inventory valuation, and supplier fulfillment are distinct business concepts and must not be combined into a single ambiguous metric.



## 7. Data Quality and Integrity Controls

### 7.1 General controls

- Required fields must not contain NULL values.
- Natural and surrogate keys must respect their uniqueness constraints.
- Categorical attributes must use approved values.
- Monetary amounts must use decimal precision.
- Invalid records must be quarantined with a rejection reason.
- Every transformation must preserve source lineage.

### 7.2 Fact table controls

| Table | Control |
|---|---|
| fact_sales | Unique transaction line identifiers within their source system |
| fact_sales | Valid transaction types and signed amounts |
| fact_sales | Valid original sale references for linked returns |
| fact_inventory_snapshot | Unique product-store-date combinations |
| fact_inventory_snapshot | Inventory reconciliation formula |
| fact_inventory_snapshot | Valid stock movement quantities |
| fact_supplier_delivery | Unique purchase order line identifiers |
| fact_supplier_delivery | Valid ordered, received, and rejected quantities |
| fact_supplier_delivery | Valid delivery status transitions |

### 7.3 Dimension table controls

| Dimension | Control |
|---|---|
| dim_product | Unique current product business key |
| dim_customer | Permanent anonymous customer member |
| dim_store | Unique current store business key |
| dim_supplier | Unique current supplier business key |
| dim_date | Continuous calendar coverage and unique dates |

### 7.4 Historical integrity controls

- Exactly one current SCD2 version per identified natural key.
- No overlapping validity periods.
- Valid effective start and end dates.
- Unique surrogate keys across historical versions.
- Correct fact-to-dimension version resolution.

### 7.5 Rejected record handling

Records failing mandatory quality checks must be stored in a quarantine structure.

Each rejected record should retain:

- Source system.
- Source record identifier.
- Ingestion timestamp.
- Rejection timestamp.
- Rejection reason.
- Relevant source payload or payload reference.
- Pipeline run identifier.

Rejected records must remain available for investigation and controlled reprocessing.

## 8. Document Maintenance

This dictionary must be updated whenever:

- A table is added or removed.
- A column changes name or data type.
- A business definition changes.
- A KPI formula changes.
- A new quality constraint is introduced.
- A dimension's historical tracking strategy changes.

All changes must remain consistent with the RetailPulse data model and technical specification.