import streamlit as st
import requests
from datetime import date
# import pandas as pd


# API_URL = "http://localhost:8000/past-predictions"

def past_prediction():
    st.header("Fetch Data")
    from_date = st.date_input("From Date", value=date.today())
    to_date = st.date_input("To Date", value=date.today())
    source_fetch = st.selectbox("Select source for fetching data", ["webapp", "scheduler"], key="source_fetch")

    # Button to trigger data retrieval
    if st.button("Fetch Data"):
        # Make a request to FastAPI for data retrieval
        data_response = requests.get("http://localhost:8000/past-predictions", params={"from_date": from_date, "to_date": to_date, "source": source_fetch})
        if data_response.status_code == 200:
            data = data_response.json()
            st.write("Predictions:")
            for item in data:
                st.write(f"Date: {item['date']}, Source: {item['source']}, Input Data: {item['input_data']}, Prediction: {item['prediction']}")
        else:
            st.error("Failed to get predictions")
