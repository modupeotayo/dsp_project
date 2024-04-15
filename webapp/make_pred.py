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


def prepare_value_for_df(result):
    try:
        result_list = json.loads(result)
        if isinstance(result_list, list):
            final_value = [int(x) for x in result_list]
        else:
            final_value = int(result_list)
    except json.JSONDecodeError:
        if isinstance(result, str) and result.isdigit():
            final_value = int(result)
        else:
            final_value = None
    except ValueError:
        final_value = None
    return final_value


def add_prediction_column_to_df(df, prediction_result):
    final_value = prepare_value_for_df(prediction_result)
    df['Predictions'] = final_value
    return df


def callmodel(df):
    df_str = to_str(df)
    response = requests.post(MODEL_API_URL, json={"source": 'webapp', "df":df_str})
    if response.status_code == 200:
        result = response.json()['pred']
        st.success("Done!")
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
        final_df = add_prediction_column_to_df(df,result)
        st.write(final_df)
            

def multi_predictions():
    st.title('Predict tool failure')
    st.header('Sample Prediction')
    df = pd.DataFrame()    
    uploaded_file = st.file_uploader('Upload CSV file')

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.write('Shape of the .CSV file',df.shape)
        st.write('data:',df)
        
    if st.button('Predict'):
        if uploaded_file is not None:
            result = callmodel(df)
            final_df = add_prediction_column_to_df(df,result)
            st.write('Shape of the results',final_df.shape)
            st.write(final_df)
        else:
            st.error('File not detected, Please upload a valid .csv file')


def manual_pred():
    userpick=st.radio(label='Pick', options=['Single Prediction','CSV file'])
    if userpick == 'Single Prediction':
        single_prediction()
    else:
        multi_predictions()
        
        