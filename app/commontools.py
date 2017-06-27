# -*-coding:utf-8 -*-
from datetime import datetime, timedelta
import calendar

from scripts.tz import UTC

def create_week_list(start, end):
    """返回日期段内的周列表"""
    startday = datetime.strptime(start, '%Y-%m-%d')
    endday = datetime.strptime(end, '%Y-%m-%d')
    bias = calendar.weekday(startday.year, startday.month, startday.day)
    start_week_day = datetime(startday.year, startday.month, startday.day, tzinfo=UTC(8)) - timedelta(bias)
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

    start_month_day = datetime(startday.year, startday.month, day=1, tzinfo=UTC(8))
    in_next_month = start_month_day + timedelta(days=31)
    end_month_day = datetime(in_next_month.year, month=in_next_month.month, day=1, tzinfo=UTC(8)) - timedelta(days=1)
    month_range_list = []
    while True:
        month_range_list.append((start_month_day, end_month_day))
        if end_month_day >= endday:
            break
        start_month_day = end_month_day + timedelta(days=1)
        tempdate = start_month_day + timedelta(days=31)
        end_month_day = datetime(tempdate.year, month=tempdate.month, day=1, tzinfo=UTC(8)) - timedelta(days=1)
    return month_range_list


def create_season_list(start, end):
    """生成日期区间的所有季度的起始，终止日的列表"""
    startday = datetime.strptime(start, '%Y-%m-%d')
    endday = datetime.strptime(end, '%Y-%m-%d')

    # 获取第一季度首日
    if startday.month in [1, 2, 3]:
        start_season_day = datetime(startday.year, 1, day=1, tzinfo=UTC(8))
    elif startday.month in [4, 5, 6]:
        start_season_day = datetime(startday.year, 4, day=1, tzinfo=UTC(8))
    elif startday.month in [7, 8, 9]:
        start_season_day = datetime(startday.year, 7, day=1, tzinfo=UTC(8))
    else:
        start_season_day = datetime(startday.year, 10, day=1, tzinfo=UTC(8))

    # 获取当季度最后一天
    temdate = start_season_day + timedelta(days=93)
    end_season_day = datetime(temdate.year, temdate.month, 1, tzinfo=UTC(8)) - timedelta(days=1)

    season_range_list = []
    while True:
        season_range_list.append((start_season_day, end_season_day))
        if end_season_day >= endday:
            break
        start_season_day = end_season_day + timedelta(days=1)
        tempdate = start_season_day + timedelta(days=93)
        end_season_day = datetime(tempdate.year, month=tempdate.month, day=1, tzinfo=UTC(8)) - timedelta(days=1)
    return season_range_list


def get_last_month_period(theday):
    """获取上个月的日期范围，返回（起始日，结束日）元组"""
    if theday.month == 1:
        start_month_day = datetime(theday.year - 1, 12, 1, tzinfo=UTC(8))
        end_month_day = datetime(theday.year, 1, 1, tzinfo=UTC(8)) - timedelta(days=1)
    else:
        start_month_day = datetime(theday.year, theday.month - 1, 1, tzinfo=UTC(8))
        end_month_day = datetime(theday.year, theday.month, 1, tzinfo=UTC(8)) - timedelta(days=1)
    return start_month_day, end_month_day
def get_last_n_month_period(theday, n=7):
    """获取过去n个月的时间段"""
    if theday.month > n:
        if theday.month < 12:
            start = datetime(theday.year, theday.month - n, 1, tzinfo=UTC(8))
            end = datetime(theday.year, theday.month + 1,1, tzinfo=UTC(8)) - timedelta(days=1)
        else:
            pass
    else:
        start = datetime(theday.year - 1, 12-theday.month+n,1,tzinfo=UTC(8))

    return start,end

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
        end_season_day = datetime(start_season_day.year, 12, 31, tzinfo=UTC(8))
    elif start_season_day.month == 1:
        end_season_day = datetime(start_season_day.year, 3, 31, tzinfo=UTC(8))
    elif start_season_day.month == 4:
        end_season_day = datetime(start_season_day.year, 6, 30, tzinfo=UTC(8))
    else:
        end_season_day = datetime(start_season_day.year, 9, 30, tzinfo=UTC(8))
    return start_season_day, end_season_day

if __name__ == '__main__':
    # create_season_list('2016-06-09', '2017-07-04')
    a,b = get_last_month_period(datetime.now())
    print(a,b)
