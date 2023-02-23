from pydantic import BaseModel


class Store(BaseModel):
    store_id: int


class BusinessHour(BaseModel):
    store_id: int
    day_of_week: int
    start_time_local: str
    end_time_local: str


class StoreTimezone(BaseModel):
    store_id: int
    timezone_str: str


class Status(BaseModel):
    store_id: int
    timestamp_utc: str
    status: str
