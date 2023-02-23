from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker

# create the engine and connect to the SQLite database
engine = create_engine("sqlite:///loop.db")

# create a base class for declarative models
Base = declarative_base()

# define the schema for the stores table
class Store(Base):
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    timezone_str = Column(String)


# define the schema for the business hours table
class BusinessHour(Base):
    __tablename__ = "business_hours"

    id = Column(Integer, primary_key=True)
    store_id = Column(Integer)
    day_of_week = Column(Integer)
    start_time_local = Column(DateTime)
    end_time_local = Column(DateTime)


# define the schema for the store status table
class StoreStatus(Base):
    __tablename__ = "store_status"

    id = Column(Integer, primary_key=True)
    store_id = Column(Integer)
    timestamp_utc = Column(DateTime)
    status = Column(Boolean)


# create the tables in the database
Base.metadata.create_all(engine)

# create a sessionmaker to create sessions
Session = sessionmaker(bind=engine)
