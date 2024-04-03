from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import databases
import sqlalchemy
import pandas as pd
import json

DATABASE_URL = "postgresql://postgres:postgres@localhost/my_newdb"
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

class PredictionRecord(BaseModel):
    df: str
    # product_id: str
    # type: str
    # air_temperature_k: float
    # process_temperature_k: float
    # rotational_speed_rpm: int
    # torque_nm: float
    # tool_wear_min: int
    # prediction: int

class PredictionData(BaseModel):
    records: List[PredictionRecord]

# Define SQLAlchemy table metadata (assuming both tables have the same structure)
table_single = sqlalchemy.Table(
    "single_prediction", metadata,
    sqlalchemy.Column('product_id', sqlalchemy.String, primary_key=True),
    sqlalchemy.Column('type', sqlalchemy.CHAR),
    sqlalchemy.Column('air_temperature_k', sqlalchemy.Float),
    sqlalchemy.Column('process_temperature_k', sqlalchemy.Float),
    sqlalchemy.Column('rotational_speed_rpm', sqlalchemy.Integer),
    sqlalchemy.Column('torque_nm', sqlalchemy.Float),
    sqlalchemy.Column('tool_wear_min', sqlalchemy.Integer),
    sqlalchemy.Column('prediction', sqlalchemy.Integer),
)

table_multiple = sqlalchemy.Table(
    "multiple_predictions", metadata,
    sqlalchemy.Column('product_id', sqlalchemy.String, primary_key=True),
    sqlalchemy.Column('type', sqlalchemy.CHAR),
    sqlalchemy.Column('air_temperature_k', sqlalchemy.Float),
    sqlalchemy.Column('process_temperature_k', sqlalchemy.Float),
    sqlalchemy.Column('rotational_speed_rpm', sqlalchemy.Integer),
    sqlalchemy.Column('torque_nm', sqlalchemy.Float),
    sqlalchemy.Column('tool_wear_min', sqlalchemy.Integer),
    sqlalchemy.Column('prediction', sqlalchemy.Integer),
)
def to_df(json_string: str)-> pd.DataFrame:
    json_data = json.loads(json_string)
    df = pd.read_json(json_data)
    return df

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code: connect to the database
    await database.connect()
    yield  # The application is now running
    # Cleanup code: disconnect from the database
    await database.disconnect()

app = FastAPI()

@app.router.lifecycle.on_startup
async def startup():
    await database.connect()

@app.router.lifecycle.on_shutdown
async def shutdown():
    await database.disconnect()

@app.post("/insert_data/")
async def insert_data(data: PredictionData):
    df = to_df(data.df)
    
