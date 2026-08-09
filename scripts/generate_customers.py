# imports
import random
from datetime import date, datetime, timedelta
from pathlib import Path
import pandas as pd
from faker import Faker
from collections import Counter

# constants
SEED = 42
TOTAL_CUSTOMERS = 4800
REFERENCE_DATE = date(2026, 7, 31)
CITIES_BY_STATE = {
    "SP": [
        "São Paulo",
        "Campinas",
        "Santos",
        "Sorocaba",
        "Ribeirão Preto",
        "São José dos Campos",
    ],
    "MG": [
        "Belo Horizonte",
        "Uberlândia",
        "Juiz de Fora",
        "Contagem",
        "Uberaba",
        "Montes Claros",
    ],
    "RJ": [
        "Rio de Janeiro",
        "Niterói",
        "Petrópolis",
        "Duque de Caxias",
        "Nova Iguaçu",
        "Volta Redonda",
    ],
    "PR": [
        "Curitiba",
        "Londrina",
        "Maringá",
        "Cascavel",
        "Ponta Grossa",
    ],
    "RS": [
        "Porto Alegre",
        "Caxias do Sul",
        "Pelotas",
        "Canoas",
        "Santa Maria",
    ],
    "BA": [
        "Salvador",
        "Feira de Santana",
        "Vitória da Conquista",
        "Camaçari",
    ],
    "SC": [
        "Florianópolis",
        "Joinville",
        "Blumenau",
        "Chapecó",
        "Itajaí",
    ],
    "PE": [
        "Recife",
        "Olinda",
        "Caruaru",
        "Jaboatão dos Guararapes",
    ],
    "GO": [
        "Goiânia",
        "Aparecida de Goiânia",
        "Anápolis",
    ],
    "CE": [
        "Fortaleza",
        "Caucaia",
        "Juazeiro do Norte",
    ],
    "ES": [
        "Vitória",
        "Vila Velha",
        "Serra",
        "Cariacica",
    ]
}

EXPECTED_FIELDS = {
    "customer_id",
    "full_name",
    "birth_date",
    "email",
    "city",
    "state",
    "registration_date",
    "status",
    "marketing_opt_in",
    "updated_at",
}

NEWER_DUPLICATE_COUNT = 120
EXACT_DUPLICATE_COUNT = 30
FUTURE_BIRTH_DATE_COUNT = 15
AGE_OVER_100_COUNT = 15
FUTURE_REGISTRATION_DATE_COUNT = 20
INVALID_STATUS_COUNT = 15
MISSING_UPDATED_AT_COUNT = 10
MISSING_NAME_COUNT = 35
INVALID_EMAIL_COUNT = 45
MISSING_EMAIL_COUNT = 25
UNKNOWN_STATE_COUNT = 20

INVALID_CUSTOMER_ID_COUNT = 50
EMPTY_ID_COUNT = 15
NUMERIC_ID_COUNT = 10
CLIENT_PREFIX_ID_COUNT = 10
WRONG_LENGTH_ID_COUNT = 10
INVALID_CHAR_ID_COUNT = 5

# Faker / random configuration
fake = Faker("pt_BR")

random.seed(SEED)
Faker.seed(SEED)

# customer generation
def generate_age():
    age_group = random.choices(
    population=["16_17", "18_24", "25_34", "35_44", "45_54", "55_64", "65_plus"],
    weights=[2, 12, 25, 25, 18, 12, 6],
    k=1)[0]

    if age_group == "16_17":
        age = random.randint(16, 17)
    elif age_group == "18_24":
        age = random.randint(18, 24)
    elif age_group == "25_34":
        age = random.randint(25, 34)
    elif age_group == "35_44":
        age = random.randint(35, 44)
    elif age_group == "45_54":
        age = random.randint(45, 54)
    elif age_group == "55_64":
        age = random.randint(55, 64)
    elif age_group == "65_plus":
        age = random.randint(65, 90)

    return age

def generate_birth_date(age):
    latest_birth_date = date(
        REFERENCE_DATE.year - age,
        REFERENCE_DATE.month,
        REFERENCE_DATE.day,
    )

    earliest_birth_date = date(
        REFERENCE_DATE.year - age - 1,
        REFERENCE_DATE.month,
        REFERENCE_DATE.day,
    ) + timedelta(days=1)

    days_between = (latest_birth_date - earliest_birth_date).days

    birth_date = earliest_birth_date + timedelta(
        days=random.randint(0, days_between)
    )

    return birth_date

