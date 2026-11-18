# Banking Fraud Investigation Platform

A human-in-the-loop platform that helps bank investigators analyze suspicious customer activity, review evidence, and generate investigation reports. Built on **synthetic** banking data.

Most fraud systems stop at a fraud score. This project combines multiple fraud signals into one customer case and uses an LLM to write the investigation summary, while the investigator keeps every final decision.

All modules share the same `CustomerID` and `AccountID`, so one customer can be investigated across every fraud scenario in one workflow.

## Use Cases

### 1. Transaction Fraud Detection
- **Problem:** Fraud causes financial loss, and manual review is not possible at high volume.
- **Solution:** A Random Forest predicts the fraud probability of each transaction. SHAP explains why it was flagged.
- **Labels:** Built from the answer key (14 known fraud transactions). The answer key is never a feature.
- **Features:** amount, hour, night flag, transaction type, transfers in the last hour, unique receivers, amount vs. the sender's normal, new receiver. Only past data is used, to avoid data leakage.
- **Output:** `TX00123 → Fraud Probability 0.87` with reasons such as high amount, night time, new receiver

### 2. Account Takeover Detection
- **Problem:** Fraudsters may access accounts using stolen credentials or compromised devices.
- **Solution:** Isolation Forest finds unusual logins. Simple rules explain why.
- **Features:** new device, new location, failed login attempts, login time
- **Output:** `ACC0100 → New Device, New Location, 3 Failed Attempts`

### 3. Transaction Pattern Analysis
- **Problem:** Fraud often shows up as a pattern over time, not a single transaction.
- **Solution:** Pandas behavior features: transfers in the last hour and day, unique recipients, average amount, time between transfers.
- **Output:** Customer activity summary such as high transfer frequency or multiple recipients

### 4. Relationship Investigation
- **Problem:** Investigators need to see how accounts connect to each other.
- **Solution:** NetworkX account graph with fan-in, fan-out, and connected accounts. A path counts only if each hop is quick and the amount stays close.
- **Output:** Fund movement paths such as `ACC0100 → ACC0250 → ACC0390`

### 5. AI Investigation Reporting
- **Problem:** Investigators spend a lot of time collecting results and writing reports.
- **Solution:** LangChain tools gather evidence from the modules above and send it to GPT, which writes a report. GPT summarizes evidence only and does not make fraud decisions.
- **Example request:** `Investigate Customer CUST001`

```
Investigation Summary
Customer ID: CUST001

- Multiple high-risk transactions identified.
- Login from a previously unseen device.
- Unusually frequent transfers in a short period.
- Multiple connected accounts found.

Overall Assessment: Multiple risk indicators identified.
Further investigation is recommended.
```

## Dataset

Four CSV files in `Data/raw/`:

| File | Columns |
|---|---|
| `customers.csv` | CustomerID, CustomerName, Age, City, CustomerSince |
| `accounts.csv` | AccountID, CustomerID, AccountType, OpeningBalance, CurrentBalance |
| `transactions.csv` | TransactionID, CustomerID, SenderAccount, ReceiverAccount, Amount, Timestamp, TransactionType |
| `login_activity.csv` | LoginID, CustomerID, AccountID, DeviceID, IPAddress, Location, Timestamp, FailedAttempts, LoginStatus |

**Size:** 100 customers, 100 accounts, 814 transactions (800 normal, 14 fraud), 102 logins (100 normal, 2 suspicious).

The raw data has no fraud label. A separate answer key (`Data/answer_key/answer_key.csv`) lists the planted fraud and is used only to build labels and check results.

**Planted fraud scenarios:**

| ID | Scenario | Pattern |
|---|---|---|
| S1 | High-value night transfer | About ₹1.1 to ₹1.5 lakh between 1 AM and 4 AM |
| S2 | Account takeover | New device and city after 3 failed attempts |
| S3 | Rapid transfers | One sender pays 3 accounts within 15 minutes |
| S4 | Mule chain | Money moves through 4 accounts, a bit smaller each hop |

## Project Folder

```
Banking Fraud Investigation/
├── Data/
│   ├── answer_key/answer_key.csv
│   ├── raw/                   # customers, accounts, transactions, login_activity
│   └── generate.ipynb         # creates the data
├── Data_Quality.ipynb              # data checks
└── fraud_detection.ipynb      # Random Forest + SHAP
```

**Run in this order:** `generate.ipynb` → `quality.ipynb` → `fraud_detection.ipynb`

**Packages:** pandas, numpy, faker, scikit-learn, shap, joblib

## Evaluation

Fraud is rare, so accuracy is misleading. The fraud model is judged with the **confusion matrix, precision, and recall**. To avoid cheating:
- features use past data only
- the answer key is never a feature
- `CustomerID`, `TransactionID`, and `CurrentBalance` are not features
- all transactions of one fraud case stay in the same train or test part
- class weights are balanced

## Human Oversight

The platform identifies risks, collects evidence, explains findings, and generates reports. It does **not** freeze accounts, block transactions, label customers as fraudsters, or make final fraud decisions. Every decision stays with the investigator.

## Tech Stack

Python, Pandas, NumPy, Faker · scikit-learn (Random Forest, Isolation Forest) · SHAP · NetworkX · LangChain + OpenAI GPT API · FastAPI · SQLite · Streamlit

## Roadmap

- [x] Synthetic data generator
- [x] Data validation and quality checks
- [ ] Use case 1: Random Forest fraud model with SHAP *(in progress)*
- [ ] Use case 2: Isolation Forest takeover model
- [ ] Use case 3: Transaction pattern features
- [ ] Use case 4: NetworkX relationship graph
- [ ] Use case 5: LangChain + GPT report generation
- [ ] SQLite storage and case management
- [ ] FastAPI endpoints
- [ ] Streamlit dashboard

## Disclaimer

This project uses synthetic data only. It is a portfolio project and is not intended for real-world financial decisions.
