# Banking Fraud Investigation Platform

A human-in-the-loop platform that helps bank investigators analyze suspicious customer activity, review evidence, and generate investigation reports. Built on synthetic banking data.

Most fraud systems stop at a fraud score. This project goes further: it combines multiple fraud signals into one customer-centric case and uses an LLM to write the investigation summary, while the investigator keeps every final decision.

All modules share the same `CustomerID` and `AccountID`, so one customer can be investigated across every fraud scenario in a single workflow.

## Use Cases

### 1. Transaction Fraud Detection
- **Problem:** Fraudulent transactions cause financial loss, and manual review is not possible at high volume.
- **Solution:** A Random Forest model predicts the fraud probability of each transaction. SHAP explains why it was flagged.
- **Tech:** Random Forest, SHAP
- **Labels:** the raw data has none, so training labels are built from the answer key (about 44 known fraud transactions); the answer key is never a feature
- **Features:** amount, transaction type, transaction time, receiver activity, velocity features
- **Output:** `TX001 → Fraud Probability 0.87` with reasons such as high amount, frequent transfers, high receiver activity

### 2. Account Takeover Detection
- **Problem:** Fraudsters may access accounts using stolen credentials or compromised devices.
- **Solution:** Isolation Forest detects unusual login behavior.
- **Tech:** Isolation Forest
- **Features:** device ID, IP address, location, failed login attempts, login time
- **Output:** `ACC100 → New Device, New Location, Multiple Failed Login Attempts`

### 3. Transaction Pattern Analysis
- **Problem:** Fraud often shows up as an unusual pattern over time, not a single transaction.
- **Solution:** Build behavior features that describe how a customer transacts.
- **Tech:** Pandas
- **Features:** transactions last hour, transactions last day, unique recipients, average transfer amount, transaction frequency
- **Output:** Customer activity summary such as high transfer frequency, multiple recipients, short transaction intervals

### 4. Relationship Investigation
- **Problem:** Investigators need to see how a customer's accounts connect to other accounts.
- **Solution:** Build an account network from transaction history.
- **Tech:** NetworkX
- **Features:** fan-in, fan-out, transaction count, connected accounts, relationship depth
- **Output:** Fund movement paths such as `ACC100 → ACC250 → ACC390`

### 5. AI Investigation Reporting
- **Problem:** Investigators spend a lot of time collecting results from multiple systems and writing reports.
- **Solution:** LangChain gathers evidence from the four modules above and sends it to GPT, which writes a structured investigation report.
- **Tech:** LangChain, OpenAI GPT API
- **LangChain tools:** Fraud Analysis, Account Takeover, Transaction Pattern, Relationship Analysis, Customer Case
- **Output:** A plain-language investigation report. GPT summarizes evidence only and does not make fraud decisions.

**Example request:** `Investigate Customer CUST001`

**Example report:**

```
Investigation Summary
Customer ID: CUST001

- Transaction analysis identified multiple high-risk transactions.
- Login activity indicates access from a previously unseen device.
- Transfers occurred unusually frequently within a short period.
- Relationship analysis identified multiple connected accounts.

Overall Assessment: Multiple risk indicators identified.
Further investigation is recommended.
```

## Folder Structure

Each use case has its own folder, so it is easy to see where everything lives.

```
fraud-investigation/
├── README.md
├── requirements.txt
├── .env.example                  # OPENAI_API_KEY
├── .gitignore
│
├── data/
│   ├── raw/                      # customers, accounts, transactions, login_activity (.csv)
│   ├── answer_key/               # hidden fraud scenarios, for checking only
│   └── processed/                # feature tables built from raw/
│
├── saved_models/                 # trained models (.pkl), gitignored
│
├── src/
│   ├── common/
│   │   ├── paths.py              # project paths
│   │   ├── data_loader.py        # loads the CSVs
│   │   └── check_data.py         # data sanity check
│   │
│   ├── data_generation/
│   │   └── generate_data.py      # customers, accounts, transactions, logins
│   │
│   ├── fraud_detection/          # Use case 1
│   │   ├── train.py              # Random Forest training
│   │   ├── predict.py            # fraud probability
│   │   └── explain.py            # SHAP explanations
│   │
│   ├── account_takeover/         # Use case 2
│   │   ├── train.py              # Isolation Forest training
│   │   └── predict.py            # risky login indicators
│   │
│   ├── pattern_analysis/         # Use case 3
│   │   └── features.py           # velocity + frequency features
│   │
│   ├── relationship_analysis/    # Use case 4
│   │   └── graph.py              # NetworkX account network
│   │
│   ├── investigation_report/     # Use case 5
│   │   ├── tools.py              # LangChain tools (one per module above)
│   │   └── report_generator.py   # evidence -> GPT -> report
│   │
│   └── database/
│       ├── db.py                 # SQLite setup
│       └── cases.py              # cases + evidence
│
├── api/                          # FastAPI backend
│   ├── main.py                   # creates the app, loads models at startup
│   ├── schemas.py                # request/response formats (Pydantic)
│   └── routes/
│       ├── fraud.py              # use case 1 endpoints
│       ├── account.py            # use case 2 endpoints
│       ├── patterns.py           # use case 3 endpoints
│       ├── relationships.py      # use case 4 endpoints
│       └── investigation.py      # use case 5 endpoints
│
├── dashboard/
│   └── app.py                    # Streamlit UI
│
└── notebooks/
    └── eda.ipynb
```

## Data Model

**Customer:** `CustomerID`, `CustomerName`, `Age`, `City`

**Account:** `AccountID`, `CustomerID`, `AccountType`, `CurrentBalance`

**Transaction:** `TransactionID`, `CustomerID`, `SenderAccount`, `ReceiverAccount`, `Amount`, `Timestamp`, `TransactionType`

**Login Activity:** `LoginID`, `CustomerID`, `AccountID`, `DeviceID`, `IPAddress`, `Location`, `Timestamp`, `FailedAttempts`

The raw data has no fraud label and no risk column. Fraud has to be found from patterns in the data. The generator also writes a separate answer key (`data/answer_key/answer_key.csv`) listing the hidden fraud scenarios, used only to check results and to build training labels for the Random Forest. It is never used as a model feature.

## Human Oversight

The platform identifies risks, collects evidence, explains findings, and generates reports.

It does **not** freeze accounts, block transactions, label customers as fraudsters, or make final fraud decisions. Every decision stays with the investigator.

## Dashboard

- **Customer Search** by Customer ID or Account ID
- **Fraud Analysis** with fraud probability and SHAP explanations
- **Account Activity** with takeover indicators
- **Relationship View** with transaction networks and connected accounts
- **Investigation Report** with the generated summary

## Tech Stack

- **Data:** Python, Pandas, NumPy, Faker
- **ML:** Random Forest, Isolation Forest (Scikit-Learn)
- **Explainability:** SHAP
- **Graph:** NetworkX
- **LLM:** LangChain, OpenAI GPT API
- **Backend:** FastAPI
- **Database:** SQLite
- **Frontend:** Streamlit

## Roadmap

- [ ] Synthetic data generator
- [ ] Use case 1: Random Forest fraud model with SHAP
- [ ] Use case 2: Isolation Forest takeover model
- [ ] Use case 3: Transaction pattern features
- [ ] Use case 4: NetworkX relationship graph
- [ ] Use case 5: LangChain + GPT report generation
- [ ] SQLite storage and case management
- [ ] FastAPI endpoints
- [ ] Streamlit dashboard

## Disclaimer

This project uses synthetic data only. It is a portfolio project and is not intended for real-world financial decisions.
