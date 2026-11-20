# Banking Fraud Detection and Investigation

A machine learning-based banking fraud detection proof of concept using synthetic Indian banking transactions. The project covers data generation, fraud detection, model evaluation, API-based predictions and an investigation dashboard with AI-assisted explanations.

## Project Overview

This project identifies potentially fraudulent banking transactions using supervised machine learning.

It compares Random Forest and XGBoost models, selects a model using validation results, and serves predictions through FastAPI. A Streamlit dashboard supports customer-level transaction review, while an OpenAI-powered explanation feature helps interpret selected predictions.

**Project scope:** Synthetic-data-based proof of concept, not a production banking fraud detection system.

## Dataset

The project uses Python and Faker to generate synthetic Indian banking data.

| File | Description | Records |
|---|---|---:|
| `customers.csv` | Customer details | 100 |
| `accounts.csv` | Account information | 100 |
| `transactions.csv` | Banking transaction records | 10,000 |
| `answers.csv` | Ground-truth fraud labels | 10,000 |

### Data Characteristics

- 100 unique customers and 100 accounts.
- Each `AccountID` is identical to its corresponding `CustomerID`.
- 10,000 transactions covering approximately six months.
- Domestic transactions only, in INR.
- 100 fraudulent transactions (1% fraud rate).
- 9,900 legitimate transactions.
- Includes devices, beneficiaries, payment methods, locations and failed login/payment attempts.
- Includes unusual but legitimate transactions to make detection more realistic.

### Fraud Scenarios

The dataset includes four simulated fraud scenarios, with 25 fraudulent transactions per scenario.

| Scenario | Description |
|---|---|
| Account Takeover | Unauthorized account activity following suspicious login attempts. |
| Rapid Fund Transfers | Multiple transfers to different beneficiaries within a short period. |
| Card Testing | Repeated failed card payment attempts followed by successful purchases. |
| Social Engineering | Payments to a newly added beneficiary following a scam. |

Each scenario contains five fraud cases, with five related fraudulent transactions per case.

### Ground-Truth Labels

`answers.csv` contains:

- `TransactionID`
- `IsFraud`
- `FraudCaseID`
- `FraudScenario`

These labels are kept separate from the model's prediction features. They are used as training targets and for evaluating predictions against the actual outcomes.

## Machine Learning Approach

Two supervised machine learning models are trained and compared:

- Random Forest
- XGBoost

### Model Workflow

1. Generate and validate the datasets.
2. Prepare transaction and customer features.
3. Perform feature engineering.
4. Split data into training, validation and testing sets.
5. Train Random Forest and XGBoost pipelines.
6. Compare models using validation results.
7. Select the model and decision threshold using validation data.
8. Evaluate the selected model on the held-out test data.

The split is chronological and group-based, keeping transactions from the same fraud case together.

| Dataset | Transactions | Fraud Transactions |
|---|---:|---:|
| Training | 6,992 | 60 |
| Validation | 1,504 | 20 |
| Testing | 1,504 | 20 |

### Evaluation Metrics

The project evaluates models using:

- Precision
- Recall
- F1 Score
- F2 Score
- PR-AUC (Average Precision)
- Confusion Matrix

Accuracy alone is not sufficient because fraud represents only 1% of the generated data.

### Recorded Test Results

The current evaluation notebook records the following results for the selected XGBoost model:

| Metric | Test Result |
|---|---:|
| Selected Model | XGBoost |
| Decision Threshold | 0.12 |
| Precision | 0.50 |
| Recall | 0.65 |
| F1 Score | 0.565 |
| F2 Score | 0.613 |
| PR-AUC | 0.698 |

**Confusion Matrix**

| Actual / Predicted | Legitimate | Fraud |
|---|---:|---:|
| Legitimate | 1,471 | 13 |
| Fraud | 7 | 13 |

These are results from the currently saved notebook run. They may change when the synthetic dataset is regenerated.

## FastAPI Integration

The selected trained model is served through FastAPI.

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Checks API availability. |
| GET | `/model-info` | Returns model information and decision threshold. |
| POST | `/predict` | Predicts whether a transaction is fraudulent or legitimate. |
| POST | `/explain` | Returns the ML prediction with an AI-generated explanation. |

