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

# orchestration
def main():
    customers = generate_base_customers()

    validate_base_customers(customers)

    validate_base_distributions(customers)

    scenario_ids = select_scenario_ids(customers)

    validate_scenario_selection(scenario_ids)

if __name__ == "__main__":
    main()