# Customer Source Manifest

## 1. Purpose

This document describes the synthetic customer source dataset generated for the Customer 360 Data Pipeline project.

The manifest records the dataset composition, generation parameters, intentional data quality scenarios, standardization scenarios, and expected record counts.

Its purpose is to provide a known reference for validating the ingestion, data quality, standardization, deduplication, and transformation stages of the pipeline.

---

## 2. Source Information

| Property       | Value                    |
| -------------- | ------------------------ |
| Source file    | `data/raw/customers.csv` |
| Format         | CSV                      |
| Encoding       | UTF-8                    |
| Delimiter      | Comma (`,`)              |
| Header         | Yes                      |
| Index column   | No                       |
| Total records  | 5,000                    |
| Reference date | `2026-07-31`             |
| Random seed    | `42`                     |

The dataset is fully synthetic and does not contain real customer information.

---

## 3. Schema

The source contains the following columns, in this order:

| Column              | Description                           |
| ------------------- | ------------------------------------- |
| `customer_id`       | Customer identifier                   |
| `full_name`         | Customer full name                    |
| `birth_date`        | Customer birth date                   |
| `email`             | Customer email address                |
| `city`              | Customer city                         |
| `state`             | Brazilian state code                  |
| `registration_date` | Customer registration date            |
| `status`            | Customer account status               |
| `marketing_opt_in`  | Marketing consent indicator           |
| `updated_at`        | Timestamp of the latest record update |

Detailed field definitions and business rules are documented separately in `customer_source_contract.md`.

---

## 4. Dataset Composition

The final source contains 5,000 records.

| Record type                       |     Count |
| --------------------------------- | --------: |
| Base customer records             |     4,800 |
| Newer duplicate versions          |       120 |
| Exact duplicates                  |        30 |
| Records with invalid customer IDs |        50 |
| **Total**                         | **5,000** |

The 4,800 base customers are initially generated as valid records.

Intentional data quality and standardization scenarios are applied only after the base dataset has been generated and validated.

---

## 5. Duplicate Scenarios

### 5.1 Newer Duplicate Versions

**Count:** 120

A second version of an existing customer record is created with:

- the same `customer_id`;
- a different `email`;
- an `updated_at` value later than the original record;
- an `updated_at` value not later than the reference date.

These records simulate multiple versions of the same customer arriving from a source system.

The downstream pipeline is expected to identify the most recent version using `updated_at`.

### 5.2 Exact Duplicates

**Count:** 30

These records are exact copies of existing customer records.

All fields are identical to the corresponding original record.

They are included to test exact duplicate detection and removal.

---

## 6. Intentional Data Quality Scenarios

The following scenarios are injected into selected base customer records.

Scenario selection is mutually exclusive: a customer selected for one scenario is not selected for another scenario controlled by the same scenario-selection process.

| Scenario                 | Count | Description                                              |
| ------------------------ | ----: | -------------------------------------------------------- |
| Future birth date        |    15 | `birth_date` is later than the reference date            |
| Age over 100             |    15 | Customer age is between 101 and 110 years                |
| Future registration date |    20 | `registration_date` is later than the reference date     |
| Invalid status           |    15 | `status` contains a value outside the accepted domain    |
| Missing `updated_at`     |    10 | `updated_at` is null                                     |
| Missing full name        |    35 | `full_name` is null                                      |
| Invalid email            |    45 | Email is populated but intentionally malformed           |
| Missing email            |    25 | `email` is null                                          |
| Unknown state            |    20 | `state` contains a value outside the known state mapping |

---

## 7. Standardization Scenarios

The dataset also contains intentional representation variations.

These records are not conceptually invalid. They simulate source-system inconsistencies that should be normalized by the downstream pipeline.

### 7.1 State Variations

**Count:** 300

Valid Brazilian states are represented using alternative formats instead of their standard two-letter code.

Examples include:

- `SP` → `São Paulo`
- `MG` → `minas gerais`
- `PR` → `paraná`
- `GO` → `Goias`
- `ES` → `Espirito Santo`

The variations intentionally include:

- full state names;
- differences in capitalization;
- accented values;
- unaccented values.