def generate_location():
    state = random.choices(
    population=["SP", "MG", "RJ", "PR", "RS", "BA", "SC", "PE", "GO", "CE", "ES"],
    weights=[35, 20, 15, 8, 7, 5, 5, 2, 1, 1, 1],
    k=1)[0]

    city = random.choice(CITIES_BY_STATE[state])

    return city, state

def generate_registration_date():
    start_date = date(2018, 1, 1)

    days_between = (REFERENCE_DATE - start_date).days

    registration_date = start_date + timedelta(
        days=random.randint(0, days_between)
    )

    return registration_date

def generate_updated_at(registration_date):
    start_datetime = datetime.combine(
        registration_date,
        datetime.min.time()
    )

    end_datetime = datetime.combine(
        REFERENCE_DATE,
        datetime.max.time()
    )

    seconds_between = int(
        (end_datetime - start_datetime).total_seconds()
    )

    random_seconds = random.randint(0, seconds_between)

    updated_at = start_datetime + timedelta(
        seconds=random_seconds
    )

    return updated_at

def generate_base_customer(customer_number):
    customer_id = f"CUST{customer_number:08d}"

    age = generate_age()

    city, state = generate_location()

    registration_date = generate_registration_date()

    status = random.choices(
        population=["ACTIVE", "INACTIVE", "BLOCKED"],
        weights=[80, 15, 5],
        k=1
    )[0]

    marketing_opt_in = random.choices(
        population=[True, False], 
        weights=[70, 30],
        k=1)[0]

    customer = {
        "customer_id": customer_id,
        "full_name": fake.name(),
        "birth_date": generate_birth_date(age),
        "email": fake.email(),
        "city": city,
        "state": state,
        "registration_date": registration_date,
        "status": status,
        "marketing_opt_in": marketing_opt_in,
        "updated_at": generate_updated_at(registration_date),
    }

    return customer

def generate_base_customers():
    customers = []

    for i in range(1, TOTAL_CUSTOMERS + 1):
        customer = generate_base_customer(i)
        customers.append(customer)

    return customers

# error customer generation
def create_newer_duplicates(customers, duplicate_ids):
    customers_by_id = {
        customer["customer_id"]: customer
        for customer in customers
    }

    duplicates = []

    for customer_id in duplicate_ids:
        original = customers_by_id[customer_id]

        duplicate = original.copy()

        new_email = fake.email()

        while new_email == original["email"]:
            new_email = fake.email()

        duplicate["email"] = new_email

        reference_end = datetime.combine(
            REFERENCE_DATE,
            datetime.max.time()
        ).replace(microsecond=0)

        seconds_available = int((reference_end - original["updated_at"]).total_seconds())

        duplicate["updated_at"] = (
            original["updated_at"]
            + timedelta(
                seconds=random.randint(1, seconds_available)
            )
        )

        duplicates.append(duplicate)

    return duplicates

def create_exact_duplicates(customers, duplicate_ids):
    customers_by_id = {
        customer["customer_id"]: customer
        for customer in customers
    }

    duplicates = []

    for customer_id in duplicate_ids:
            original = customers_by_id[customer_id]
    
            duplicate = original.copy()

            duplicates.append(duplicate)

    return duplicates

def inject_future_birth_dates(customers, customer_ids):
    for customer in customers:
        if customer["customer_id"] in customer_ids:
            customer["birth_date"] = REFERENCE_DATE + timedelta(days=random.randint(1, 365))

    return customers

def inject_age_over_100(customers, customer_ids):
    for customer in customers:
        if customer["customer_id"] in customer_ids:
            age = random.randint(101, 110)
            customer["birth_date"] = generate_birth_date(age)

    return customers

def inject_future_registration_dates(customers, customer_ids):
    for customer in customers:
        if customer["customer_id"] in customer_ids:
            customer["registration_date"] = REFERENCE_DATE + timedelta(days=random.randint(1, 365))

    return customers

def inject_invalid_status(customers, customer_ids):
    for customer in customers:
        if customer["customer_id"] in customer_ids:
            customer["status"] = "UNKNOWN"

    return customers

