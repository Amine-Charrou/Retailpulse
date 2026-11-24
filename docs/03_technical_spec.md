# RetailPulse — Technical Specification

**Project:** RetailPulse
**Version:** 1.0
**Status:** Proposed technical design
**Related documents:** Business Case and Functional Specification

## 1. Purpose

This document defines the technical architecture, technologies, storage strategy, processing mechanisms, development practices and operational constraints of RetailPulse.

The initial implementation targets Databricks Free Edition while maintaining a modular architecture that can be migrated to a more capable Databricks environment.

## 2. Technology Stack

| Component | Technology | Responsibility |
|---|---|---|
| Development | VS Code | Local development |
| Programming language | Python 3.12 | Data generation and application logic |
| Version control | Git and GitHub | Source control |
| Synthetic data | Faker, NumPy | Retail data simulation |
| Data manipulation | Pandas | Local data preparation |
| Distributed processing | PySpark | Data transformations |
| Query language | Spark SQL | Analytical transformations |
| Data platform | Databricks | Managed processing |
| Storage | Delta Lake | Transactional data storage |
| Data governance | Unity Catalog | Data organization and access |
| File ingestion | Auto Loader | Incremental file discovery |
| Streaming | Spark Structured Streaming | Incremental event processing |
| Testing | pytest | Automated validation |
| Code quality | Ruff | Linting |
| Visualization | Databricks SQL dashboards | Business analytics |

## 3. Environment Architecture

### 3.1 Local Development Environment

The local environment runs on macOS using Python 3.12 and an isolated virtual environment.

Responsibilities:

- Generate synthetic retail datasets.
- Develop reusable Python modules.
- Validate schemas and business rules.
- Run unit tests.
- Perform static code analysis.
- Manage source control and documentation.

Local execution must not depend on an active Databricks session for basic unit tests.

### 3.2 Databricks Environment

Databricks will execute distributed processing workloads.

Responsibilities:

- Execute Spark batch transformations.
- Ingest incremental JSON files.
- Store Delta Lake tables.
- Run data quality checks.
- Build dimensional models.
- Execute scheduled workloads.
- Support analytical queries.

The initial environment uses Databricks Free Edition and serverless compute.

## 4. Platform Constraints

The design must account for the following Free Edition limitations:

- Serverless compute only.
- Limited compute usage and fair-use quotas.
- One SQL warehouse, limited to 2X-Small.
- Maximum five concurrent job tasks per account.
- One active Lakeflow pipeline per pipeline type.
- No guarantee of production-grade availability or SLA.
- Restricted outbound network access.

Serverless notebooks and jobs support Spark Connect APIs. Implementation must avoid unsupported Spark APIs, including RDD-based operations.

Streaming notebooks and jobs must use supported triggers. The initial implementation will use `Trigger.AvailableNow()`.

These constraints are implementation boundaries, not permanent architectural requirements.

## 5. Lakehouse Architecture

RetailPulse follows the Medallion Architecture.

### 5.1 Bronze Layer

Purpose: Preserve source data and ingestion lineage.

Responsibilities:

- Ingest historical datasets.
- Ingest incremental JSON events.
- Preserve original source attributes.
- Add ingestion metadata.
- Track source files and processing runs.

Proposed tables:

- `bronze.sales`
- `bronze.inventory`
- `bronze.products`
- `bronze.customers`
- `bronze.stores`
- `bronze.suppliers`
- `bronze.purchase_orders`

### 5.2 Silver Layer

Purpose: Produce validated, standardized and integrated datasets.

Responsibilities:

- Normalize data types.
- Standardize timestamps and monetary values.
- Deduplicate records.
- Apply business validation.
- Resolve relationships.
- Handle missing and inconsistent values.
- Maintain selected historical dimension changes.

Proposed tables:

- `silver.sales`
- `silver.inventory`
- `silver.products`
- `silver.customers`
- `silver.stores`
- `silver.suppliers`
- `silver.purchase_orders`

Invalid records will be stored in appropriate quarantine datasets.

### 5.3 Gold Layer

Purpose: Provide analytical datasets for business reporting.

Dimensions:

