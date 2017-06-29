# -*-coding:utf-8 -*-
"""统计维修单"""

from pymongo import MongoClient
from datetime import datetime
from app.base_class import CodeTable
from app.commontools import create_day_list


def statistics_maintenaces(citycode):
    """"""
    mongo_client = MongoClient(host='127.0.0.1', port=27017)
    today = datetime.today().strftime('%Y-%m-%d')

    # 获取某个城市的维修单数据
    maintenaces = mongo_client.spv1.maintenaces.find()
    target_maintenaces = [maintenace for maintenace in maintenaces if maintenace.get('cityCode') == citycode]


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
            if tmaintenace.get('countyCode') == county_info[1]:
                temp_maintenace_list.append(tmaintenace)
        area_relatived_maintenaces[(county_info[0], county_info[1])] = temp_maintenace_list

    # 按照每天统计
    for k, v in area_relatived_maintenaces.items():
        # 生成按照天的时间段
        def in_date(dayperiod, target_date):
            """根据日期判断一个日期是否在日期时间段内"""
            if dayperiod[0] <= target_date < dayperiod[1]:
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
                    'maintenaceQty': 0,  # 维修量
                }
                print('按照日统计：', daily_data)
                mongo_client.statistics.maintenacesstatistics.replace_one(
                    {'cityCode': citycode, 'statsType': 1, 'date': day[0], 'countyCode': k[1]},
                    daily_data, upsert=True)
        else:
            for day in days:
                count = 0  # 记数
                for maintenace in v:
                    if in_date(day, maintenace.get('created')):
                        count += 1
                if count > 0:
                    daily_data = {
                        'statsType': 1,  # 统计类型 1-按照分区
                        'cityCode': citycode,
                        'countyCode': k[1],  # 辖区代码
                        'date': day[0],  # 唯一值
                        'maintenaceQty': count,  # 维修单量
                    }
                else:
                    daily_data = {
                        'statsType': 1,  # 统计类型 1-按照分区
                        'cityCode': citycode,
                        'countyCode': k[1],  # 辖区代码
                        'date': day[0],  # 唯一值
                        'maintenaceQty': 0,  # 维修单量  # 问题
                    }
                print('按照日统计：', daily_data)
                mongo_client.statistics.maintenacesstatistics.replace_one(
                    {'cityCode': citycode, 'statsType': 1, 'date': day[0], 'countyCode': k[1]},
                    daily_data, upsert=True)


if __name__ == '__main__':
    statistics_maintenaces('371100')
