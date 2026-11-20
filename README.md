# Banking Fraud Detection and Investigation

## Project Overview

This project develops a machine learning-based banking fraud detection system to identify potentially fraudulent transactions using synthetic Indian banking data.

It uses **Random Forest and XGBoost** to detect suspicious transactions and **FastAPI** to serve predictions through an API.

The project focuses on realistic transaction patterns, fraud detection, model evaluation and prediction serving.

## Dataset

A synthetic banking dataset was generated using Python and Faker.

| Dataset | Description | Records |
|---|---|---:|
| `customers.csv` | Customer information | 100 |
| `accounts.csv` | Customer account information | 100 |
| `transactions.csv` | Banking transaction records | 10,000 |
| `answers.csv` | Actual fraud labels and scenario details | 10,000 |

### Data Characteristics

- 100 unique customers with different names.
- 100 accounts, with `AccountID` identical to `CustomerID`.
- 10,000 transactions covering six months.
- All transactions are domestic Indian transactions in INR.
- Exactly 100 fraudulent transactions (1% fraud rate).
- Includes transaction amounts, payment methods, devices, beneficiaries, locations and failed login/payment attempts.

### Fraud Scenarios

The dataset contains four simulated fraud scenarios, with 25 fraudulent transactions per scenario.

1. **Account Takeover:** Unauthorized account access following suspicious login attempts.
2. **Rapid Fund Transfers:** Multiple transfers to different beneficiaries within a short period.
3. **Card Testing:** Repeated failed card payment attempts followed by successful purchases.
4. **Social Engineering:** Multiple payments to a newly added beneficiary following a scam.

Each scenario contains five separate fraud cases, with five related fraudulent transactions per case.

The dataset also includes legitimate unusual transactions to make fraud detection less dependent on obvious patterns.

### Ground-Truth Labels

`answers.csv` contains:

- `TransactionID`
- `IsFraud`
- `FraudCaseID`
- `FraudScenario`

The answer key is kept separate from model input features. Test labels are hidden during prediction and used only afterward to evaluate model performance.

## Machine Learning Approach

Two supervised machine learning algorithms are trained and compared:

- Random Forest
- XGBoost

### Workflow

1. Load and validate the generated datasets.
2. Perform feature engineering.
3. Prepare numerical and categorical features.
4. Split the data into training, validation and test sets.
5. Train Random Forest and XGBoost.
6. Compare model performance using validation data.
7. Select the model and decision threshold using validation results.
8. Predict on unseen test transactions.
9. Compare predictions against actual test labels.

### Evaluation Metrics

The models are evaluated using:

- Precision
- Recall
- F1 Score
- F2 Score
- PR-AUC (Average Precision)
- Confusion Matrix

Because fraud represents only 1% of the generated transactions, accuracy alone is not used to judge model performance.

## FastAPI Integration

The selected trained model is integrated with FastAPI to provide transaction fraud predictions.

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Checks API availability |
| GET | `/model-info` | Returns selected model information |
| POST | `/predict` | Predicts whether a transaction is fraudulent or legitimate |

The prediction response includes the predicted class, fraud probability, decision threshold and selected model.

## Project Structure

```text
Banking-Fraud-Detection/
│
├── app/
│   ├── __init__.py
│   └── api.py
│
├── data/
│   ├── customers.csv
│   ├── accounts.csv
│   ├── transactions.csv
│   └── answers.csv
│
├── models/
│   ├── fraud_model.joblib
│   └── test_data.joblib
│
├── notebooks/
│   ├── 02_data_validation.ipynb
│   ├── 03_model_training.ipynb
│   └── 04_model_evaluation.ipynb
│
├── src/
│   └── generate_data.py
│
├── requirements.txt
├── .gitignore
└── README.md
```

## Project Objective

To develop an understandable end-to-end fraud detection proof of concept that demonstrates synthetic data generation, supervised machine learning, model evaluation and API-based prediction serving.
