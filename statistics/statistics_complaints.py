# -*-coding:utf-8 -*-
"""投诉量/投诉率统计"""

from pymongo import MongoClient, ReturnDocument
from datetime import datetime
from app.base_class import CodeTable
from app.commontools import create_day_list, in_date


def statistics_complaints(citycode, startdate='2016-01-01'):
    """

    :param startdate: 统计开始的日期 '2016-01-01'
    :param citycode: 城市代码 '371100'
    :return: None
    """
    mongo_client = MongoClient(host='127.0.0.1', port=27017)
    today = datetime.today().strftime('%Y-%m-%d')

    # 获取某个城市的投诉数据
    complaints = mongo_client.spv1.complaints.find({}, {'_id': 0, 'provinceCode': 1, 'cityCode': 1, 'countyCode': 1})
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
            county_code = tcomplaint.get('countyCode')
            if county_code is not None:
                if str(int(county_code)) == county_info[1]:
                    temp_complaint_list.append(tcomplaint)
        area_relatived_complaints[(county_info[0], county_info[1])] = temp_complaint_list

    # 按照每天统计
    for k, v in area_relatived_complaints.items():
        # 生成按照天的时间段

        days = create_day_list(startdate, today)
        if len(v) == 0:  # 如果某个地区的投诉为0,则全部置为0
            for day in days:
                daily_data = {
                    'provinceCode': citycode[0:2] + '0000',
                    'cityCode': citycode,
                    'countyCode': k[1],  # 辖区代码
                    'date': day[0],
                    'complaintQty': 0,  # 投诉量
                }
                print('按照日统计：', daily_data)
                mongo_client.statistics.maintenacesstatistics.find_one_and_update(
                    {'cityCode': citycode, 'provinceCode': citycode[0:2] + '0000', 'date': day[0], 'countyCode': k[1]},
                    {
                        '$set': daily_data}, upsert=True, return_document=ReturnDocument.AFTER)
        else:
            for day in days:
                count = 0  # 记数
                for comlaint in v:
                    if in_date(day, comlaint.get('created')):
                        count += 1
                if count > 0:
                    daily_data = {
                        'provinceCode': citycode[0:2] + '0000',
                        'cityCode': citycode,
                        'countyCode': k[1],  # 辖区代码
                        'date': day[0],
                        'complaintQty': count,  # 投诉量
                    }
                else:
                    daily_data = {
                        'provinceCode': citycode[0:2] + '0000',
                        'cityCode': citycode,
                        'countyCode': k[1],  # 辖区代码
                        'date': day[0],
                        'complaintQty': 0,  # 投诉量
                    }
                print('按照日统计：', daily_data)
                mongo_client.statistics.maintenacesstatistics.find_one_and_update(
                    {'cityCode': citycode, 'provinceCode': citycode[0:2] + '0000', 'date': day[0], 'countyCode': k[1]},
                    {
                        '$set': daily_data}, upsert=True, return_document=ReturnDocument.AFTER)

if __name__ == '__main__':
    statistics_complaints('371100')
