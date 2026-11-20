
import csv
import random
import math
from pathlib import Path
from datetime import datetime, timedelta
from collections import Counter
from faker import Faker

# Settings
random.seed(42)
Faker.seed(42)
fake = Faker("en_IN")

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)

END = datetime.now().replace(microsecond=0)
START = END - timedelta(days=180)

CITIES = [
    "Hyderabad", "Mumbai", "Bengaluru", "Chennai",
    "Delhi", "Pune", "Kolkata", "Jaipur",
    "Ahmedabad", "Kochi", "Lucknow", "Indore"
]

METHODS = ["UPI", "NEFT", "IMPS", "RTGS", "Debit Card", "Credit Card"]
CHANNELS = ["Mobile Banking", "Internet Banking", "POS", "ATM"]

# 1. Generate 100 unique customers
customers = []

for i in range(1, 101):
    cid = f"CUST{i:03d}"

    customers.append({
        "CustomerID": cid,
        "CustomerName": fake.unique.name(),
        "Age": random.randint(21, 70),
        "Occupation": fake.job(),
        "MonthlyIncomeINR": random.randint(25000, 250000),
        "HomeCity": random.choice(CITIES),
        "PreferredPaymentMethod": random.choice(METHODS),
        "PrimaryDeviceID": f"DEV-{cid}-01"
    })

customer_lookup = {c["CustomerID"]: c for c in customers}

# 2. Generate 100 accounts (AccountID = CustomerID)
accounts = []

for c in customers:
    accounts.append({
        "AccountID": c["CustomerID"],
        "CustomerID": c["CustomerID"],
        "AccountType": random.choice(["Savings", "Current"]),
        "AccountBalanceINR": round(random.uniform(10000, 1500000), 2),
        "AccountStatus": "Active"
    })

# 3. Generate normal transactions
def random_time():
    seconds = random.randint(0, int((END - START).total_seconds()))
    return START + timedelta(seconds=seconds)


def failed_attempts():
    return random.choices(
        [0, 1, 2, 3, 4, 5],
        weights=[88, 7, 3, 1.3, 0.5, 0.2]
    )[0]


transactions = []

for i in range(1, 10001):
    c = random.choice(customers)
    cid = c["CustomerID"]
    income = c["MonthlyIncomeINR"]

    amount = random.lognormvariate(math.log(income * 0.02), 0.75)

    # Legitimate expensive purchases
    if random.random() < 0.025:
        amount = income * random.uniform(0.5, 1.4)

    amount = round(min(max(amount, 100), 250000), 2)

    transaction_type = random.choice([
        "Purchase", "Transfer", "Bill Payment",
        "Cash Withdrawal", "Online Purchase"
    ])

    method = (
        c["PreferredPaymentMethod"]
        if random.random() < 0.65
        else random.choice(METHODS)
    )

    channel = random.choice(CHANNELS)

    # Familiar and unfamiliar devices
    device = c["PrimaryDeviceID"]
    is_new_device = 0

    if random.random() < 0.06:
        device = f"DEV-NEW-{random.randint(100000, 999999)}"
        is_new_device = 1
    elif random.random() < 0.12:
        device = f"DEV-{cid}-02"

    # Some legitimate transactions also use new beneficiaries
    beneficiary = ""
    is_new_beneficiary = 0

    if transaction_type == "Transfer":
        is_new_beneficiary = int(random.random() < 0.12)
        beneficiary = (
            f"BEN-NEW-{random.randint(100000, 999999)}"
            if is_new_beneficiary else f"BEN-{cid}-01"
        )

    city = (
        c["HomeCity"]
        if random.random() < 0.82
        else random.choice([x for x in CITIES if x != c["HomeCity"]])
    )

    transactions.append({
        "TransactionID": f"TXN{i:06d}",
        "CustomerID": cid,
        "AccountID": cid,
        "TransactionDate": random_time().strftime("%Y-%m-%d %H:%M:%S"),
        "AmountINR": amount,
        "Currency": "INR",
        "PaymentMethod": method,
        "TransactionType": transaction_type,
        "Channel": channel,
        "MerchantCategory": random.choice([
            "Groceries", "Food", "Shopping", "Travel",
            "Fuel", "Healthcare", "Utilities", "Electronics"
        ]),
        "MerchantName": fake.company(),
        "City": city,
        "Country": "India",
        "DeviceID": device,
        "IsNewDevice": is_new_device,
        "BeneficiaryID": beneficiary,
        "IsNewBeneficiary": is_new_beneficiary,
        "FailedLoginAttempts": failed_attempts(),
        "FailedPaymentAttempts": failed_attempts(),
        "TransactionStatus": "SUCCESS"
    })

