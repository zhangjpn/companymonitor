# -*-coding:utf-8 -*-
"""投诉量/投诉率统计"""

from pymongo import MongoClient
from datetime import datetime, timedelta
from app.base_class import CodeTable
from app.commontools import create_day_list


def statistics_complaints(citycode):
    """"""
    mongo_client = MongoClient(host='127.0.0.1', port=27017)
    today = datetime.today().strftime('%Y-%m-%d')

    # 获取某个城市的投诉数据
    complaints = mongo_client.spv1.complaints.find()
    target_complaints = []
    for complaint in complaints:
        complaint_citycode = complaint.get('cityCode')
        if complaint_citycode is not None:
            if str(int(complaint_citycode)) == citycode:
                target_complaints.append(complaint)

    # 获取辖区列表
    province_code_abbr = citycode[0:2]
    city_code_abbr = citycode[2:4]
    codetable = CodeTable()
    countylist = codetable.get_belong_county_info(province_code_abbr, city_code_abbr)  # 获取市内区域代码列表

    # 按照辖区分类评价数据
    area_relatived_complaints = {}
    for county_info in countylist:
        temp_complaint_list = []
        for tcomplaint in target_complaints:
            if str(int(tcomplaint.get('countyCode'))) == county_info[1]:
                temp_complaint_list.append(tcomplaint)
        area_relatived_complaints[(county_info[0], county_info[1])] = temp_complaint_list

    # 按照每天统计
    for k, v in area_relatived_complaints.items():
        # 生成按照天的时间段
        def in_date(dayperiod, target_date):
            """根据日期判断一个日期是否在日期时间段内"""
            if dayperiod[0] - timedelta(hours=8) <= target_date < dayperiod[1] - timedelta(hours=8):
                return True
            return False

        days = create_day_list('2015-12-01', today)
        if len(v) == 0:  # 如果某个地区的投诉为0,则全部置为0
            for day in days:
                daily_data = {
                    'statsType': 1,  # 统计类型 1-按照分区
                    'cityCode': citycode,
                    'countyCode': k[1],  # 辖区代码
                    'date': day[0],
                    'complaintQty': 0,  # 投诉量
                }
                print('按照日统计：', daily_data)
                mongo_client.statistics.complaintsstatistics.replace_one(
                    {'cityCode': citycode, 'statsType': 1, 'date': day[0], 'countyCode': k[1]},
                    daily_data, upsert=True)
        else:
            for day in days:
                count = 0  # 记数
                for comlaint in v:
                    if in_date(day, comlaint.get('created')):
                        count += 1
                if count > 0:
                    daily_data = {
                        'statsType': 1,  # 统计类型 1-按照分区
                        'cityCode': citycode,
                        'countyCode': k[1],  # 辖区代码
                        'date': day[0],
                        'complaintQty': count,  # 投诉量
                    }
                else:
                    daily_data = {
                        'statsType': 1,  # 统计类型 1-按照分区
                        'cityCode': citycode,
                        'countyCode': k[1],  # 辖区代码
                        'date': day[0],
                        'complaintQty': 0,  # 投诉量
                    }
                print('按照日统计：', daily_data)
                mongo_client.statistics.complaintsstatistics.replace_one(
                    {'cityCode': citycode, 'statsType': 1, 'date': day[0], 'countyCode': k[1]},
                    daily_data, upsert=True)


if __name__ == '__main__':
    statistics_complaints('371100')
