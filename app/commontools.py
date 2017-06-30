# -*-coding:utf-8 -*-
from datetime import datetime, timedelta
import calendar


def str_to_date(string=None):
    if not isinstance(string, str):
        return None
    string = string.strip()
    try:
        res = datetime.strptime(string, '%Y.%m.%d')
        return res
    except ValueError:
        try:
            res = datetime.strptime(string, '%Y-%m-%d')
            return res
        except ValueError:
            pass
    return None


def in_date(dayperiod, target_date):
    """根据日期判断一个日期是否在日期时间段内"""
    if not target_date:
        return False
    if dayperiod[0] - timedelta(hours=8) <= target_date < dayperiod[1] - timedelta(hours=8):
        return True
    return False


def in_week(weekperiod, target_date):
    """根据日期判断一个日期是否在日期时间段内"""
    if weekperiod[0] - timedelta(hours=8) <= target_date < (
                    weekperiod[1] + timedelta(days=1) - timedelta(hours=8)):
        return True
    return False


def in_month(monthperiod, target_date):
    """根据日期判断一个日期是否在日期时间段内"""
    if monthperiod[0] - timedelta(hours=8) <= target_date < (
                    monthperiod[1] + timedelta(days=1) - timedelta(hours=8)):
        return True
    return False


def in_season(seasonperiod, target_date):
    """根据日期判断一个日期是否在日期时间段内"""
    if seasonperiod[0] - timedelta(hours=8) <= target_date < (
                    seasonperiod[1] + timedelta(days=1) - timedelta(hours=8)):
        return True
    return False


def create_week_list(start, end):
    """返回日期段内的周列表"""
    startday = datetime.strptime(start, '%Y-%m-%d')
    temp = datetime.strptime(end, '%Y-%m-%d')
    endday = datetime(temp.year, temp.month, temp.day, tzinfo=None)
    bias = calendar.weekday(startday.year, startday.month, startday.day)
    start_week_day = datetime(startday.year, startday.month, startday.day, tzinfo=None) - timedelta(bias)
    week_range_list = []
    end_week_day = start_week_day + timedelta(days=6)
    while True:
        week_range_list.append((start_week_day, end_week_day))
        start_week_day += timedelta(days=7)
        if end_week_day >= endday:
            break
        end_week_day = start_week_day + timedelta(days=6)
    return week_range_list


def create_month_list(start, end):
    startday = datetime.strptime(start, '%Y-%m-%d')
    endday = datetime.strptime(end, '%Y-%m-%d')

    start_month_day = datetime(startday.year, startday.month, day=1, tzinfo=None)
    in_next_month = start_month_day + timedelta(days=31)
    end_month_day = datetime(in_next_month.year, month=in_next_month.month, day=1, tzinfo=None) - timedelta(days=1)
    month_range_list = []
    while True:
        month_range_list.append((start_month_day, end_month_day))
        if end_month_day >= endday:
            break
        start_month_day = end_month_day + timedelta(days=1)
        tempdate = start_month_day + timedelta(days=31)
        end_month_day = datetime(tempdate.year, month=tempdate.month, day=1, tzinfo=None) - timedelta(days=1)
    return month_range_list


def create_season_list(start, end):
    """生成日期区间的所有季度的起始，终止日的列表"""
    startday = datetime.strptime(start, '%Y-%m-%d')
    endday = datetime.strptime(end, '%Y-%m-%d')

    # 获取第一季度首日
    if startday.month in [1, 2, 3]:
        start_season_day = datetime(startday.year, 1, day=1, tzinfo=None)
    elif startday.month in [4, 5, 6]:
        start_season_day = datetime(startday.year, 4, day=1, tzinfo=None)
    elif startday.month in [7, 8, 9]:
        start_season_day = datetime(startday.year, 7, day=1, tzinfo=None)
    else:
        start_season_day = datetime(startday.year, 10, day=1, tzinfo=None)

    # 获取当季度最后一天
    temdate = start_season_day + timedelta(days=93)
    end_season_day = datetime(temdate.year, temdate.month, 1, tzinfo=None) - timedelta(days=1)

    season_range_list = []
    while True:
        season_range_list.append((start_season_day, end_season_day))
        if end_season_day >= endday:
            break
        start_season_day = end_season_day + timedelta(days=1)
        tempdate = start_season_day + timedelta(days=93)
        end_season_day = datetime(tempdate.year, month=tempdate.month, day=1, tzinfo=None) - timedelta(days=1)
    return season_range_list


