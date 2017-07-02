# -*-coding:utf-8 -*-
"""根据维修类别对评论进行分地区、分时期统计"""

from pymongo import MongoClient, ReturnDocument
from datetime import datetime, timedelta
from app.base_class import CodeTable
from app.commontools import create_week_list, create_month_list, create_season_list, create_day_list, in_date


def statistics_satisfaction(citycode, startdate='2016-01-01'):
    """
    :param startdate: 统计开始的日期 '2016-01-01'
    :param citycode: 城市代码
    :return: None
    """
    mongo_client = MongoClient(host='127.0.0.1', port=27017)
    today = datetime.today().strftime('%Y-%m-%d')

    # 获取某个城市的评价
    comments = mongo_client.spv1.comments.aggregate(
        [{'$match': {'status': 1}},
         {'$lookup': {'from': 'companies', 'localField': 'company', 'foreignField': '_id',
                      'as': 'companyInfo'}},
         {'$project': {'_id': 0, 'companyInfo': 1, 'allComment': 1, 'serviceScore': 1,
                       'priceScore': 1, 'qualityScore': 1, 'envirScore': 1, 'efficiencyScore': 1}}
         ])
    target_comments = []
    for comment in comments:
        if str(int(comment.get('companyInfo')[0].get('cityCode'))) == citycode:
            target_comments.append(comment)

    # 获取辖区列表
    province_code_abbr = citycode[0:2]
    city_code_abbr = citycode[2:4]
    codetable = CodeTable()
    countylist = codetable.get_belong_county_info(province_code_abbr, city_code_abbr)  # 获取市内区域代码列表

    # 按照辖区分类评价数据
    area_relatived_comments = {}
    for county_info in countylist:
        temp_comment_list = []
        for tcomment in target_comments:
            if str(int(tcomment.get('companyInfo')[0].get('countyCode'))) == county_info[1]:
                temp_comment_list.append(tcomment)
        area_relatived_comments[(county_info[0], county_info[1])] = temp_comment_list

    # 全部数据，按照维修类别统计各项评价指标
    for k, v in area_relatived_comments.items():
        days = create_day_list(startdate, today)
        if len(v) == 0:  # 如果某个地区的投诉为0,则全部置为0
            for day in days:
                daily_data = {
                    'provinceCode': citycode[0:2] + '0000',
                    'cityCode': citycode,
                    'countyCode': k[1],
                    'date': day[0],
                    'commentsQty': 0,  # 维修量
                    'satisfiedcommentsQty': 0,  # 满意评价数
                    'allComment': 0,
                    'serviceScore': 0,
                    'priceScore': 0,
                    'qualityScore': 0,
                    'envirScore': 0,
                    'efficiencyScore': 0,
                }
                updated_data = mongo_client.statistics.county.find_one_and_update(
                    {'cityCode': citycode, 'provinceCode': citycode[0:2] + '0000', 'date': day[0], 'countyCode': k[1]},
                    {
                        '$set': daily_data}, upsert=True, return_document=ReturnDocument.AFTER)
                print(updated_data)
        else:
            for day in days:
                comments_num = 0  # 总数计数
                satisfied_num = 0  # 满意评论计数
                service_score = 0
                price_score = 0
                quality_score = 0
                envir_score = 0
                efficiency_score = 0
                all_comment = 0
                # 统计各项指标
                for comment in v:
                    if in_date(day, comment.get('created')):
                        comments_num += 1
                        allc = comment.get('allComment')
                        if isinstance(allc, (int, float)):
                            if allc >= 2:
                                satisfied_num += 1
                        service_score += comment.get('serviceScore')
                        price_score += comment.get('priceScore')
                        quality_score += comment.get('serviceScore')
                        envir_score += comment.get('envirScore')
                        efficiency_score += comment.get('efficiencyScore')
                        all_comment += comment.get('allComment')
                if comments_num > 0:
                    daily_data = {
                        'provinceCode': citycode[0:2] + '0000',
                        'cityCode': citycode,
                        'countyCode': k[1],
                        'date': day[0],
                        'commentsQty': comments_num,  # 维修量
                        'satisfiedcommentsQty': satisfied_num,  # 满意评价数
                        'serviceScore': round(service_score / comments_num, 1),
                        'priceScore': round(price_score / comments_num, 1),
                        'qualityScore': round(quality_score / comments_num, 1),
                        'envirScore': round(envir_score / comments_num, 1),
                        'efficiencyScore': round(efficiency_score / comments_num, 1),
                        'allComment': round(all_comment / comments_num, 1),
                    }
                else:
                    daily_data = {
                        'provinceCode': citycode[0:2] + '0000',
                        'cityCode': citycode,
                        'countyCode': k[1],
                        'date': day[0],
                        'commentsQty': 0,  # 维修量
                        'satisfiedcommentsQty': 0,  # 满意评价数
                        'allComment': 0,
                        'serviceScore': 0,
                        'priceScore': 0,
                        'qualityScore': 0,
                        'envirScore': 0,
                        'efficiencyScore': 0,
                    }
                updated_data = mongo_client.statistics.county.find_one_and_update(
                    {'cityCode': citycode, 'provinceCode': citycode[0:2] + '0000', 'date': day[0],
                     'countyCode': k[1]},
                    {
                        '$set': daily_data}, upsert=True, return_document=ReturnDocument.AFTER)
                print(updated_data)

if __name__ == '__main__':
    statistics_satisfaction('371100')
