"""Fraud investigation dashboard.
Run from the project root:  streamlit run app/dashboard.py   (FastAPI must be running)"""
import os
from pathlib import Path

import pandas as pd
import requests
import streamlit as st

API = os.getenv("FRAUD_API_URL", "http://127.0.0.1:8000")
DATA = next(p / "data" for p in Path(__file__).resolve().parents if (p / "data").is_dir())
SHOW = ["TransactionDate", "AmountINR", "TransactionType", "PaymentMethod", "Channel", "City",
        "IsNewDevice", "IsNewBeneficiary", "FailedLoginAttempts", "FailedPaymentAttempts",
        "Probability", "Prediction", "FraudScenario"]

st.set_page_config("Fraud Investigation", "🏦", layout="wide")


@st.cache_data
def load():
    cust, acc, tx, ans = (pd.read_csv(DATA / f"{n}.csv") for n in ("customers", "accounts", "transactions", "answers"))
    cust = cust.merge(acc[["CustomerID", "AccountType", "AccountBalanceINR"]], on="CustomerID")
    tx = tx.merge(ans, on="TransactionID").merge(cust, on="CustomerID")
    tx["TransactionDate"] = pd.to_datetime(tx["TransactionDate"])
    return cust, tx


def payload(r):
    """One transaction row (joined with its customer) -> /predict input."""
    return {"amount_inr": float(r.AmountINR), "transaction_date": r.TransactionDate.isoformat(),
            "age": int(r.Age), "monthly_income_inr": float(r.MonthlyIncomeINR),
            "failed_login_attempts": int(r.FailedLoginAttempts),
            "failed_payment_attempts": int(r.FailedPaymentAttempts),
            "is_new_device": bool(r.IsNewDevice), "is_new_beneficiary": bool(r.IsNewBeneficiary),
            "payment_method": r.PaymentMethod, "transaction_type": r.TransactionType,
            "channel": r.Channel, "merchant_category": r.MerchantCategory, "city": r.City,
            "home_city": r.HomeCity, "occupation": r.Occupation,
            "preferred_payment_method": r.PreferredPaymentMethod}


def call(path, body, client=requests):
    r = client.post(f"{API}/{path}", json=body, timeout=60)
    r.raise_for_status()
    return r.json()


customers, TX = load()


@st.cache_data(ttl=300, show_spinner="Scoring this customer's transactions...")
def scan(cid):
    rows = TX[TX.CustomerID == cid].sort_values("TransactionDate")
    with requests.Session() as s:
        out = [call("predict", payload(r), s) for _, r in rows.iterrows()]
    return rows.assign(Probability=[o["fraud_probability"] for o in out],
                       Prediction=[o["prediction"] for o in out])


# ---- sidebar: API status
try:
    info = requests.get(f"{API}/model-info", timeout=3).json()
    st.sidebar.success("FastAPI connected")
    st.sidebar.write(f"Model: **{info['model']}**  \nThreshold: **{info['threshold']:.2%}**")
except (requests.RequestException, ValueError):
    st.sidebar.error("FastAPI is not running")
    st.sidebar.code("python -m uvicorn app.api:app --reload")
    st.stop()

# ---- 1. find a customer (the box is searchable: type an ID or a name)
st.title("Fraud Investigation")
cid = st.selectbox("Search customer (type ID or name)", customers.CustomerID,
                   index=None, placeholder="e.g. CUST007 or a name",
                   format_func=lambda i: f"{i} - {customers.set_index('CustomerID').CustomerName[i]}")
if not cid:
    st.info("Pick a customer to review their transactions.")
    st.stop()

# ---- 2. customer profile
c = customers.set_index("CustomerID").loc[cid]
st.subheader(f"{c.CustomerName}  ·  {cid}")
for col, (label, val) in zip(st.columns(5), [
        ("Age / job", f"{c.Age}, {c.Occupation}"), ("Monthly income", f"₹{c.MonthlyIncomeINR:,.0f}"),
        ("Home city", c.HomeCity), ("Usually pays by", c.PreferredPaymentMethod),
        (f"{c.AccountType} balance", f"₹{c.AccountBalanceINR:,.0f}")]):
    col.caption(label)
    col.markdown(f"**{val}**")

# ---- 3. score every transaction of this customer
try:
    scanned = scan(cid)
except requests.RequestException as e:
    st.error(f"Scoring failed: {e}")
    st.stop()

flagged = scanned[scanned.Prediction == "Fraud"]
st.subheader(f"{len(scanned)} transactions, {len(flagged)} flagged by the model")
st.scatter_chart(scanned, x="TransactionDate", y="Probability", color="Prediction", height=220)

only = st.toggle("Show only flagged transactions", value=len(flagged) > 0)
view = (flagged if only else scanned).sort_values("TransactionDate", ascending=False)
sel = st.dataframe(view[SHOW], hide_index=True, on_select="rerun",
                   selection_mode="single-row", key=f"t_{cid}_{only}",
                   column_config={"Probability": st.column_config.ProgressColumn(
                       "Fraud probability", min_value=0.0, max_value=1.0, format="%.2f"),
                       "FraudScenario": "Answer key"})
st.caption("'Answer key' is the true label from answers.csv, shown so you can check the model.")

# ---- 4. explain a selected transaction
if not sel.selection.rows:
    st.info("Select a transaction row to get an explanation.")
elif st.button("Explain selected transaction", type="primary"):
    row = view.iloc[sel.selection.rows[0]]
    with st.spinner("Asking the model and the explainer..."):
        try:
            res = call("explain", payload(row))
        except requests.RequestException:
            res = call("predict", payload(row))
            st.warning("The explanation service is unavailable, showing the prediction only.")
    (st.error if res["prediction"] == "Fraud" else st.success)(
        f"{res['prediction']} - probability {res['fraud_probability']:.2%} "
        f"(threshold {res['threshold']:.2%})")
    if "explanation" in res:
        st.markdown(res["explanation"])
    st.caption("ML prediction, not proof of fraud")