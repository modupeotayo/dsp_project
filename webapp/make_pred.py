import streamlit as st
import pandas as pd
import numpy as np
import json
import requests
from equipfailpred import FEATURES

ID = ['Product ID']
FEATURES = ['Air temperature [K]', 'Process temperature [K]', 'Rotational speed [rpm]', 'Torque [Nm]', 'Tool wear [min]', 'Type']
COLNAME = ID + FEATURES
MODEL_API_URL = "http://127.0.0.1:8000/predict"


def to_str(df)-> str:
    json_data = df.to_json(orient='records')
    json_string = json.dumps(json_data)
    return json_string

    
def to_ar(json_str: str):
    json_list = json.loads(json_str)
    arr = np.array(json_list)
    return arr



def callmodel(df):
    df_str = to_str(df)
    response = requests.post(MODEL_API_URL, json={"source": 'webapp', "df":df_str})
    if response.status_code == 200:
        result = response.json()['pred']
        st.write("Done!")
        return result
    else:
        st.error("Failed to make prediction. Please try again.")
        return 'Failed!'


def single_prediction():
    st.title("Prediction Page")
    st.subheader("Single Sample Prediction")
    product_id = st.text_input("Product ID",placeholder='H12345')
    type_value = st.selectbox("Type", options=["L", "M", "H"])
    air_temp = st.number_input("Air temperature [K]", value=0.0)
    process_temp = st.number_input("Process temperature [K]", value=0.0)
    rotational_speed = st.number_input("Rotational speed [rpm]", value=0)
    torque = st.number_input("Torque [Nm]", value=0.0)
    tool_wear = st.number_input("Tool wear [min]", value=0)
    
    data = [
        str(product_id),
        float(air_temp),
        float(process_temp),
        int(rotational_speed),
        float(torque),
        int(tool_wear),
        type_value]
    
    df = pd.DataFrame([data],columns=COLNAME)
    st.write(df)
    if st.button("Predict Single Sample"):
        result = callmodel(df)
        st.write(result)
            

def multi_predictions():
    st.title('Predict tool failure')
    st.header('Sample Prediction')
    df = pd.DataFrame()    
    uploaded_file = st.file_uploader('Upload CSV file')

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        col1, col2 = st.columns(2)
        with col1:
            sample_size = st.number_input(
                "sample size (between 5 and 200)",
                min_value=5, max_value=200)
            sample_size = int(sample_size)
        with col2:
            random_state = st.number_input(
                "random state (between 1 and 100)",
                min_value=0, max_value=100)
            random_state=int(random_state)
            
        sample_df = df.sample(n=sample_size,random_state=random_state)
        st.write('Sample data:',sample_df)
        
    if st.button('Predict'):
        if uploaded_file is not None:
            result = callmodel(sample_df)
            st.write(result)
        else:
            st.error('File not detected, Please upload a valid .csv file')


def manual_pred():
    userpick=st.radio(label='Pick', options=['Single Prediction','CSV file'])
    if userpick == 'Single Prediction':
        single_prediction()
    else:
        multi_predictions()
        
        