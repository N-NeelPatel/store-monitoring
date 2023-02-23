from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List
import csv
import io
import uuid
from datetime import datetime, timedelta

from database import engine, SessionLocal
import models
import queries
import utils


models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Define input models


class ReportRequest(BaseModel):
    pass


class ReportResponse(BaseModel):
    report_id: str


class ReportStatusResponse(BaseModel):
    status: str


# Define API endpoints


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
