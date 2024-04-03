import streamlit as st
import requests
from datetime import date

# FETCHING_API_URL = "http://localhost:8000/past-predictions?start_date={start_date}&end_date={end_date}&source={source}"

def past_prediction():
    st.title('Past Predictions')
    start_date = st.date_input('Start Date', value=date.today())
    end_date = st.date_input('End Date', value=date.today())
    source = st.selectbox('Data Source', ['webapp', 'scheduler', 'all'])
    # if st.button('Fetch Predictions'):
    #     response = requests.post(f"http://localhost:8000/past-predictions?start_date={start_date}&end_date={end_date}&source={source}")
    #     if response.status_code == 200:
    #         predictions = response.json()
    #         st.write(predictions)
    #     else:
    #         st.write("Error fetching predictions.")