The downstream pipeline is expected to normalize these representations back to the corresponding state code.

### 7.2 Status Variations

**Count:** 250

Valid customer statuses are represented using alternative capitalization.

Examples include:

- `ACTIVE` → `active`
- `INACTIVE` → `Inactive`
- `BLOCKED` → `blocked`

These values preserve the original business meaning and should be normalized to:

- `ACTIVE`
- `INACTIVE`
- `BLOCKED`

They are different from the intentional invalid status scenario, which contains a value outside the accepted status domain.

### 7.3 Marketing Opt-In Variations

**Count:** 200

Boolean marketing consent values are represented using textual alternatives.

Mapping used in the source:

- `True` → `yes`
- `False` → `no`

These values preserve the original consent meaning and should be normalized by the downstream pipeline to boolean values.

---

## 8. Invalid Customer ID Records

An additional 50 records are generated with valid customer attributes but intentionally invalid `customer_id` values.

The purpose is to isolate customer identifier validation from other data quality rules.

| Invalid ID type   |  Count | Example          |
| ----------------- | -----: | ---------------- |
| Empty ID          |     15 | `""`             |
| Numeric-only ID   |     10 | `10000001`       |
| Invalid prefix    |     10 | `CLIENT00000001` |
| Incorrect length  |     10 | `CUST0001`       |
| Invalid character |      5 | `CUST0000001@`   |
| **Total**         | **50** |                  |

Except for `customer_id`, the remaining fields of these records are generated using the same valid generation rules as the base customers.

---

## 9. Valid Customer ID Format

A valid customer identifier follows the pattern:

`CUST` + 8 numeric digits

Example:

`CUST00000001`

Therefore, a valid identifier:

- starts with `CUST`;
- contains exactly 12 characters;
- contains exactly 8 numeric characters after the prefix.

---

## 10. Expected Data Quality Behavior

The synthetic source intentionally contains reject-worthy records, non-blocking quality issues, and standardization scenarios.

### Expected rejection scenarios

The following conditions are intended to be rejected by the downstream validation layer:

- invalid or missing `customer_id`;
- future `birth_date`;
- age greater than 100;
- future `registration_date`;
- invalid `status`;
- missing `updated_at`.

### Expected non-blocking quality issues

The following conditions should be reported as data quality issues but do not necessarily require rejection of the customer record:

- missing `full_name`;
- invalid `email`;
- missing `email`;
- unknown `state`.

### Expected standardization scenarios

The following values should be normalized rather than rejected:

- alternative state representations;
- status capitalization variations;
- textual marketing opt-in representations.

The exact downstream treatment is defined by the pipeline business rules.

---

## 11. Generation and Reproducibility

The dataset is generated programmatically by:

`scripts/generate_customers.py`

The generator uses a fixed random seed:

`SEED = 42`

and a fixed reference date:

`REFERENCE_DATE = 2026-07-31`

Scenario IDs are selected deterministically, and unordered ID collections are explicitly sorted before operations whose execution order affects random value generation.

These controls ensure that the same code, seed, and reference date produce the same source dataset.

### Reproducibility Verification

Reproducibility was verified by running the complete generator twice independently and calculating the SHA-256 hash of the resulting `customers.csv` file after each execution.

Both executions produced:

`63E644BD66A1A8C4FFAEF7C5A589AE4A65066C9A0C4BAB4BEFD4C7D7580CB1C0`

The identical SHA-256 hashes confirm that both generated files were byte-for-byte identical.

The generator also validates the base population and intentional scenarios before writing the final CSV.

---

## 12. Expected Final State

After generation, the following conditions must hold:

- `customers.csv` exists in `data/raw`;
- the file contains exactly 5,000 data records;
- the file contains exactly the expected 10 columns;
- column order matches the source contract;
- no unintended index column is written;
- duplicate scenarios match the documented quantities;
- data quality scenarios match the documented quantities;
- standardization scenarios match the documented quantities;
- repeated executions using the same seed and reference date produce identical output.

This manifest acts as the reference inventory for subsequent ingestion, data quality, standardization, deduplication, and transformation stages.