# 4. Prepare fraud cases
available = set(range(10000))
fraud_labels = {}


def set_time(row, anchor, minutes):
    row["TransactionDate"] = (
        anchor + timedelta(minutes=minutes)
    ).strftime("%Y-%m-%d %H:%M:%S")


def create_case(customer_id, case_no, case_type, scenario):
    candidates = [
        i for i in available
        if transactions[i]["CustomerID"] == customer_id
    ]

    indexes = random.sample(candidates, 5)
    available.difference_update(indexes)

    # 3 cases in training period, 1 validation, 1 testing
    if case_no <= 3:
        day = random.randint(15, 110)
    elif case_no == 4:
        day = random.randint(132, 142)
    else:
        day = random.randint(160, 168)

    anchor = START + timedelta(
        days=day, hours=random.randint(8, 20)
    )

    c = customer_lookup[customer_id]
    income = c["MonthlyIncomeINR"]

    case_id = f"{case_type}-{case_no:02d}"
    beneficiary = f"BEN-{case_id}"

    # Vary the signals between fraud cases
    new_device = random.random() < 0.60
    unusual_city = random.random() < 0.55
    other_city = random.choice([
        city for city in CITIES if city != c["HomeCity"]
    ])

    for p, index in enumerate(indexes):
        row = transactions[index]

        row["City"] = other_city if unusual_city else c["HomeCity"]

        if new_device:
            row["DeviceID"] = f"DEV-{case_id}"
            row["IsNewDevice"] = 1
        else:
            row["DeviceID"] = c["PrimaryDeviceID"]
            row["IsNewDevice"] = 0

        row["FailedLoginAttempts"] = failed_attempts()
        row["FailedPaymentAttempts"] = failed_attempts()

        if case_type == "ATO":
            # Account takeover
            set_time(row, anchor, [0, 10, 25, 45, 70][p])

            row.update({
                "TransactionType": "Transfer",
                "PaymentMethod": random.choice(["UPI", "IMPS", "NEFT"]),
                "Channel": random.choice(["Mobile Banking", "Internet Banking"]),
                "AmountINR": round(income * random.uniform(0.08, 0.45), 2),
                "BeneficiaryID": beneficiary if random.random() < 0.7
                    else f"BEN-{customer_id}-01",
                "IsNewBeneficiary": 0
            })

            if p == 0 and random.random() < 0.75:
                row["FailedLoginAttempts"] = random.randint(2, 5)

            if p == 0 and row["BeneficiaryID"] == beneficiary:
                row["IsNewBeneficiary"] = 1

        elif case_type == "RAPID":
            # Rapid transfers
            set_time(row, anchor, [0, 2, 5, 8, 11][p])

            new_count = 2 + (case_no % 4)

            row.update({
                "TransactionType": "Transfer",
                "PaymentMethod": random.choice(["UPI", "IMPS"]),
                "Channel": random.choice(["Mobile Banking", "Internet Banking"]),
                "AmountINR": round(income * random.uniform(0.02, 0.15), 2),
                "BeneficiaryID": (
                    f"BEN-{case_id}-{p}"
                    if p < new_count else f"BEN-{customer_id}-01"
                ),
                "IsNewBeneficiary": int(p < new_count)
            })

        elif case_type == "CARD":
            # Card testing
            set_time(row, anchor, [0, 6, 15, 25, 40][p])

            amounts = [
                150, 350, 700, 1500,
                round(income * random.uniform(0.10, 0.30), 2)
            ]

            row.update({
                "TransactionType": "Online Purchase",
                "PaymentMethod": random.choice(["Debit Card", "Credit Card"]),
                "Channel": "Internet Banking",
                "MerchantCategory": "Electronics",
                "AmountINR": amounts[p],
                "BeneficiaryID": "",
                "IsNewBeneficiary": 0
            })

            if p == case_no % 3:
                row["FailedPaymentAttempts"] = random.randint(2, 5)

        elif case_type == "SCAM":
            # Social engineering
            set_time(row, anchor, [0, 180, 1440, 1800, 2880][p])

            amounts = [0.12, 0.10, 0.15, 0.10, 0.12]

            row.update({
                "TransactionType": "Transfer",
                "PaymentMethod": random.choice(["UPI", "NEFT", "IMPS"]),
                "Channel": random.choice(["Mobile Banking", "Internet Banking"]),
                "AmountINR": round(income * amounts[p], 2),
                "BeneficiaryID": beneficiary,
                "IsNewBeneficiary": int(p == 0)
            })

        row["TransactionStatus"] = "SUCCESS"

        fraud_labels[row["TransactionID"]] = {
            "IsFraud": 1,
            "FraudCaseID": case_id,
            "FraudScenario": scenario
        }


