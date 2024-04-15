import datetime
from datetime import date
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, Date
import pandas as pd
import json
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from equipfailpred import FEATURES
from equipfailpred.inference import make_predictions
from typing import List
from io import StringIO

app = FastAPI()
df = pd.DataFrame
COLM_ORDER = ['Product ID', 'Air temperature [K]', 'Process temperature [K]', 'Rotational speed [rpm]', 'Torque [Nm]', 'Tool wear [min]', 'Type']

DB_USER = "postgres"
DB_PASSWORD = "postgres"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "my_newdb"

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
TABLE = 'single_prediction'
# database = databases.Database(DATABASE_URL)
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date)
    source = Column(String)
    input_data = Column(String)
    prediction = Column(String)

Base.metadata.create_all(bind=engine)

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
    json_data_io = StringIO(json_data)
    df = pd.read_json(json_data_io)
    return df


@app.post("/predict")
async def makePredictions(data: ToPred) :
    df = to_df(data.df)
    result = make_predictions(df[FEATURES])
    pred = ar_tostr(result)
    final_df = df[COLM_ORDER].copy()
    final_df['Predictions'] = result
    
    if len(df) == 1:
        table = 'single_prediction'
    else:
        table = 'multiple_predictions'
        
    current_date = datetime.date.today()
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


# class PredictionRequest(BaseModel):
#     start_date: date
#     end_date: date
#     source: str


class PredictionResponse(BaseModel):
    product_id: str
    air_temperature_k: float
    process_temperature_k: float
    rotational_speed_rpm: int
    torque_nm: float
    tool_wear_min: int
    type: str
    prediction: int
    date: datetime.date
    source: str

@app.get("/data/")
async def get_data(from_date: date, to_date: date, source: str):
    db = SessionLocal()
    data = db.query(Prediction).filter(Prediction.date >= from_date, Prediction.date <= to_date, Prediction.source == source).all()
    db.close()
    return data


@app.get("/past-predictions", response_model=List[PredictionResponse])
async def fetch_predictions(start_date: str, end_date: str, source: str):
    print(f"Received: start_date={start_date}, end_date={end_date}, source={source}")
    try:
        datetime.datetime.strptime(start_date, '%Y-%m-%d')
        datetime.datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    query = "SELECT * FROM single_prediction WHERE date BETWEEN :start_date AND :end_date"
    values = {"start_date": start_date, "end_date": end_date}

    if source.lower() != "all":
        query += " AND source = :source"
        values["source"] = source

    try:
        rows = await database.fetch_all(query=query, values=values)
        return [PredictionResponse(**row) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        