# -*-coding:utf-8 -*-
"""统计维修单"""

from pymongo import MongoClient, ReturnDocument
from datetime import datetime, timedelta
from app.base_class import CodeTable
from app.commontools import create_day_list, in_date


def statistics_maintenaces(citycode, startdate='2016-01-01'):
    """

    :param startdate: 统计开始的日期 '2016-01-01'
    :param citycode: 城市代码
    :return: None
    """
    mongo_client = MongoClient(host='127.0.0.1', port=27017)
    today = datetime.today().strftime('%Y-%m-%d')

    # 获取某个城市的维修单数据
    maintenaces = mongo_client.spv1.maintenaces.aggregate(
        [
            {'$lookup': {'from': 'companies', 'localField': 'companyId', 'foreignField': '_id', 'as': 'company'}},
            {'$project': {'_id': 0, 'company': 1}}
        ])
    target_maintenaces = []
    for maintenace in maintenaces:
        if str(int(maintenace.get('company')[0].get('cityCode'))) == citycode:
            target_maintenaces.append(maintenace)

    # 获取辖区列表
    province_code_abbr = citycode[0:2]
    city_code_abbr = citycode[2:4]
    codetable = CodeTable()
    countylist = codetable.get_belong_county_info(province_code_abbr, city_code_abbr)  # 获取市内区域代码列表

    # 按照辖区分类维修数据
    area_relatived_maintenaces = {}
    for county_info in countylist:
        temp_maintenace_list = []
        for tmaintenace in target_maintenaces:
            if str(int(tmaintenace.get('company')[0].get('countyCode'))) == county_info[1]:
                temp_maintenace_list.append(tmaintenace)
        area_relatived_maintenaces[(county_info[0], county_info[1])] = temp_maintenace_list

    # 按照每天统计
    for k, v in area_relatived_maintenaces.items():
        # 生成按照天的时间段
        days = create_day_list(startdate, today)
        if len(v) == 0:  # 如果某个地区的投诉为0,则全部置为0
            for day in days:
                daily_data = {
                    'provinceCode': citycode[0:2] + '0000',
                    'cityCode': citycode,
                    'countyCode': k[1],  # 辖区代码
                    'date': day[0],
                    'maintenaceQty': 0,  # 维修量
                }

                updated_data = mongo_client.statistics.maintenacesstatistics.find_one_and_update(
                    {'cityCode': citycode, 'provinceCode': citycode[0:2] + '0000', 'date': day[0], 'countyCode': k[1]},
                    {
                        '$set': daily_data}, upsert=True, return_document=ReturnDocument.AFTER)
                print(updated_data)
        else:
            for day in days:
                count = 0  # 记数
                for maintenace in v:
                    if in_date(day, maintenace.get('created')):
                        count += 1
                if count > 0:
                    daily_data = {
                        'provinceCode': citycode[0:2] + '0000',
                        'cityCode': citycode,
                        'countyCode': k[1],  # 辖区代码
                        'date': day[0],
                        'maintenaceQty': count,  # 维修单量
                    }
                else:
                    daily_data = {
                        'provinceCode': citycode[0:2] + '0000',
                        'cityCode': citycode,
                        'countyCode': k[1],  # 辖区代码
                        'date': day[0],
                        'maintenaceQty': 0,  # 维修单量
                    }
                updated_data = mongo_client.statistics.maintenacesstatistics.find_one_and_update(
                    {'cityCode': citycode, 'provinceCode': citycode[0:2] + '0000', 'date': day[0], 'countyCode': k[1]},
                    {
                        '$set': daily_data}, upsert=True, return_document=ReturnDocument.AFTER)
                print(updated_data)

if __name__ == '__main__':
    statistics_maintenaces('371100')
