# test_fetch.py
from app.app import fetch_demand_data
import datetime

df = fetch_demand_data(
    "Península",
    "Real",
    datetime.date(2026, 7, 1),
    datetime.date(2026, 7, 10),
)

print(df["time.datetime_utc"].head())
print(df.columns)
print(df.shape)