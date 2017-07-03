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
    companies_cursor = mongo_client.spv1.companies.find({'cityCode': citycode})
    target_companies = [t for t in companies_cursor]

    # 获取辖区列表
    province_code_abbr = citycode[0:2]
    city_code_abbr = citycode[2:4]
    codetable = CodeTable()
    countylist = codetable.get_belong_county_info(province_code_abbr, city_code_abbr)  # 获取市内区域代码列表

    # 按照辖区分类维修企业
    area_relatived_companies = {}
    for county_info in countylist:
        temp_companies_list = []
        for tcompany in target_companies:
            if str(int(tcompany.get('company')[0].get('countyCode'))) == county_info[1]:
                temp_companies_list.append(tcompany)
        area_relatived_companies[(county_info[0], county_info[1])] = temp_companies_list

    for k, v in area_relatived_companies.items():
        days = create_day_list(startdate, today)
        for day in days:
            daily_data = {
                'provinceCode': citycode[0:2] + '0000',
                'cityCode': citycode,
                'countyCode': k[1],
                'date': day[0],
                'companiesQty': len(v),
            }
            updated_data = mongo_client.statistics.maintenacesstatistics.find_one_and_update(
                {'cityCode': citycode, 'provinceCode': citycode[0:2] + '0000', 'date': day[0], 'countyCode': k[1]},
                {
                    '$set': daily_data}, upsert=True, return_document=ReturnDocument.AFTER)
            print(updated_data)

if __name__ == '__main__':
    statistics_maintenaces('371100')