# 5. Create 20 incidents across four scenarios
case_customers = random.sample(
    [c["CustomerID"] for c in customers], 20
)

scenarios = [
    ("ATO", "Account takeover after failed login attempts"),
    ("RAPID", "Rapid transfers to multiple beneficiaries"),
    ("CARD", "Card testing after failed payment attempts"),
    ("SCAM", "Social engineering through a new beneficiary")
]

for s, (case_type, scenario) in enumerate(scenarios):
    for case_no in range(1, 6):
        customer_id = case_customers[s * 5 + case_no - 1]
        create_case(customer_id, case_no, case_type, scenario)

# 6. Add legitimate rapid-transfer activity too
normal_customers = [
    c["CustomerID"] for c in customers
    if c["CustomerID"] not in case_customers
]

for customer_id in random.sample(normal_customers, 8):
    indexes = random.sample([
        i for i in available
        if transactions[i]["CustomerID"] == customer_id
    ], 3)

    available.difference_update(indexes)

    anchor = START + timedelta(
        days=random.randint(20, 105), hours=random.randint(8, 20)
    )

    for p, index in enumerate(indexes):
        row = transactions[index]
        set_time(row, anchor, [0, 4, 9][p])

        row.update({
            "TransactionType": "Transfer",
            "PaymentMethod": random.choice(["UPI", "IMPS"]),
            "Channel": "Mobile Banking",
            "AmountINR": round(random.uniform(500, 5000), 2),
            "BeneficiaryID": f"BEN-REGULAR-{customer_id}",
            "IsNewBeneficiary": int(p == 0 and random.random() < 0.5)
        })

# 7. Create answers separately
transactions.sort(key=lambda r: r["TransactionDate"])

answers = []

for row in transactions:
    label = fraud_labels.get(row["TransactionID"], {
        "IsFraud": 0,
        "FraudCaseID": "",
        "FraudScenario": "Legitimate"
    })

    answers.append({
        "TransactionID": row["TransactionID"],
        **label
    })

# 8. Save four CSV files
def save_csv(filename, rows):
    with open(DATA / filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


save_csv("customers.csv", customers)
save_csv("accounts.csv", accounts)
save_csv("transactions.csv", transactions)
save_csv("answers.csv", answers)

# 9. Final counts
scenario_counts = Counter(
    x["FraudScenario"] for x in answers if x["IsFraud"] == 1
)

case_counts = Counter(
    x["FraudCaseID"] for x in answers if x["IsFraud"] == 1
)

assert len(customers) == 100
assert len({c["CustomerName"] for c in customers}) == 100
assert len(accounts) == 100
assert len(transactions) == 10000
assert sum(x["IsFraud"] for x in answers) == 100
assert len(case_counts) == 20
assert all(v == 5 for v in case_counts.values())
assert all(a["AccountID"] == a["CustomerID"] for a in accounts)
assert all(t["AccountID"] == t["CustomerID"] for t in transactions)
assert all(t["Country"] == "India" for t in transactions)

print("\nDATA GENERATION COMPLETED")
print("-------------------------")
print("Customers:", len(customers))
print("Accounts:", len(accounts))
print("Transactions:", len(transactions))
print("Fraud:", sum(x["IsFraud"] for x in answers))
print("Legitimate:", len(answers) - sum(x["IsFraud"] for x in answers))
print("Fraud rate:", "1%")
print("\nFraud scenarios:", dict(scenario_counts))
print("Fraud cases:", len(case_counts))
print("Unique customer names:", len({c["CustomerName"] for c in customers}))
print("Saved in:", DATA)