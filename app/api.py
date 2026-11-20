
from app.gpt_explainer import explain_prediction

from fastapi import FastAPI
from pydantic import BaseModel, Field
from pathlib import Path
from datetime import datetime
import pandas as pd
import joblib

# Load saved model
ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "models" / "fraud_model.joblib"

saved = joblib.load(MODEL_PATH)

model = saved["model"]
features = saved["features"]
threshold = saved["threshold"]
model_name = saved["model_name"]

app = FastAPI(title="Banking Fraud Detection API")


# Transaction input
class Transaction(BaseModel):
    amount_inr: float = Field(gt=0)
    transaction_date: datetime
    age: int = Field(ge=18, le=100)
    monthly_income_inr: float = Field(gt=0)

    failed_login_attempts: int = Field(default=0, ge=0)
    failed_payment_attempts: int = Field(default=0)

    is_new_device: bool = False
    is_new_beneficiary: bool = False

    payment_method: str
    transaction_type: str
    channel: str
    merchant_category: str
    city: str
    home_city: str
    occupation: str
    preferred_payment_method: str


# Prepare transaction features
def prepare_features(transaction):

    hour = transaction.transaction_date.hour

    row = {
        "AmountINR": transaction.amount_inr,
        "AmountToIncomeRatio": (
            transaction.amount_inr / transaction.monthly_income_inr
        ),
        "Hour": hour,
        "DayOfWeek": transaction.transaction_date.weekday(),
        "IsNight": int(hour < 6 or hour >= 22),
        "Age": transaction.age,
        "MonthlyIncomeINR": transaction.monthly_income_inr,
        "FailedLoginAttempts": transaction.failed_login_attempts,
        "FailedPaymentAttempts": transaction.failed_payment_attempts,
        "IsNewDevice": int(transaction.is_new_device),
        "IsNewBeneficiary": int(transaction.is_new_beneficiary),
        "IsDifferentCity": int(transaction.city != transaction.home_city),
        "PaymentMethod": transaction.payment_method,
        "TransactionType": transaction.transaction_type,
        "Channel": transaction.channel,
        "MerchantCategory": transaction.merchant_category,
        "City": transaction.city,
        "Occupation": transaction.occupation,
        "PreferredPaymentMethod": transaction.preferred_payment_method
    }

    return pd.DataFrame([row], columns=features)


# Get prediction from ML model
def get_prediction(transaction):

    X = prepare_features(transaction)

    probability = float(model.predict_proba(X)[0][1])
    prediction = int(probability >= threshold)

    return {
        "prediction": "Fraud" if prediction else "Legitimate",
        "fraud_probability": round(probability, 4),
        "threshold": threshold,
        "model": model_name
    }


@app.get("/health")
def health():
    return {"status": "API is running"}


@app.get("/model-info")
def model_info():
    return {
        "model": model_name,
        "threshold": threshold,
        "features": len(features)
    }


@app.post("/predict")
def predict(transaction: Transaction):
    return get_prediction(transaction)


# GPT explains the ML prediction
@app.post("/explain")
def explain(transaction: Transaction):

    result = get_prediction(transaction)

    details = {
        **result,
        "amount_inr": transaction.amount_inr,
        "payment_method": transaction.payment_method,
        "transaction_type": transaction.transaction_type,
        "city": transaction.city,
        "home_city": transaction.home_city,
        "failed_login_attempts": transaction.failed_login_attempts,
        "failed_payment_attempts": transaction.failed_payment_attempts,
        "is_new_device": transaction.is_new_device,
        "is_new_beneficiary": transaction.is_new_beneficiary
    }

    explanation = explain_prediction(details)

    return {
        **result,
        "explanation": explanation
    }