- `dim_date`
- `dim_product`
- `dim_customer`
- `dim_store`
- `dim_supplier`

Facts:

- `fact_sales`
- `fact_inventory_snapshot`
- `fact_supplier_delivery`

Additional business aggregates may be created when query requirements justify them.

## 6. Storage Strategy

Delta Lake will be the primary table format.

Requirements:

- Use Unity Catalog-managed tables where available.
- Use Unity Catalog Volumes for non-tabular landing files and pipeline support files.
- Keep source files separate from curated tables.
- Maintain separate schemas for Bronze, Silver, Gold and Monitoring.
- Store streaming checkpoints and Auto Loader schema metadata in appropriate Unity Catalog-managed locations.
- Keep checkpoint locations separate from target table directories.

Proposed namespace:

`retailpulse_dev`

Schemas:

- `bronze`
- `silver`
- `gold`
- `monitoring`

Proposed Volume:

`landing`

## 7. Batch Processing Architecture

Historical datasets will be generated locally and uploaded to the Databricks landing Volume.

Processing sequence:

1. Validate source file availability.
2. Read the source dataset.
3. Apply schema validation.
4. Write raw records into Bronze Delta tables.
5. Transform Bronze records into Silver.
6. Execute data quality checks.
7. Quarantine invalid records.
8. Build Gold dimensions and facts.
9. Record execution metrics.

Batch processing must support repeatable execution.

Stable business identifiers and appropriate merge or overwrite strategies will be used to prevent duplicate curated records.

## 8. Streaming Architecture

### 8.1 Event Generation

Simulated POS transactions will be generated as JSON files.

Each event should include:

- `event_id`
- `transaction_id`
- `transaction_line_id`
- `store_id`
- `product_id`
- `customer_id` where applicable
- `quantity`
- `unit_price`
- `discount_amount`
- `event_time`
- `event_type`

### 8.2 Ingestion

The preferred ingestion mechanism is Databricks Auto Loader using the `cloudFiles` source.

The system will use:

- JSON source files.
- Explicit or controlled schema evolution.
- Unity Catalog Volume paths.
- Dedicated schema metadata locations.
- Dedicated checkpoint locations.

If Auto Loader is unavailable in the verified workspace configuration, a supported Structured Streaming file source will be evaluated as a fallback.

### 8.3 Execution Model

The initial implementation will use `Trigger.AvailableNow()`.

Each execution:

1. Discovers files not previously processed.
2. Processes available events incrementally.
3. Writes raw events to Bronze.
4. Applies downstream transformations.
5. Records execution metrics.
6. Terminates after processing available input.

Repeated scheduled executions will simulate ongoing incremental processing.

### 8.4 Event Processing Controls

The streaming implementation must support:

- Stable event identifiers.
- Duplicate detection.
- Event-time tracking.
- Ingestion-time tracking.
- Late-arriving event handling.
- Checkpoint-based recovery.
- Idempotent curated writes.

Auto Loader and Delta Lake provide ingestion and storage reliability capabilities, but business-level deduplication and reconciliation must still be explicitly implemented and tested.

The project will not claim end-to-end exactly-once business processing without evidence from its implementation and tests.

## 9. Data Quality Architecture

The quality framework will be modular and reusable.

Validation categories:

- Completeness.
- Uniqueness.
- Validity.
- Referential integrity.
- Consistency.
- Timeliness.

Every validation result should include:

- Rule identifier.
- Dataset name.
- Processing run identifier.
- Validation status.
- Affected record count.
- Rejection reason where applicable.

Proposed monitoring tables:

- `pipeline_runs`
- `data_quality_results`
- `rejected_records`
- `ingestion_metrics`

## 10. Dimensional Modeling

The analytical layer will use a star schema.

### Fact tables

**fact_sales**

Grain: one sales transaction line.

**fact_inventory_snapshot**

Grain: one product, store and snapshot date.

**fact_supplier_delivery**

Grain: one purchase order line and its delivery outcome.

### Dimension tables

**dim_date:** Calendar attributes and seasonal classifications.

**dim_product:** Product attributes and category information.

**dim_customer:** Synthetic customer attributes and historical changes.

**dim_store:** Store location and organizational attributes.