def inject_missing_updated_at(customers, customer_ids):
    for customer in customers:
        if customer["customer_id"] in customer_ids:
            customer["updated_at"] = None

    return customers

def inject_missing_names(customers, customer_ids):
    for customer in customers:
        if customer["customer_id"] in customer_ids:
            customer["full_name"] = None

    return customers

def inject_invalid_emails(customers, customer_ids):
    for customer in customers:
        if customer["customer_id"] in customer_ids:
            customer["email"] = customer["email"].split("@")[0] 

    return customers


def inject_missing_emails(customers, customer_ids):
    for customer in customers:
        if customer["customer_id"] in customer_ids:
            customer["email"] = None

    return customers

def inject_unknown_states(customers, customer_ids):
    for customer in customers:
        if customer["customer_id"] in customer_ids:
            customer["state"] = "XX"

    return customers

def create_invalid_customer_id_records():
    invalid_customer_records = []

    for i in range(1, EMPTY_ID_COUNT + 1):
        customer = generate_base_customer(i)
        customer["customer_id"] = ""
        invalid_customer_records.append(customer)

    for i in range(1, NUMERIC_ID_COUNT + 1):
        customer = generate_base_customer(i)
        customer["customer_id"] = str(10000000 + i)
        invalid_customer_records.append(customer)

    for i in range(1, CLIENT_PREFIX_ID_COUNT + 1):
        customer = generate_base_customer(i)
        customer["customer_id"] = customer["customer_id"].replace("CUST", "CLIENT")
        invalid_customer_records.append(customer)

    for i in range(1, WRONG_LENGTH_ID_COUNT + 1):
        customer = generate_base_customer(i)
        customer["customer_id"] = f"CUST{i:04d}"
        invalid_customer_records.append(customer)

    for i in range(1, INVALID_CHAR_ID_COUNT + 1):
        customer = generate_base_customer(i)
        customer["customer_id"] = f"CUST{i:07d}@"
        invalid_customer_records.append(customer)

    return invalid_customer_records

# final dataset generation
def build_final_customer_dataset(customers, newer_duplicates, exact_duplicates, invalid_customer_records):
    final_customers = customers + newer_duplicates + exact_duplicates + invalid_customer_records

    return final_customers
   
# ids selection
def select_ids(available_ids, count):
    selected_ids = set(
        random.sample(available_ids, count)
    )

    remaining_ids = [
        customer_id
        for customer_id in available_ids
        if customer_id not in selected_ids
    ]

    return selected_ids, remaining_ids

# scenario selection
def select_scenario_ids(customers):
    available_ids = [
        customer["customer_id"]
        for customer in customers
    ]

    newer_duplicate_ids, available_ids = select_ids(
        available_ids,
        NEWER_DUPLICATE_COUNT
    )

    exact_duplicate_ids, available_ids = select_ids(
        available_ids,
        EXACT_DUPLICATE_COUNT
    )

    future_birth_date_ids, available_ids = select_ids(
        available_ids,
        FUTURE_BIRTH_DATE_COUNT
    )

    age_over_100_ids, available_ids = select_ids(
        available_ids,
        AGE_OVER_100_COUNT
    )

    future_registration_date_ids, available_ids = select_ids(
        available_ids,
        FUTURE_REGISTRATION_DATE_COUNT
    )

    invalid_status_ids, available_ids = select_ids(
        available_ids,
        INVALID_STATUS_COUNT
    )

    missing_updated_at_ids, available_ids = select_ids(
        available_ids,
        MISSING_UPDATED_AT_COUNT
    )

    missing_name_ids, available_ids = select_ids(
        available_ids,
        MISSING_NAME_COUNT
    )

    invalid_email_ids, available_ids = select_ids(
        available_ids,
        INVALID_EMAIL_COUNT
    )

    missing_email_ids, available_ids = select_ids(
        available_ids,
        MISSING_EMAIL_COUNT
    )

    unknown_state_ids, available_ids = select_ids(
        available_ids,
        UNKNOWN_STATE_COUNT
    )

    return {
        "newer_duplicates": newer_duplicate_ids,
        "exact_duplicates": exact_duplicate_ids,
        "future_birth_date": future_birth_date_ids,
        "age_over_100": age_over_100_ids,
        "future_registration_date": future_registration_date_ids,
        "invalid_status": invalid_status_ids,
        "missing_updated_at": missing_updated_at_ids,
        "missing_name": missing_name_ids,
        "invalid_email": invalid_email_ids,
        "missing_email": missing_email_ids,
        "unknown_state": unknown_state_ids,
    }

