import pandas as pd
import numpy as np
from equipfailpred.preprocess import preprocessor, predict


def make_predictions(input_data: pd.DataFrame) -> np.ndarray:
    processed_data = preprocessor(input_data, False)
    predictions = predict(processed_data)
    return predictions

def selective_predict(features: list[str], data: pd.DataFrame)-> np.ndarray:
    selected_data = data[features]
    pred = make_predictions(selected_data)
    return pred