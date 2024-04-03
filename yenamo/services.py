import json
import pandas as pd
import numpy as np


def to_str(data: any)-> str:
    json_data = data.to_json(orient='records')
    json_string = json.dumps(json_data)
    return json_string


def to_df(json_string: str)-> pd.DataFrame:
    json_data = json.loads(json_string)
    df = pd.read_json(json_data)
    return df


def ar_tostr(data):
    data_list = data.tolist()
    json_string = json.dumps(data_list)
    return json_string

def to_ar(json_str: str):
    json_list = json.loads(json_str)
    arr = np.array(json_list)
    return arr