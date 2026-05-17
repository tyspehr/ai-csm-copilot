import os
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

st.set_page_config(
    page_title="AI Customer Success Risk Copilot",
    page_icon="📊",
    layout="wide"
)

st.title("AI Customer Success Risk Copilot")
st.write("Analyze customer health and churn risk.")

df = pd.read_csv("fake_accounts.csv")

account_names = df["account_name"].tolist()
selected_account = st.selectbox("Select a customer account", account_names)

account = df[df["account_name"] == selected_account].iloc[0]

col1, col2, col3, col4 = st.columns(4)

col1.metric("Contract Value", f"${account['contract_value']:,}")
col2.metric("Usage Change", f"{account['usage_change']}%")
col3.metric("Support Tickets", int(account["support_tickets"]))
col4.metric("NPS", int(account["nps"]))

st.subheader("Account Notes")
st.write(account["last_meeting_notes"])

def calculate_basic_risk(account):
    score = 0

    if account["usage_change"] < -30:
        score += 35
    elif account["usage_change"] < -10:
        score += 20

    if account["support_tickets"] >= 8:
        score += 30
    elif account["support_tickets"] >= 4:
        score += 15

    if account["nps"] <= 4:
        score += 30
    elif account["nps"] <= 6:
        score += 15

    if score >= 70:
        return "High", score
    elif score >= 35:
        return "Medium", score
    else:
        return "Low", score

risk_level, risk_score = calculate_basic_risk(account)

st.subheader("Rule-Based Risk Score")
if risk_level == "High":
    st.error(f"Risk Level: {risk_level}")

elif risk_level == "Medium":
    st.warning(f"Risk Level: {risk_level}")

else:
    st.success(f"Risk Level: {risk_level}")
st.progress(min(risk_score, 100))

if st.button("Generate AI Customer Success Brief"):

    prompt = f"""
You are an expert Customer Success Manager.

Analyze this customer account.

Account Name: {account['account_name']}
Industry: {account['industry']}
Contract Value: ${account['contract_value']}
Renewal Date: {account['renewal_date']}
Usage Change: {account['usage_change']}%
Support Tickets: {account['support_tickets']}
NPS: {account['nps']}
Meeting Notes: {account['last_meeting_notes']}

Provide:
1. Executive Summary
2. Churn Risk Assessment
3. Key Risks
4. Recommended Actions
5. Draft Follow-Up Email
6. Customer Sentiment Analysis
"""

    with st.spinner("Generating AI brief..."):

        response = client.chat.completions.create(
            model="gpt-5.5",
            messages=[
                {
                    "role": "system",
                    "content": "You are a customer success expert."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        ai_output = response.choices[0].message.content

    st.subheader("AI Customer Success Brief")
    st.write(ai_output)