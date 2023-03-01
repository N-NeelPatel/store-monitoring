import pytz
import pandas as pd
from datetime import datetime, timedelta, time
import csv
from collections import defaultdict
import numpy as np


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

business_hours_df["start_time_utc"] = pd.to_datetime(
    business_hours_df["start_time_utc"]
)
business_hours_df["end_time_utc"] = pd.to_datetime(business_hours_df["end_time_utc"])

# read the csv data
df = pd.read_csv("store_status.csv")
# convert timestamp_utc column to pandas datetime format
df["timestamp_utc"] = pd.to_datetime(df["timestamp_utc"])
df["time"] = pd.to_datetime(df["timestamp_utc"]).dt.date


# get the current timestamp
current_time = df["timestamp_utc"].max()
current_time_only = df["time"].max()

df["day"] = df["timestamp_utc"].dt.dayofweek


df = pd.merge(
    df,
    business_hours_df,
    how="left",
    left_on=["store_id"],
    right_on=["store_id"],
)
df["time"] = df["timestamp_utc"].dt.time
df["start_time_only"] = df["start_time_utc"].dt.time
df["end_time_only"] = df["end_time_utc"].dt.time

df["day_y"] = df["day_y"].astype("Int64")
df = df.query("day_x == day_y")
df = df[(df["time"] >= df["start_time_only"]) & (df["time"] < df["end_time_only"])]

# print(df)

df.to_csv("filtered_data.csv")


# read in data
data = pd.read_csv("filtered_data.csv")

# convert timestamp_utc and start_time_utc/end_time_utc to datetime objects
data["timestamp_utc"] = pd.to_datetime(data["timestamp_utc"], utc=True)
data["start_time_utc"] = pd.to_datetime(data["start_time_utc"], utc=True)
data["end_time_utc"] = pd.to_datetime(data["end_time_utc"], utc=True)

# create new columns for hour, day, and week
data["hour"] = data["timestamp_utc"].dt.hour
data["day"] = data["timestamp_utc"].dt.day
data["week"] = data["timestamp_utc"].dt.isocalendar().week

# create new column for current status of each store
data["current_status"] = data.groupby("store_id")["status"].transform("last")

# filter to only include rows where store is currently active
active_data = data[data["current_status"] == "active"]

# get list of active stores
active_stores = pd.DataFrame(active_data["store_id"].unique(), columns=["store_id"])

# initialize parameters for each active store
active_stores["uptime_last_hour"] = 0
active_stores["uptime_last_day"] = 0
active_stores["uptime_last_week"] = 0
active_stores["downtime_last_hour"] = 0
active_stores["downtime_last_day"] = 0
active_stores["downtime_last_week"] = 0

# create business hours time range
business_hours = pd.date_range("00:00", "23:59", freq="15min").time

# loop through each active store
for store in active_stores["store_id"]:
    # filter to only include data for current store
    store_data = active_data[active_data["store_id"] == store]
    # create new DataFrame to hold uptime and downtime for each 15-minute interval
    store_uptime = pd.DataFrame(index=business_hours)
    store_downtime = pd.DataFrame(index=business_hours)

    # calculate uptime and downtime for last hour, day, and week
    store_uptime_last_hour = (
        store_data[store_data["timestamp_utc"] >= current_time - pd.Timedelta("1H")][
            "status"
        ]
        .value_counts(normalize=True)
        .get("active", 0)
        * 60
    )
    store_uptime_last_day = (
        store_data[store_data["day"] == pd.Timestamp.utcnow().tz_localize(None).day][
            "status"
        ]
        .value_counts(normalize=True)
        .get("active", 0)
        * 24
    )
    store_uptime_last_week = (
        store_data[store_data["week"] == pd.Timestamp.utcnow().tz_localize(None).week][
            "status"
        ]
        .value_counts(normalize=True)
        .get("active", 0)
        * 24
        * 7
    )
    store_downtime_last_hour = 60 - store_uptime_last_hour
    store_downtime_last_day = 24 - store_uptime_last_day
    store_downtime_last_week = (24 * 7) - store_uptime_last_week

    # loop through each 15-minute interval in business hours
    for interval in business_hours:
        # get start and end times for current interval
        # current_date = pd.Timestamp.utcnow().tz_localize(None).date()
        # print("timestamp", current_time.)
        # print((current_time_only), interval)
        start_time = pd.Timestamp.combine(current_time_only, interval).tz_localize(
            "UTC"
        )
        end_time = start_time + pd.Timedelta("15min")

        # convert start and end times to datetime64[ns, UTC] objects
        start_time = pd.to_datetime(start_time)
        end_time = pd.to_datetime(end_time)

        # filter to only include data for current interval
        interval_data = store_data[
            (store_data["timestamp_utc"] >= start_time)
            & (store_data["timestamp_utc"] < end_time)
        ]

        # calculate uptime and downtime for current interval
        interval_uptime = interval_data[interval_data["status"] == "active"][
            "status"
        ].count()
        interval_downtime = interval_data[interval_data["status"] == "inactive"][
            "status"
        ].count()

        # add interval uptime and downtime to store uptime and downtime DataFrames
        store_uptime[interval] = interval_uptime
        store_downtime[interval] = interval_downtime

    # interpolate missing values in store uptime and downtime DataFrames
    store_uptime_interpolated = store_uptime.interpolate(method="linear")
    store_downtime_interpolated = store_downtime.interpolate(method="linear")

    # calculate total uptime and downtime for each active store
    active_stores["total_uptime"] = store_uptime_interpolated.sum(axis=1)
    active_stores["total_downtime"] = store_downtime_interpolated.sum(axis=1)

    # calculate uptime and downtime for last hour, day, and week by summing appropriate intervals
    active_stores["uptime_last_hour"] = store_uptime_interpolated.iloc[-4:].sum().sum()
    active_stores["uptime_last_day"] = store_uptime_interpolated.iloc[-96:].sum().sum()
    active_stores["uptime_last_week"] = (
        store_uptime_interpolated.iloc[-672:].sum().sum()
    )
    active_stores["downtime_last_hour"] = (
        store_downtime_interpolated.iloc[-4:].sum().sum()
    )
    active_stores["downtime_last_day"] = (
        store_downtime_interpolated.iloc[-96:].sum().sum()
    )
    active_stores["downtime_last_week"] = (
        store_downtime_interpolated.iloc[-672:].sum().sum()
    )

# display results
print(active_stores)

active_stores.to_csv("results.csv")
