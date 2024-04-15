import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, Date, JSON
from fastapi import FastAPI, HTTPException
from equipfailpred import FEATURES
from equipfailpred.inference import make_predictions
from pydantic import BaseModel
import pandas as pd
import json
from typing import List

app = FastAPI()

DB_USER = "postgres"
DB_PASSWORD = "postgres"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "my_newdb"

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date)
    source = Column(String)
    input_data = Column(JSON)
    prediction = Column(String)

Base.metadata.create_all(bind=engine)

class PredictionResponse(BaseModel):
    id: int
    date: datetime.date
    source: str
    input_data: dict
    prediction: str

class PastPredictionRequest(BaseModel):
    from_date: str
    to_date: str
    source: str

class ToPred(BaseModel):
    source: str
    df: str

def to_df(json_string: str)-> pd.DataFrame:
    json_data = json.loads(json_string)
    return pd.DataFrame.from_dict(json_data)

@app.post("/predict")
async def makePredictions(data: ToPred):
    df = to_df(data.df)
    result = make_predictions(df[FEATURES])

    session = SessionLocal()
    try:
        for index, row in df.iterrows():
            prediction = Prediction(
                date=datetime.date.today(),
                source=data.source,
                input_data=json.dumps(row.to_dict()),
                prediction=result[index]
            )
            session.add(prediction)
        session.commit()
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()

    return {"message": "Predictions stored successfully"}


@app.post("/past-predictions", response_model=List[PredictionResponse])
async def fetch_predictions(request_data: PastPredictionRequest):
    from_date = datetime.strptime(request_data.from_date, '%Y-%m-%d').date()
    to_date = datetime.strptime(request_data.to_date, '%Y-%m-%d').date()

    session = SessionLocal()
    try:
        # Query database for predictions within date range
        if request_data.source.lower() == "all":
            predictions = session.query(Prediction).filter(
                Prediction.date.between(from_date, to_date)
            ).all()
        else:
            predictions = session.query(Prediction).filter(
                Prediction.date.between(from_date, to_date),
                Prediction.source == request_data.source
            ).all()

        # Parse predictions into response model
        prediction_responses = []
        for prediction in predictions:
            input_data = json.loads(prediction.input_data)
            prediction_response = PredictionResponse(
                id=prediction.id,
                date=prediction.date,
                source=prediction.source,
                input_data=input_data,
                prediction=prediction.prediction
            )
            prediction_responses.append(prediction_response)

        return prediction_responses
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()