# validation helpers
def calculate_age(birth_date):
    age = REFERENCE_DATE.year - birth_date.year

    birthday_has_not_occurred = (
        REFERENCE_DATE.month,
        REFERENCE_DATE.day,
    ) < (
        birth_date.month,
        birth_date.day,
    )

    if birthday_has_not_occurred:
        age -= 1

    return age

def get_age_group(age):
    if 16 <= age <= 17:
        return "16_17"
    elif 18 <= age <= 24:
        return "18_24"
    elif 25 <= age <= 34:
        return "25_34"
    elif 35 <= age <= 44:
        return "35_44"
    elif 45 <= age <= 54:
        return "45_54"
    elif 55 <= age <= 64:
        return "55_64"
    elif 65 <= age <= 90:
        return "65_plus"

    return "OUT_OF_RANGE"

def validate_percentage(counts, category, total, expected_percentage, tolerance):
    actual_percentage = counts[category] / total

    minimum = expected_percentage - tolerance
    maximum = expected_percentage + tolerance

    assert minimum <= actual_percentage <= maximum, (
        f"{category}: expected {expected_percentage:.2%} "
        f"± {tolerance:.2%}, got {actual_percentage:.2%}"
    )

# validations
def validate_base_customers(customers):
    assert len(customers) == TOTAL_CUSTOMERS

    customer_ids = [
        customer["customer_id"]
        for customer in customers
    ]

    assert len(set(customer_ids)) == TOTAL_CUSTOMERS

    assert all(
        set(customer.keys()) == EXPECTED_FIELDS
        for customer in customers
    )

    assert all(
        customer["customer_id"] is not None and customer["customer_id"] != ""
        for customer in customers
    )

    assert all(
        customer["birth_date"] is not None for customer in customers
    )

    assert all(
        customer["registration_date"] is not None for customer in customers
    )

    assert all(
        customer["status"] is not None and customer["status"] != ""
        for customer in customers
    )

    assert all(
        customer["updated_at"] is not None for customer in customers
    )

    assert all(
        customer["customer_id"].startswith("CUST")
        and len(customer["customer_id"]) == 12
        and customer["customer_id"][4:].isdigit()
        for customer in customers
    )

    assert all(
        customer["birth_date"] <= REFERENCE_DATE
        and 16 <= calculate_age(customer["birth_date"]) <= 90
        for customer in customers
    )

    assert all(
        date(2018, 1, 1) <= customer["registration_date"] <= REFERENCE_DATE
        for customer in customers
    )

    assert all(
        customer["registration_date"]
        <= customer["updated_at"].date()
        <= REFERENCE_DATE
        for customer in customers
    )

    assert all(
        customer["status"] in {"ACTIVE", "INACTIVE", "BLOCKED"}
        for customer in customers
    )

    assert all(
        isinstance(customer["marketing_opt_in"], bool)
        for customer in customers
    )

    assert all(
        customer["state"] in CITIES_BY_STATE
        and customer["city"] in CITIES_BY_STATE[customer["state"]]
        for customer in customers
    )

