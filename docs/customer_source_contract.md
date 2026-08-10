# Customer Source Contract

## Source file

`data/raw/customers.csv`

## File format

- Format: CSV
- Encoding: UTF-8
- Delimiter: comma (`,`)
- Header: yes
- Expected columns: 10

## Schema

| Field | Logical Type | Required | Description / Expected Rule |
|---|---|---|---|
| customer_id | string | Yes | `CUST` followed by 8 digits |
| full_name | string | No | Customer full name |
| birth_date | date | Yes | Expected format: `YYYY-MM-DD` |
| email | string | No | Customer email address |
| city | string | No | Customer city |
| state | string | No | State name or abbreviation |
| registration_date | date | Yes | Expected format: `YYYY-MM-DD` |
| status | string | Yes | Customer account status |
| marketing_opt_in | boolean/string | Yes | Marketing communication consent |
| updated_at | datetime | Yes | Last update timestamp |