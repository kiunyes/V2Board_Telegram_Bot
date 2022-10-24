import pytz
import datetime
import time
ts = 1666454400
timezone = pytz.timezone('Asia/Shanghai')
def getTodayTimestemp():
    return datetime.datetime.fromtimestamp(ts,timezone).strftime(
        "%Y-%m-%d %H:%M:%S")
print(getTodayTimestemp())