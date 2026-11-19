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

## Installation and Setup

### 1. Clone the repository

```bash
git clone <your-github-repository-url>
cd <your-project-folder>
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it in Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Generate the dataset

```bash
python src/generate_data.py
```

This generates the four CSV files inside the `data` folder.

### 5. Run the notebooks

Open the notebooks in VS Code or Jupyter and execute them in order:

1. Data validation
2. Model training
3. Model evaluation

The training notebook saves the selected model in the `models` folder.

### 6. Start FastAPI

From the project root directory, run:

```bash
python -m uvicorn app.api:app --reload
```

### 7. Open API documentation

Visit:

`http://127.0.0.1:8000/docs`

Use the interactive Swagger documentation to submit transaction details and receive fraud predictions.


## Current Development Status

**Completed:**
- Synthetic banking data generation.
- Data validation and quality checks.
- Random Forest and XGBoost model training and comparison.
- Model evaluation and initial error analysis.
- FastAPI prediction integration.

**Remaining:**
- Streamlit dashboard development.
- Final project documentation and GitHub updates.

## Project Objective

To develop an understandable end-to-end fraud detection proof of concept that demonstrates synthetic data generation, supervised machine learning, model evaluation and API-based prediction serving.
