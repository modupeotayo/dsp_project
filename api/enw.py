# fastapi_app.py
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import date

# Initialize FastAPI app
app = FastAPI()

# PostgreSQL connection parameters
DB_USER = "postgres"
DB_PASSWORD = "postgres"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "my_newdb"

# SQLAlchemy engine
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)

# SQLAlchemy session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative base for SQLAlchemy models
Base = declarative_base()

# SQLAlchemy model for predictions
class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date)
    source = Column(String)
    input_data = Column(String)
    prediction = Column(String)

# Create tables
Base.metadata.create_all(bind=engine)

# Define a model for input data
class InputData(BaseModel):
    data: str
    source: str

# FastAPI route for prediction
@app.post("/predict/")
async def predict(data: InputData):
    # Here you would put your actual prediction logic
    # For now, let's just return the data received
    prediction = data.data
    # Store data, prediction, date, and source in PostgreSQL using SQLAlchemy
    db = SessionLocal()
    db_prediction = Prediction(date=date.today(), source=data.source, input_data=data.data, prediction=prediction)
    db.add(db_prediction)
    db.commit()
    db.refresh(db_prediction)
    db.close()
    return {"prediction": prediction}

# FastAPI route for fetching data based on user input
@app.get("/data/")
async def get_data(from_date: date, to_date: date, source: str):
    db = SessionLocal()
    data = db.query(Prediction).filter(Prediction.date >= from_date, Prediction.date <= to_date, Prediction.source == source).all()
    db.close()
    return data