def create_day_list(start, end):
    """生成日列表"""
    startday = datetime.strptime(start, '%Y-%m-%d')
    endday = datetime.strptime(end, '%Y-%m-%d')
    res = []
    # (a, b)
    a = startday
    b = a + timedelta(days=1)
    while True:
        if b > endday:
            break
        res.append((a, b))
        a = b
        b = a + timedelta(days=1)
    return res


def get_last_month_period(theday):
    """获取上个月的日期范围，返回（起始日，结束日）元组"""
    if theday.month == 1:
        start_month_day = datetime(theday.year - 1, 12, 1, tzinfo=None)
        end_month_day = datetime(theday.year - 1, 12, 31, tzinfo=None)
    else:
        start_month_day = datetime(theday.year, theday.month - 1, 1, tzinfo=None)
        end_month_day = datetime(theday.year, theday.month, 1, tzinfo=None) - timedelta(days=1)
    return start_month_day, end_month_day


def get_last_n_month_period(theday, n=7):
    """获取过去n个月的时间段"""
    start = end = theday
    if theday.month > n:
        start = datetime(theday.year, theday.month - n + 1, 1, tzinfo=None)
        if theday.month < 12:
            end = datetime(theday.year, theday.month + 1, 1, tzinfo=None) - timedelta(days=1)
        elif theday.month == 12:
            end = datetime(theday.year, 12, 31, tzinfo=None)
    else:
        start = datetime(theday.year - 1, 12 - n + theday.month + 1, 1, tzinfo=None)
        end = datetime(theday.year, theday.month + 1, 1, tzinfo=None) - timedelta(days=1)
    return start, end


def get_last_season_period(today):
    if today.month in [1, 2, 3]:
        start_season_day = datetime(today.year - 1, 10, day=1)
    elif today.month in [4, 5, 6]:
        start_season_day = datetime(today.year, 1, day=1)
    elif today.month in [7, 8, 9]:
        start_season_day = datetime(today.year, 4, day=1)
    else:
        start_season_day = datetime(today.year, 7, day=1)
    # 获取季度最后一天
    if start_season_day.month == 10:
        end_season_day = datetime(start_season_day.year, 12, 31, tzinfo=None)
    elif start_season_day.month == 1:
        end_season_day = datetime(start_season_day.year, 3, 31, tzinfo=None)
    elif start_season_day.month == 4:
        end_season_day = datetime(start_season_day.year, 6, 30, tzinfo=None)
    else:
        end_season_day = datetime(start_season_day.year, 9, 30, tzinfo=None)
    return start_season_day, end_season_day


def get_last_n_season_period(theday, n=7):
    """获取过去n个季度的时间段，返回起始时间和结束时间"""
    # 获取本季度首日日期
    if theday.month in [1, 2, 3]:
        l = [4, 1, 10, 7]
        mon = l[n % 4]
        if n > 1:
            deltayear = n // 6 + 1
        else:
            deltayear = 0
        start_season_day = datetime(theday.year - deltayear, mon, day=1, tzinfo=None)
        end_season_day = datetime(theday.year, 3, day=31, tzinfo=None)
    elif theday.month in [4, 5, 6]:
        l = [7, 4, 1, 10]
        mon = l[n % 4]
        if n > 2:
            deltayear = (n - 1) // 6 + 1
        else:
            deltayear = 0
        start_season_day = datetime(theday.year - deltayear, mon, day=1, tzinfo=None)
        end_season_day = datetime(theday.year, 6, day=30, tzinfo=None)

    elif theday.month in [7, 8, 9]:
        l = [10, 7, 4, 1]
        mon = l[n % 4]
        if n > 3:
            deltayear = (n - 2) // 6 + 1
        else:
            deltayear = 0
        start_season_day = datetime(theday.year - deltayear, mon, day=1, tzinfo=None)
        end_season_day = datetime(theday.year, 9, day=30, tzinfo=None)
    else:
        l = [1, 10, 7, 4]
        mon = l[n % 4]
        if n > 4:
            deltayear = (n - 3) // 6 + 1
        else:
            deltayear = 0
        start_season_day = datetime(theday.year - deltayear, mon, day=1, tzinfo=None)
        end_season_day = datetime(theday.year, 12, day=31, tzinfo=None)
    return start_season_day, end_season_day


if __name__ == '__main__':
    # create_season_list('2016-06-09', '2017-07-04')
    # a, b = get_last_month_period(datetime.now())
    # print(a, b)
    # today = datetime.today()
    # theday = datetime.date(datetime(2017, 12, 31))
    # s,v = get_last_n_season_period(today, n=7)
    # print(s,v)
    # get_last_n_month_period(today)

    res = create_day_list('2017-06-01', '2017-07-01')
    for i in res:
        print(i)
