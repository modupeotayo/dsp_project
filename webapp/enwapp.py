# streamlit_app.py
import streamlit as st
import requests
from datetime import date

# Streamlit UI
st.title("Prediction App")

# Input text box for user input
user_input = st.text_input("Enter your data")

# Dropdown for selecting source
source_predict = st.selectbox("Select source for prediction", ["webapp", "schedule"], key="source_predict")

# Button to trigger prediction
if st.button("Predict"):
    # Make a request to FastAPI for prediction
    response = requests.post("http://localhost:8000/predict/", json={"data": user_input, "source": source_predict})
    if response.status_code == 200:
        prediction = response.json()["prediction"]
        st.write(f"Prediction: {prediction}")
    else:
        st.error("Failed to get prediction")

# Page for fetching data based on user input
st.header("Fetch Data")
from_date = st.date_input("From Date", value=date.today())
to_date = st.date_input("To Date", value=date.today())
source_fetch = st.selectbox("Select source for fetching data", ["webapp", "scheduler"], key="source_fetch")

# Button to trigger data retrieval
if st.button("Fetch Data"):
    # Make a request to FastAPI for data retrieval
    data_response = requests.get("http://localhost:8000/data/", params={"from_date": from_date, "to_date": to_date, "source": source_fetch})
    if data_response.status_code == 200:
        data = data_response.json()
        st.write("Predictions:")
        for item in data:
            st.write(f"Date: {item['date']}, Source: {item['source']}, Input Data: {item['input_data']}, Prediction: {item['prediction']}")
    else:
        st.error("Failed to get predictions")
