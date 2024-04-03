from datetime import date
from sqlalchemy.orm import sessionmaker
from sqlalchemy import MetaData, Table, create_engine
import databases
import pandas as pd
import json
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from equipfailpred import FEATURES
from equipfailpred.inference import make_predictions
from contextlib import asynccontextmanager
# from models import Prediction
from typing import List



COLM_ORDER = ['Product ID', 'Air temperature [K]', 'Process temperature [K]', 'Rotational speed [rpm]', 'Torque [Nm]', 'Tool wear [min]', 'Type']
DATABASE_URL = "postgresql://postgres:postgres@localhost/my_newdb"
TABLE = 'single_prediction'
database = databases.Database(DATABASE_URL)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

metadata = MetaData()

table_name = "single_prediction"
# table = Table(table_name, metadata, autoload_with=engine)


class FetchPred(BaseModel):
    start_date: str
    end_date: str
    soruce: str


class ToPred(BaseModel):
    source: str
    df: str


def ar_tostr(data):
    data_list = data.tolist()
    json_string = json.dumps(data_list)
    return json_string


def to_df(json_string: str)-> pd.DataFrame:
    json_data = json.loads(json_string)
    df = pd.read_json(json_data)
    return df


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    yield
    await database.disconnect()


app = FastAPI(lifespan=lifespan)
df = pd.DataFrame


@app.post("/predict")
async def makePredictions(data: ToPred):
    df = to_df(data.df)
    result = make_predictions(df[FEATURES])
    pred = ar_tostr(result)
    final_df = df[COLM_ORDER].copy()
    final_df['Predictions'] = result
    
    if len(df) == 1:
        table = 'single_prediction'
    else:
        table = 'multiple_predictions'
        
    current_date = date.today()
    final_df['date'] = current_date.strftime("%Y-%m-%d")  
    final_df['source'] = data.source
    
    final_df = final_df.rename(columns={
            'Product ID': 'product_id',
            'Air temperature [K]': 'air_temperature_k',
            'Process temperature [K]': 'process_temperature_k',
            'Rotational speed [rpm]': 'rotational_speed_rpm',
            'Torque [Nm]': 'torque_nm',
            'Tool wear [min]': 'tool_wear_min',
            'Type': 'type',
            'Predictions': 'prediction'
        })
    print(final_df)
    try:
        final_df.to_sql(table, engine, if_exists='append', index=False)
        message = "Single prediction inserted successfully" if len(df) == 1 else "Multiple predictions inserted successfully"
        return {"message": message,"pred":pred}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class Prediction(BaseModel):
    product_id: str
    air_temperature_k: float
    process_temperature_k: float
    rotational_speed_rpm: int
    torque_nm: float
    tool_wear_min: int
    type: str
    prediction: int
    date: str
    source: str


class PredictionRequest(BaseModel):
    start_date: date
    end_date: date
    source: str


class PredictionResponse(BaseModel):
    product_id: str
    air_temperature_k: float
    process_temperature_k: float
    rotational_speed_rpm: int
    torque_nm: float
    tool_wear_min: int
    type: str
    prediction: int
    date: date
    source: str


# @app.get("/past-predictions")
# async def fetchPredicitons(start_date: date, end_date: date, source: str = "all") -> List[PredictionResponse]:
#     db = SessionLocal()
#     try:
#         query = table.select().where(table.c.date.between(start_date, end_date) & (table.c.source == source))
#         result = db.execute(query).fetchall()

#         # Convert result to list of Data objects
#         data_list = [PredictionResponse(**row) for row in result]
#         return data_list
#     finally:
#         db.close()
        