def validate_base_distributions(customers):
    total = len(customers)

    age_counts = Counter(get_age_group(calculate_age(customer["birth_date"])) for customer in customers)

    location_counts = Counter(customer["state"] for customer in customers)

    status_counts = Counter(customer["status"] for customer in customers)

    marketing_opt_in_counts = Counter(customer["marketing_opt_in"] for customer in customers)

    # age
    validate_percentage(
        age_counts,
        "16_17",
        total,
        expected_percentage=0.02,
        tolerance=0.01,
    )

    validate_percentage(
        age_counts,
        "18_24",
        total,
        expected_percentage=0.12,
        tolerance=0.03,
    )

    validate_percentage(
        age_counts,
        "25_34",
        total,
        expected_percentage=0.25,
        tolerance=0.03,
    )

    validate_percentage(
        age_counts,
        "35_44",
        total,
        expected_percentage=0.25,
        tolerance=0.03,
    )

    validate_percentage(
        age_counts,
        "45_54",
        total,
        expected_percentage=0.18,
        tolerance=0.03,
    )

    validate_percentage(
        age_counts,
        "55_64",
        total,
        expected_percentage=0.12,
        tolerance=0.03,
    )

    validate_percentage(
        age_counts,
        "65_plus",
        total,
        expected_percentage=0.06,
        tolerance=0.02,
    )

    # location
    validate_percentage(
        location_counts,
        "SP",
        total,
        expected_percentage=0.35,
        tolerance=0.05,
    ) 

    validate_percentage(
        location_counts,
        "MG",
        total,
        expected_percentage=0.20,
        tolerance=0.05,
    )

    validate_percentage(
        location_counts,
        "RJ",
        total,
        expected_percentage=0.15,
        tolerance=0.05,
    ) 

    validate_percentage(
        location_counts,
        "PR",
        total,
        expected_percentage=0.08,
        tolerance=0.03,
    )

    validate_percentage(
        location_counts,
        "RS",
        total,
        expected_percentage=0.07,
        tolerance=0.03,
    )

    validate_percentage(
        location_counts,
        "BA",
        total,
        expected_percentage=0.05,
        tolerance=0.02,
    )

    validate_percentage(
        location_counts,
        "SC",
        total,
        expected_percentage=0.05,
        tolerance=0.02,
    )

    validate_percentage(
        location_counts,
        "PE",
        total,
        expected_percentage=0.02,
        tolerance=0.01,
    )

    validate_percentage(
        location_counts,
        "GO",
        total,
        expected_percentage=0.01,
        tolerance=0.01,
    )

    validate_percentage(
        location_counts,
        "CE",
        total,
        expected_percentage=0.01,
        tolerance=0.01,
    )

    validate_percentage(
        location_counts,
        "ES",
        total,
        expected_percentage=0.01,
        tolerance=0.01,
    )

    # status
    validate_percentage(
        status_counts,
        "ACTIVE",
        total,
        expected_percentage=0.80,
        tolerance=0.05,
    )

    validate_percentage(
        status_counts,
        "INACTIVE",
        total,
        expected_percentage=0.15,
        tolerance=0.05,
    )

    validate_percentage(
        status_counts,
        "BLOCKED",
        total,
        expected_percentage=0.05,
        tolerance=0.02,
    )

    # marketing_opt_in
    validate_percentage(
        marketing_opt_in_counts,
        True,
        total,
        expected_percentage=0.70,
        tolerance=0.05,
    )

    validate_percentage(
        marketing_opt_in_counts,
        False,
        total,
        expected_percentage=0.30,
        tolerance=0.05,
    )

def validate_scenario_selection(scenario_ids):
    expected_counts = {
        "newer_duplicates": NEWER_DUPLICATE_COUNT,
        "exact_duplicates": EXACT_DUPLICATE_COUNT,
        "future_birth_date": FUTURE_BIRTH_DATE_COUNT,
        "age_over_100": AGE_OVER_100_COUNT,
        "future_registration_date": FUTURE_REGISTRATION_DATE_COUNT,
        "invalid_status": INVALID_STATUS_COUNT,
        "missing_updated_at": MISSING_UPDATED_AT_COUNT,
        "missing_name": MISSING_NAME_COUNT,
        "invalid_email": INVALID_EMAIL_COUNT,
        "missing_email": MISSING_EMAIL_COUNT,
        "unknown_state": UNKNOWN_STATE_COUNT,
    }

    for scenario, expected_count in expected_counts.items():
        assert len(scenario_ids[scenario]) == expected_count, (
            f"{scenario}: expected {expected_count} IDs, "
            f"got {len(scenario_ids[scenario])}"
        )

    all_selected_ids = [
    customer_id
    for ids in scenario_ids.values()
    for customer_id in ids
    ]

    assert len(all_selected_ids) == len(set(all_selected_ids)), (
        "Scenario IDs overlap"
    )

