import streamlit as st
import requests
import pandas as pd


API_URL = "http://localhost:8000/past-predictions"

def past_prediction():
    st.title("Fetch Predictions")

    start_date = st.date_input("Start Date")
    end_date = st.date_input("End Date")
    source = st.selectbox("Source of Prediction", ["all", "webapp", "scheduler"])

    if st.button("Fetch Predictions"):
        request_data = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "source": source
        }

        response = requests.get(API_URL, params=request_data)

        if response.status_code == 200:
            predictions = pd.DataFrame(response.json())
            if not predictions.empty:
                st.write(predictions)
            else:
                st.write("No predictions found for the selected criteria.")
        else:
            st.error("Failed to fetch predictions. Please try again.")