The prediction response includes:

- Predicted class
- Fraud probability
- Decision threshold
- Selected model

API documentation is available at:

`http://127.0.0.1:8000/docs`

## Streamlit Investigation Dashboard

The Streamlit dashboard provides an interface for reviewing customer transactions.

Key features:

- Search for a customer by ID.
- View customer and account information.
- Review transaction history.
- See fraud probabilities and model predictions.
- Filter flagged transactions.
- Select a transaction to request an AI-generated explanation.

The dashboard also displays the ground-truth scenario for checking predictions in this proof of concept.

## AI-Powered Explanation

The project includes an OpenAI-powered explanation feature.

It uses the ML prediction and selected transaction details to:

- Explain why a transaction was flagged.
- Identify suspicious indicators.
- Suggest practical investigation steps.

The AI explanation does not change the ML prediction and does not treat a flagged transaction as proven fraud.

An OpenAI API key is required for this feature. The core ML prediction API can run without it.

## Project Structure

```text
Banking-Fraud-Detection-and-Investigation/
│
├── app/
│   ├── api.py
│   ├── dashboard.py
│   └── gpt_explainer.py
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
├── src/
│   ├── generate_data.py
│   ├── validate_data.ipynb
│   ├── model_training.ipynb
│   └── model_evaluation.ipynb
│
├── requirements.txt
├── .gitignore
└── README.md
```

## Setup and Installation

### 1. Clone the repository

```bash
git clone https://github.com/Ahmed0000712/Banking-Fraud-Detection-and-Investigation.git
cd Banking-Fraud-Detection-and-Investigation
```

### 2. Create a Python environment (recommended)

Windows CMD:

```cmd
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Generate the dataset

```bash
python src/generate_data.py
```

This generates the four CSV files inside the `data/` directory. Running it again regenerates those files.

## Running the Notebooks

Open the project in VS Code or Jupyter Notebook and run these notebooks in order:

1. `src/validate_data.ipynb`
2. `src/model_training.ipynb`
3. `src/model_evaluation.ipynb`

The training notebook saves the selected model and test data inside `models/`.

Run the training notebook before starting the API if the required model artifacts are not already available.

## Running the Application

### 1. Start FastAPI

From the project root:

```bash
python -m uvicorn app.api:app --reload
```

Open the API documentation:

`http://127.0.0.1:8000/docs`

### 2. Start the Streamlit dashboard

Open a second terminal, activate the same Python environment, and run:

```bash
streamlit run app/dashboard.py
```

### 3. Configure the OpenAI explanation feature

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=your_available_model
```

`OPENAI_MODEL` is optional and can be used to configure the model available to your API account.

Keep your API key private. Never commit the `.env` file to GitHub.

## Technologies Used

- **Python** – Main programming language.
- **Pandas** – Data handling and processing.
- **Scikit-learn** – Preprocessing and Random Forest.
- **XGBoost** – Gradient boosting model.
- **Faker** – Synthetic customer data generation.
- **Joblib** – Model and test-data storage.
- **FastAPI** – Prediction API.
- **Streamlit** – Investigation dashboard.
- **OpenAI API** – AI-assisted prediction explanations.
- **Jupyter Notebook** – Data validation, model training and evaluation.

## Limitations

- The dataset is synthetic and does not represent actual bank transactions.
- The dataset is relatively small and contains only 100 customers.
- Model results on synthetic data do not establish real-world fraud detection performance.
- The system is a proof of concept and requires further validation, security controls, monitoring and testing before any real banking deployment.
- A model prediction indicates potential risk; it is not proof of fraud.

## Project Objective

This is an educational and portfolio project developed to learn and demonstrate an end-to-end banking fraud detection workflow. It uses synthetic data to practice supervised machine learning, model evaluation, API-based prediction serving and AI-assisted fraud investigation.

The project is intended for learning and skill development, not for deployment in a real banking environment. It demonstrates the practical application of AI and machine learning concepts in a simulated banking use case.