# errors validation
def validate_newer_duplicates(customers, duplicates, duplicate_ids):
    duplicate_customer_ids = {
        duplicate["customer_id"]
        for duplicate in duplicates
    }

    customer_ids = {
        customer["customer_id"]
        for customer in customers
    }

    customers_by_id = {
    customer["customer_id"]: customer
    for customer in customers
    }

    assert len(duplicates) == NEWER_DUPLICATE_COUNT

    assert duplicate_customer_ids == set(duplicate_ids)

    assert duplicate_customer_ids.issubset(customer_ids)

    assert all(
        duplicate["email"] != customers_by_id[duplicate["customer_id"]]["email"]
        for duplicate in duplicates
    )

    assert all(
        duplicate["updated_at"] > customers_by_id[duplicate["customer_id"]]["updated_at"]
        for duplicate in duplicates
    )

    assert all(
        duplicate["updated_at"].date() <= REFERENCE_DATE
        for duplicate in duplicates
    )

def validate_exact_duplicates(customers, duplicates, duplicate_ids):
    duplicate_customer_ids = {
        duplicate["customer_id"]
        for duplicate in duplicates
    }

    customers_by_id = {
        customer["customer_id"]: customer
        for customer in customers
    }

    assert len(duplicates) == EXACT_DUPLICATE_COUNT

    assert duplicate_customer_ids == set(duplicate_ids)

    assert all(
        duplicate == customers_by_id[duplicate["customer_id"]]
        for duplicate in duplicates
    )

def validate_future_birth_dates(customers, customer_ids):
    future_birth_date_customer_ids = {
        customer["customer_id"]
        for customer in customers
        if customer["birth_date"] > REFERENCE_DATE
    }

    assert len(future_birth_date_customer_ids) == FUTURE_BIRTH_DATE_COUNT

    assert future_birth_date_customer_ids == set(customer_ids)

def validate_age_over_100(customers, customer_ids):
    age_over_100_customer_ids = {
        customer["customer_id"]
        for customer in customers
        if calculate_age(customer["birth_date"]) > 100
    }

    assert len(age_over_100_customer_ids) == AGE_OVER_100_COUNT

    assert age_over_100_customer_ids == set(customer_ids)

def validate_future_registration_dates(customers, customer_ids):
    future_registration_date_customer_ids = {
        customer["customer_id"]
        for customer in customers
        if customer["registration_date"] > REFERENCE_DATE
    }

    assert len(future_registration_date_customer_ids) == FUTURE_REGISTRATION_DATE_COUNT

    assert future_registration_date_customer_ids == set(customer_ids)

def validate_invalid_status(customers, customer_ids):
    invalid_status_customer_ids = {
        customer["customer_id"]
        for customer in customers
        if customer["status"] not in {"ACTIVE", "INACTIVE", "BLOCKED"}
    }

    assert len(invalid_status_customer_ids) == INVALID_STATUS_COUNT

    assert invalid_status_customer_ids == set(customer_ids)

def validate_missing_updated_at(customers, customer_ids):
    missing_updated_at_customer_ids = {
        customer["customer_id"]
        for customer in customers
        if customer["updated_at"] is None
    }

    assert len(missing_updated_at_customer_ids) == MISSING_UPDATED_AT_COUNT

    assert missing_updated_at_customer_ids == set(customer_ids)

def validate_missing_names(customers, customer_ids):
    missing_name_customer_ids = {
        customer["customer_id"]
        for customer in customers
        if customer["full_name"] is None
    }

    assert len(missing_name_customer_ids) == MISSING_NAME_COUNT

    assert missing_name_customer_ids == set(customer_ids)

def validate_invalid_emails(customers, customer_ids):
    invalid_email_customer_ids = {
        customer["customer_id"]
        for customer in customers
        if customer["email"] is not None and "@" not in customer["email"]
    }

    assert len(invalid_email_customer_ids) == INVALID_EMAIL_COUNT

    assert invalid_email_customer_ids == set(customer_ids)

def validate_missing_emails(customers, customer_ids):
    missing_email_customer_ids = {
        customer["customer_id"]
        for customer in customers
        if customer["email"] is None
    }

    assert len(missing_email_customer_ids) == MISSING_EMAIL_COUNT

    assert missing_email_customer_ids == set(customer_ids)

def validate_unknown_state(customers, customer_ids):
    unknown_state_customer_ids = {
        customer["customer_id"]
        for customer in customers
        if customer["state"] not in CITIES_BY_STATE
    }

    assert len(unknown_state_customer_ids) == UNKNOWN_STATE_COUNT

    assert unknown_state_customer_ids == set(customer_ids)

