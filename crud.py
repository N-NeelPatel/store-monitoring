from typing import List, Tuple
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from pytz import timezone
from schema import Store, BusinessHour, StoreTimezone, Status


def get_stores(session: Session) -> List[Store]:
    """Get a list of all stores"""
    return session.query(Store).all()


def get_business_hours(session: Session, store_id: int) -> List[BusinessHour]:
    """Get the business hours for a store"""
    return session.query(BusinessHour).filter(BusinessHour.store_id == store_id).all()


def get_store_timezone(session: Session, store_id: int) -> StoreTimezone:
    """Get the timezone for a store"""
    return (
        session.query(StoreTimezone).filter(StoreTimezone.store_id == store_id).first()
    )


def get_latest_status(
    session: Session, store_id: int, timestamp: datetime
) -> Tuple[Status, datetime]:
    """
    Get the latest status for a store before the given timestamp.

    Returns a tuple of the latest status and the timestamp of that status.
    """
    latest_status = (
        session.query(Status)
        .filter(Status.store_id == store_id, Status.timestamp_utc <= timestamp)
        .order_by(Status.timestamp_utc.desc())
        .first()
    )

    if latest_status is None:
        # Store has no status data before given timestamp
        return None, None

    return latest_status, latest_status.timestamp_utc


def get_previous_status(
    session: Session, store_id: int, timestamp: datetime
) -> Tuple[Status, datetime]:
    """
    Get the previous status for a store before the given timestamp.

    Returns a tuple of the previous status and the timestamp of that status.
    """
    previous_status = (
        session.query(Status)
        .filter(Status.store_id == store_id, Status.timestamp_utc < timestamp)
        .order_by(Status.timestamp_utc.desc())
        .first()
    )

    if previous_status is None:
        # Store has no status data before given timestamp
        return None, None

    return previous_status, previous_status.timestamp_utc


def get_statuses_between(
    session: Session, store_id: int, start_time: datetime, end_time: datetime
) -> List[Status]:
    """Get all the statuses for a store between the given times"""
    return (
        session.query(Status)
        .filter(
            Status.store_id == store_id,
            Status.timestamp_utc >= start_time,
            Status.timestamp_utc < end_time,
        )
        .all()
    )


def get_statuses_between_local(
    session: Session,
    store_id: int,
    start_time_local: datetime,
    end_time_local: datetime,
) -> List[Tuple[Status, datetime]]:
    """
    Get all the statuses for a store between the given local times.

    Returns a list of tuples, where the first element is the status and the second element is the timestamp of that status.
    """
    store_timezone = get_store_timezone(session, store_id)
    timezone_obj = timezone(store_timezone.timezone_str)

    # Convert local times to UTC times
    start_time_utc = timezone_obj.localize(start_time_local).astimezone(timezone("UTC"))
    end_time_utc = timezone_obj.localize(end_time_local).astimezone(timezone("UTC"))

    # Get all the statuses between the UTC times
    statuses = get_statuses_between(session, store_id, start_time_utc, end_time_utc)

    # Convert the timestamps back to local times and return as a list of tuples
    return [(s, s.timestamp_utc.astimezone(timezone_obj)) for s in statuses]
