# Customer Source Manifest

## 1. Purpose

This document describes the synthetic customer source dataset generated for the Customer 360 Data Pipeline project.

The manifest records the dataset composition, generation parameters, intentional data quality scenarios, and expected record counts.

Its purpose is to provide a known reference for validating the ingestion, data quality, deduplication, and transformation stages of the pipeline.

---

## 2. Source Information

| Property | Value |
|---|---|
| Source file | `data/raw/customers.csv` |
| Format | CSV |
| Encoding | UTF-8 |
| Delimiter | Comma (`,`) |
| Header | Yes |
| Index column | No |
| Total records | 5,000 |
| Reference date | `2026-07-31` |
| Random seed | `42` |

The dataset is fully synthetic and does not contain real customer information.

---

## 3. Schema

The source contains the following columns, in this order:

| Column | Description |
|---|---|
| `customer_id` | Customer identifier |
| `full_name` | Customer full name |
| `birth_date` | Customer birth date |
| `email` | Customer email address |
| `city` | Customer city |
| `state` | Brazilian state code |
| `registration_date` | Customer registration date |
| `status` | Customer account status |
| `marketing_opt_in` | Marketing consent indicator |
| `updated_at` | Timestamp of the latest record update |

Detailed field definitions and business rules are documented separately in `customer_source_contract.md`.

---

## 4. Dataset Composition

The final source contains 5,000 records.

| Record type | Count |
|---|---:|
| Base customer records | 4,800 |
| Newer duplicate versions | 120 |
| Exact duplicates | 30 |
| Records with invalid customer IDs | 50 |
| **Total** | **5,000** |

The 4,800 base customers are initially generated as valid records.

Intentional data quality scenarios are applied only after the base dataset has been generated and validated.

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

Scenario selection is mutually exclusive: a customer selected for one of these scenarios is not selected for another scenario in this group.

| Scenario | Count | Description |
|---|---:|---|
| Future birth date | 15 | `birth_date` is later than the reference date |
| Age over 100 | 15 | Customer age is between 101 and 110 years |
| Future registration date | 20 | `registration_date` is later than the reference date |
| Invalid status | 15 | `status` contains a value outside the accepted domain |
| Missing `updated_at` | 10 | `updated_at` is null |
| Missing full name | 35 | `full_name` is null |
| Invalid email | 45 | Email is populated but intentionally malformed |
| Missing email | 25 | `email` is null |
| Unknown state | 20 | `state` contains a value outside the known state mapping |

---

## 7. Invalid Customer ID Records

An additional 50 records are generated with valid customer attributes but intentionally invalid `customer_id` values.

The purpose is to isolate customer identifier validation from other data quality rules.

| Invalid ID type | Count | Example |
|---|---:|---|
| Empty ID | 15 | `""` |
| Numeric-only ID | 10 | `10000001` |
| Invalid prefix | 10 | `CLIENT00000001` |
| Incorrect length | 10 | `CUST0001` |
| Invalid character | 5 | `CUST0000001@` |
| **Total** | **50** | |

Except for `customer_id`, the remaining fields of these records are generated using the same valid generation rules as the base customers.

---

## 8. Valid Customer ID Format

A valid customer identifier follows the pattern:

`CUST` + 8 numeric digits

Example:

`CUST00000001`

Therefore, a valid identifier:

- starts with `CUST`;
- contains exactly 12 characters;
- contains exactly 8 numeric characters after the prefix.

---

## 9. Expected Data Quality Behavior

The synthetic source intentionally contains both reject-worthy records and non-blocking quality issues.

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

The exact downstream treatment is defined by the pipeline business rules.

---

## 10. Generation and Reproducibility

The dataset is generated programmatically by:

`scripts/generate_customers.py`

The generator uses a fixed random seed:

`SEED = 42`

and a fixed reference date:

`REFERENCE_DATE = 2026-07-31`

These parameters are intended to make dataset generation reproducible and allow expected data quality counts to be tested consistently.

The generator validates the base population and intentional scenarios before writing the final CSV.

---

## 11. Expected Final State

After generation, the following conditions must hold:

- `customers.csv` exists in `data/raw`;
- the file contains exactly 5,000 data records;
- the file contains exactly the expected 10 columns;
- column order matches the source contract;
- no unintended index column is written;
- duplicate and data quality scenarios match the quantities documented in this manifest.

This manifest acts as the reference inventory for subsequent ingestion and data quality validation stages.