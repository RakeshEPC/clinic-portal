import streamlit as st
import json
import pandas as pd
from datetime import datetime
import os

# Load config (for login code, modules, etc.)
config = json.load(open("config.json"))

st.set_page_config(page_title="Clinic Portal", layout="centered")

# --- LOGIN ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
   st.title("🔐 Secure Clinic Portal Login")
code_input = st.text_input("Enter your access code:")

if st.button("Login"):
    if code_input.strip() == config.get("access_code", ""):
        st.session_state.logged_in = True
    else:
        st.error("Invalid code. Please try again.")

if not st.session_state.logged_in:
    st.stop()


# --- MAIN APP ---
st.title("🏥 Clinic Follow-Up + Diabetes Education")

# Follow-up Module
if config.get("enable_followup", True):
    st.header("📬 Pre/Post Visit Follow-Up Tool")
    file = st.file_uploader("Upload Excel file with patient emails", type=["xlsx"])
    if file:
        df = pd.read_excel(file)
        st.success(f"Loaded {len(df)} patients.")
        st.write(df.head())
        st.markdown("Emails would be sent in production.")

# Education Module
if config.get("enable_education", True):
    st.header("🎓 Diabetes Education Intake")

    with st.form("intake_form"):
        name = st.text_input("Full Name")
        email = st.text_input("Email Address")
        dob = st.date_input("Date of Birth")
        diabetes_type = st.selectbox("Type of Diabetes", ["Type 1", "Type 2", "Gestational", "Not sure"])
        insulin = st.radio("Do you take insulin?", ["Yes", "No"])
        answer1 = st.text_area("❓ What do you understand about insulin?")
        submit = st.form_submit_button("Submit")

    if submit:
        submitted_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_row = pd.DataFrame([{
            "Timestamp": submitted_time,
            "Name": name,
            "Email": email,
            "DOB": dob,
            "Diabetes Type": diabetes_type,
            "Insulin Use": insulin,
            "Insulin Answer": answer1
        }])

        file_exists = os.path.isfile("responses.csv")
        if file_exists:
            existing = pd.read_csv("responses.csv")
            updated = pd.concat([existing, new_row], ignore_index=True)
        else:
            updated = new_row

        updated.to_csv("responses.csv", index=False)
        st.success("Response saved!")

# Download Responses
if os.path.exists("responses.csv"):
    st.header("📥 Download Patient Responses")
    with open("responses.csv", "rb") as f:
        st.download_button("Download CSV", f, file_name="responses.csv")
