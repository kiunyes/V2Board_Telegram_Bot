import pytz
import datetime
import time
import datetime
import calendar

timezone = pytz.timezone('Asia/Shanghai')

def getTodayTimestemp():
    yesterday = (datetime.datetime.now(timezone) -
                 datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    inconvert = datetime.datetime.strptime(yesterday, "%Y-%m-%d")
    timestemp = int(calendar.timegm(inconvert.timetuple())-28800)
    return timestemp


print(getTodayTimestemp())

today_date = 1668096000
ltime = time.gmtime(today_date+28800)
today_date = time.strftime("%Y-%m-%d", ltime)

print(today_date)