from pydantic import BaseModel
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean


from database import Base, engine

# define the schema for the stores table
class Store(Base):
    __tablename__ = "test__stores"

    store_id = Column(String, primary_key=True)
    timezone_str = Column(String)


# define the schema for the business hours table
class BusinessHour(Base):
    __tablename__ = "test__business_hours"

    store_id = Column(Integer, primary_key=True)
    day_of_week = Column(Integer)
    start_time_local = Column(DateTime)
    end_time_local = Column(DateTime)


class BusinessHourUTC(Base):
    __tablename__ = "test__business_hours_utc"

    store_id = Column(Integer, primary_key=True)
    day_of_week = Column(Integer)
    start_time_local = Column(DateTime)
    end_time_local = Column(DateTime)
    start_time_utc = Column(DateTime)
    end_time_utc = Column(DateTime)


# define the schema for the store status table
class StoreStatus(Base):
    __tablename__ = "test__store_status"

    store_id = Column(Integer, primary_key=True)
    timestamp_utc = Column(DateTime)
    status = Column(Boolean)


class Report(Base):
    __tablename__ = "report"

    id = Column(Integer, primary_key=True)
    store_id = Column(Integer, nullable=False)
    timestamp_utc = Column(DateTime, nullable=False)
    uptime_last_hour = Column(Integer)
    uptime_last_day = Column(Integer)
    downtime_last_hour = Column(Integer)
    downtime_last_day = Column(Integer)
    update_last_week = Column(Integer)


# create the tables in the database
# Base.metadata.create_all(engine)