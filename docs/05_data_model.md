# RetailPulse — Data Model Specification

**Version:** 1.0
**Status:** Proposed
**Architecture:** Medallion Lakehouse + Star Schema

## 1. Purpose

This document defines the logical dimensional data model for RetailPulse. It specifies the fact tables, dimension tables, grain, keys, relationships, historical tracking, and data integrity requirements.

The model supports sales, inventory, and supplier analytics for a simulated Moroccan supermarket chain.

## 2. Modeling Principles

- Use a dimensional Star Schema for analytical workloads.
- Define the grain before designing each fact table.
- Use surrogate keys for dimension relationships.
- Preserve source business identifiers.
- Support historical changes through SCD Type 2.
- Model returns as separate transaction events.
- Support anonymous and identifiable loyalty customers.
- Preserve data lineage and reject invalid records explicitly.

## 3. Customer Identification Strategy

Most transactions are anonymous. A smaller proportion of transactions are associated with identifiable loyalty customers.

The customer dimension uses a designated anonymous member with `customer_key = 0`.

Anonymous transactions reference this member rather than generating artificial customer identities.

Identifiable loyalty customers receive pseudonymous business identifiers. Personally identifiable information is excluded from the analytical model.

## 4. Fact Tables

### 4.1 fact_sales

**Grain:** One product line within one POS transaction, including sale and return events.

**Primary key:** `sales_line_key`

**Foreign keys:**
- `date_key`
- `product_key`
- `customer_key`
- `store_key`

**Degenerate identifiers:**
- `transaction_id`
- `transaction_line_id`
- `original_sale_line_id`

**Measures and attributes:**
- `transaction_type`
- `quantity`
- `unit_price`
- `gross_amount`
- `discount_amount`
- `tax_amount`
- `net_sales_amount`

Sales quantities and monetary measures are positive. Return quantities and corresponding reversal amounts are negative. The original sale reference is retained whenever available.

### 4.2 fact_inventory_snapshot

**Grain:** One product at one store at the end of one business day.

**Primary key:** `snapshot_key`

**Foreign keys:**
- `date_key`
- `product_key`
- `store_key`

**Measures:**
- `opening_stock`
- `received_quantity`
- `sold_quantity`
- `returned_quantity`
- `adjustment_quantity`
- `minimum_available_stock`
- `closing_stock`
- `reserved_quantity`
- `reorder_level`
- `stockout_flag`

Inventory snapshots are periodic measurements. Closing stock from different dates must not be summed together.

### 4.3 fact_supplier_delivery

**Grain:** One purchase order line and its aggregated delivery outcome.

**Primary key:** `delivery_key`

**Foreign keys:**
- `supplier_key`
- `product_key`
- `store_key`
- `order_date_key`
- `promised_date_key`
- `actual_delivery_date_key`

**Degenerate identifiers:**
- `purchase_order_id`
- `purchase_order_line_id`

**Measures and attributes:**
- `ordered_quantity`
- `received_quantity`
- `rejected_quantity`
- `delivery_status`
- `on_time_flag`

Partial deliveries are aggregated before loading this fact table. Ordered quantity is stored once per purchase order line.

## 5. Dimension Tables

### 5.1 dim_product

- `product_key` — surrogate primary key
- `product_id` — natural business key
- `product_name`
- `category`
- `subcategory`
- `brand`
- `unit_cost`
- `selling_price`
- `is_active`
- `effective_start_date`
- `effective_end_date`
- `is_current`
- `record_hash`

### 5.2 dim_customer

- `customer_key` — surrogate primary key
- `customer_id` — pseudonymous business key
- `customer_segment`
- `city`
- `loyalty_status`
- `effective_start_date`
- `effective_end_date`
- `is_current`
- `record_hash`

The anonymous customer member uses `customer_key = 0`.

### 5.3 dim_store

- `store_key` — surrogate primary key
- `store_id` — natural business key
- `store_name`
- `city`
- `region`
- `store_type`
- `is_active`
- `effective_start_date`
- `effective_end_date`
- `is_current`
- `record_hash`

### 5.4 dim_supplier

- `supplier_key` — surrogate primary key
- `supplier_id` — natural business key
- `supplier_name`
- `city`
- `supplier_category`
- `is_active`
- `effective_start_date`
- `effective_end_date`
- `is_current`
- `record_hash`

### 5.5 dim_date

- `date_key` — primary key, integer in YYYYMMDD format
- `calendar_date`
- `day`
- `day_name`
- `week`
- `month`
- `quarter`
- `year`
- `is_weekend`
- `is_holiday`

## 6. Relationships

- `fact_sales` references product, customer, store, and transaction date.
- `fact_inventory_snapshot` references product, store, and snapshot date.
- `fact_supplier_delivery` references supplier, product, store, and order, promised, and actual delivery dates.

All fact-to-dimension relationships use surrogate keys.

## 7. Slowly Changing Dimensions

Selected dimensions use SCD Type 2.

Required historical attributes:

- `effective_start_date`
- `effective_end_date`
- `is_current`
- `record_hash`

Initial implementation targets:

- `dim_product`
- `dim_customer`
- `dim_store`
- `dim_supplier`

A changed tracked attribute creates a new dimension version with a new surrogate key. Previous versions remain available for historical reporting.

## 8. Data Integrity Rules

- Dimension surrogate keys must be unique.
- Current natural keys must be unique.
- Fact rows must respect their declared grain.
- Foreign keys must resolve to dimension members.
- Missing dimension references must use explicit unknown members.
- Return records should reference original sales when available.
- Return quantities must not exceed eligible sold quantities.
- Inventory balances must follow documented stock movement rules.
- SCD2 validity periods must not overlap for the same business key.
- Only one current version may exist per business key.

## 9. Financial Definitions

- Gross sales: positive sale amounts before discounts.
- Discounts: discounts granted, net of reversals on returned items.
- Net sales revenue: sales excluding VAT, less discounts and returns.
- Refund amount: actual amount refunded, tracked separately.
- Return rate: returned quantity divided by sold quantity for compatible product and date scopes.

Financial calculations must use consistent currency and tax conventions.

## 10. Future Extensions

Potential extensions include:

- Promotion dimension.
- Payment method dimension.
- Sales channel dimension.
- Dedicated purchase order fact.
- Product-store inventory movement fact.
- Customer cohort and retention analytics.

These extensions are not required for the initial implementation.
