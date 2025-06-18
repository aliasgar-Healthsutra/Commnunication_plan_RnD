from datetime import timedelta
import pandas as pd

def generate_schedule(start_date):
    days = [0, 3, 7, 14, 21, 30]
    months = [2, 3, 4, 6, 9, 12]
    schedule = [start_date + timedelta(days=d) for d in days]
    schedule += [(start_date.replace(day=1) + pd.DateOffset(months=m)).to_pydatetime() for m in months]
    return [d.strftime("%Y-%m-%d") for d in schedule]