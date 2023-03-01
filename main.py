from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List
import csv
import io
import uuid
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import engine, SessionLocal
import models
import crud
import utils
import pandas as pd
import pytz

models.Base.metadata.create_all(bind=engine)

df = pd.read_csv("timezones.csv")

try:
    df.to_sql("test__stores", engine, if_exists="replace", index=False)
except:
    print("Sorry, some error has occurred!")

df = pd.read_csv("menu_hours.csv")

try:
    df.to_sql("test__business_hours", engine, if_exists="replace", index=False)
except:
    print("Sorry, some error has occurred!")


df = pd.read_csv("store_status.csv")

try:
    df.to_sql("test__store_status", engine, if_exists="replace", index=False)
except:
    print("Sorry, some error has occurred!")


# Load timezone information from the third table
timezone_df = pd.read_csv("timezones.csv")
timezone_dict = dict(zip(timezone_df.store_id, timezone_df.timezone_str))

# Load data from the first and second tables
business_hours_df = pd.read_csv("menu_hours.csv")


# Convert time ranges in business_hours.csv to UTC
for i, row in business_hours_df.iterrows():
    store_id = row["store_id"]
    local_tz = pytz.timezone(timezone_dict.get(store_id, "America/Chicago"))

    start_time = datetime.strptime(row["start_time_local"], "%H:%M:%S").replace(
        tzinfo=local_tz
    )
    end_time = datetime.strptime(row["end_time_local"], "%H:%M:%S").replace(
        tzinfo=local_tz
    )
    start_utc = start_time.astimezone(pytz.utc).strftime("%H:%M:%S")
    end_utc = end_time.astimezone(pytz.utc).strftime("%H:%M:%S")
    business_hours_df.at[i, "start_time_utc"] = start_utc
    business_hours_df.at[i, "end_time_utc"] = end_utc


try:
    business_hours_df.to_sql(
        "test__business_hours_utc", engine, if_exists="replace", index=False
    )
except:
    print("Sorry, some error has occurred!")

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Define input models


class ReportRequest(BaseModel):
    pass


class ReportResponse(BaseModel):
    report_id: str


class ReportStatusResponse(BaseModel):
    status: str


# Define API endpoints


@app.get("/")
def home():
    return {"business_hours_df": business_hours_df}


@app.get("/get_store")
def get_store_info(db: Session = Depends(get_db)):
    # d1 = queries.get_stores(SessionLocal)
    return db


@app.post("/trigger_report", response_model=ReportResponse)
def trigger_report(request: ReportRequest):
    # Generate report ID
    report_id = str(uuid.uuid4())

    # Start report generation in background
    utils.generate_report(report_id)

    # Return report ID to user
    return {"report_id": report_id}


@app.get("/get_report/{report_id}")
def get_report(report_id: str):
    # Check if report exists
    report_path = f"reports/{report_id}.csv"
    if not utils.file_exists(report_path):
        raise HTTPException(status_code=404, detail="Report not found")

    # Check if report is complete
    status_path = f"reports/{report_id}.status"
    if not utils.file_exists(status_path):
        return {"status": "Running"}

    # Load report from file and return as CSV response
    with open(report_path, "r") as f:
        csv_text = f.read()
    return StreamingResponse(io.StringIO(csv_text), media_type="text/csv")


# Start application

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
