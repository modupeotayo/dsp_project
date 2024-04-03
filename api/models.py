from sqlalchemy import create_engine, Column, Integer, Float, String, Date
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Prediction(Base):
    __tablename__ = 'multiple_predictions'

    product_id = Column(String, primary_key=True)
    air_temperature_k = Column(Float)
    process_temperature_k = Column(Float)
    rotational_speed_rpm = Column(Integer)
    torque_nm = Column(Float)
    tool_wear_min = Column(Integer)
    type = Column(String)
    prediction = Column(Integer)
    date = Column(Date)
    source = Column(String)