**dim_supplier:** Supplier information and historical changes.

Selected dimensions will use Slowly Changing Dimension Type 2.

Surrogate keys and effective date ranges will preserve historical context.

## 11. Orchestration

The preferred orchestration mechanism is Databricks Lakeflow Jobs, subject to workspace availability.

The initial workflow will separate:

1. Historical ingestion.
2. Silver transformation.
3. Data quality validation.
4. Gold modeling.
5. Streaming ingestion.
6. Monitoring and reconciliation.

The design will respect Free Edition concurrency limits.

The first implementation may use sequential tasks to simplify debugging and resource consumption.

## 12. Monitoring and Observability

Every pipeline execution must record:

- Run identifier.
- Pipeline name.
- Start timestamp.
- End timestamp.
- Execution status.
- Input record count.
- Output record count.
- Rejected record count.
- Error information.

Data freshness and processing duration will be measured.

Monitoring datasets will be queryable through Spark SQL and Databricks SQL.

## 13. Testing Strategy

### Local unit tests

Run with pytest.

Test examples:

- Data generation reproducibility.
- Schema validation.
- Business rules.
- Transformation functions.
- Data quality rules.
- Deduplication logic.

### Databricks integration tests

Validate:

- Spark DataFrame transformations.
- Delta table writes.
- Batch ingestion.
- Streaming ingestion.
- Checkpoint recovery.
- Incremental processing.
- Gold table reconciliation.

### Data quality tests

Validate:

- Null constraints.
- Uniqueness.
- Referential integrity.
- Business-rule compliance.
- Record count reconciliation.

## 14. Security and Configuration

Requirements:

- Do not commit credentials or access tokens.
- Keep secrets outside source control.
- Use synthetic customer records.
- Avoid storing real personal information.
- Separate development configuration from code.
- Use Unity Catalog governance where available.

Environment-specific configuration will be maintained separately from business logic.

## 15. Performance and Resource Management

The Free Edition environment requires controlled workloads.

The implementation will:

- Use configurable dataset sizes.
- Start with small representative workloads.
- Avoid unnecessary concurrent jobs.
- Limit streaming batch sizes.
- Prefer efficient DataFrame and SQL operations.
- Measure execution duration and data volume.
- Avoid collecting large datasets to the driver.
- Document performance observations.

No arbitrary performance guarantees will be assumed before benchmarking.

## 16. Repository Integration

The project will maintain a separation between reusable source code, Databricks execution assets, configuration, SQL models and tests.

The planned repository structure will support:

- `data_generator/`
- `src/`
- `config/`
- `notebooks/`
- `pipelines/`
- `sql/`
- `tests/`
- `docs/`

Business logic should remain modular and reusable rather than being duplicated across notebooks.

## 17. Future Portability

The architecture should allow migration to a paid Databricks environment.

Potential future capabilities include:

- Larger serverless or classic compute.
- More advanced continuous streaming.
- Additional orchestration capacity.
- External event brokers such as Kafka.
- More advanced monitoring and governance.
- Production-scale workloads.

These are future extensions, not mandatory dependencies for the initial implementation.

## 18. Technical Acceptance Criteria

The technical architecture is accepted when:

1. Local and Databricks responsibilities are documented.
2. Bronze, Silver and Gold responsibilities are defined.
3. Storage organization is specified.
4. Batch ingestion strategy is defined.
5. Streaming ingestion and recovery strategy is defined.
6. Data quality architecture is specified.
7. Dimensional modeling strategy is documented.
8. Testing and monitoring strategies are defined.
9. Free Edition limitations are reflected in implementation decisions.
10. Workspace-specific capabilities are verified before implementation.

## 19. Official Technical References

- Databricks Free Edition limitations: https://docs.databricks.com/aws/en/getting-started/free-edition-limitations
- Serverless compute limitations: https://docs.databricks.com/aws/en/compute/serverless/limitations
- Auto Loader: https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader
- Auto Loader with Unity Catalog: https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/unity-catalog
- Unity Catalog Volumes: https://docs.databricks.com/aws/en/volumes
- Streaming on serverless compute: https://docs.databricks.com/aws/en/compute/serverless/streaming