def validate_invalid_customer_id_records(invalid_customer_records):
    empty_count = sum(1 for customer in invalid_customer_records if customer["customer_id"] == "")

    numeric_count = sum(1 for customer in invalid_customer_records if customer["customer_id"].isdigit())

    client_prefix_count = sum(1 for customer in invalid_customer_records if customer["customer_id"].startswith("CLIENT"))

    wrong_length_count = sum(1 for customer in invalid_customer_records if customer["customer_id"].startswith("CUST") and len(customer["customer_id"]) != 12)

    invalid_char_count = sum(1 for customer in invalid_customer_records if customer["customer_id"].startswith("CUST")
        and len(customer["customer_id"]) == 12
        and not customer["customer_id"][4:].isdigit()
    )

    assert len(invalid_customer_records) == INVALID_CUSTOMER_ID_COUNT

    assert empty_count == EMPTY_ID_COUNT, (f"Expected {EMPTY_ID_COUNT} empty IDs, got {empty_count}")

    assert numeric_count == NUMERIC_ID_COUNT, (f"Expected {NUMERIC_ID_COUNT} numeric IDs, got {numeric_count}")

    assert client_prefix_count == CLIENT_PREFIX_ID_COUNT, (f"Expected {CLIENT_PREFIX_ID_COUNT} CLIENT IDs, got {client_prefix_count}")

    assert wrong_length_count == WRONG_LENGTH_ID_COUNT, (f"Expected {WRONG_LENGTH_ID_COUNT} wrong length IDs, got {wrong_length_count}")

    assert invalid_char_count == INVALID_CHAR_ID_COUNT, (f"Expected {INVALID_CHAR_ID_COUNT} invalid character IDs, got {invalid_char_count}")

def validate_final_dataset(final_customers):
    assert len(final_customers) == TOTAL_CUSTOMERS + NEWER_DUPLICATE_COUNT + EXACT_DUPLICATE_COUNT + INVALID_CUSTOMER_ID_COUNT

# orchestration
def main():
    customers = generate_base_customers()

    validate_base_customers(customers)

    validate_base_distributions(customers)

    scenario_ids = select_scenario_ids(customers)

    validate_scenario_selection(scenario_ids)

    newer_duplicates = create_newer_duplicates(customers, scenario_ids["newer_duplicates"])

    validate_newer_duplicates(customers, newer_duplicates, scenario_ids["newer_duplicates"])

    exact_duplicates = create_exact_duplicates(customers, scenario_ids["exact_duplicates"])

    validate_exact_duplicates(customers, exact_duplicates, scenario_ids["exact_duplicates"])

    customers = inject_future_birth_dates(customers, scenario_ids["future_birth_date"])

    validate_future_birth_dates(customers, scenario_ids["future_birth_date"])

    customers = inject_age_over_100(customers, scenario_ids["age_over_100"])

    validate_age_over_100(customers, scenario_ids["age_over_100"])

    customers = inject_future_registration_dates(customers, scenario_ids["future_registration_date"])

    validate_future_registration_dates(customers, scenario_ids["future_registration_date"])

    customers = inject_invalid_status(customers, scenario_ids["invalid_status"])

    validate_invalid_status(customers, scenario_ids["invalid_status"])

    customers = inject_missing_updated_at(customers, scenario_ids["missing_updated_at"])

    validate_missing_updated_at(customers, scenario_ids["missing_updated_at"])

    customers = inject_missing_names(customers, scenario_ids["missing_name"])

    validate_missing_names(customers, scenario_ids["missing_name"])

    customers = inject_invalid_emails(customers, scenario_ids["invalid_email"])

    validate_invalid_emails(customers, scenario_ids["invalid_email"])

    customers = inject_missing_emails(customers, scenario_ids["missing_email"])

    validate_missing_emails(customers, scenario_ids["missing_email"])

    customers = inject_unknown_states(customers, scenario_ids["unknown_state"])

    validate_unknown_state(customers, scenario_ids["unknown_state"])

    invalid_customer_records = create_invalid_customer_id_records()

    validate_invalid_customer_id_records(invalid_customer_records)

    final_customers = build_final_customer_dataset(customers, newer_duplicates, exact_duplicates, invalid_customer_records)

    validate_final_dataset(final_customers)

if __name__ == "__main__":
    main()