# -*-coding:utf-8 -*-
"""统计维修单"""

from pymongo import MongoClient, ReturnDocument
from datetime import datetime
from app.commontools import create_day_list, in_date


def statistics_vehiclebrand(citycode, startdate='2016-01-01'):
    """

    :param startdate: 统计开始的日期 '2016-01-01'
    :param citycode: 城市代码
    :return: None
    """
    mongo_client = MongoClient(host='127.0.0.1', port=27017)
    today = datetime.today().strftime('%Y-%m-%d')

    comments = mongo_client.spv1.comments.aggregate(
        [{'$lookup': {'from': 'companies', 'localField': 'company', 'foreignField': '_id',
                      'as': 'companyInfo'}},
         {'$lookup': {'from': 'maintenaces', 'localField': 'maintenace', 'foreignField': '_id',
                      'as': 'maintenaceInfo'}},
         {'$project': {'_id': 0, 'companyInfo': 1, 'maintenaceInfo': 1, 'allComment': 1, 'serviceScore': 1,
                       'priceScore': 1, 'qualityScore': 1, 'envirScore': 1, 'efficiencyScore': 1}}
         ])
    # 过滤某个城市的维修单数据
    target_comments = []
    for comment in comments:
        if str(int(comment.get('companyInfo')[0].get('cityCode'))) == citycode:
            target_comments.append(comment)

    # 获取所有车辆的品牌列表
    vehiclebrandlist = mongo_client.spv1.maintenaces.distinct('vehicleBrand')

    # 按照品牌分类评价数据
    brand_relatived_comments = {}
    for brand in vehiclebrandlist:
        temp_comments_list = []
        for tcomment in target_comments:
            if str(tcomment.get('maintenaceInfo')[0].get('vehicleBrand')) == brand:
                temp_comments_list.append(tcomment)
                brand_relatived_comments[brand] = temp_comments_list

    # 按照每天统计
    for k, v in brand_relatived_comments.items():
        # 生成按照天的时间段
        days = create_day_list(startdate, today)
        if len(v) == 0:  # 如果某个地区的投诉为0,则全部置为0
            for day in days:
                daily_data = {
                    'provinceCode': citycode[0:2] + '0000',
                    'cityCode': citycode,
                    'vehicleBrand': k,  # 品牌
                    'date': day[0],
                    'commentsQty': 0,  # 维修量
                    'satisfiedcommentsQty': 0,  # 满意评价数
                    'allComment': 0,
                    'serviceScore': 0,
                    'priceScore': 0,
                    'qualityScore': 0,
                    'envirScore': 0,
                    'efficiencyScore': 0
                }

                updated_data = mongo_client.statistics.vehiclebrand.find_one_and_update(
                    {'cityCode': citycode, 'provinceCode': citycode[0:2] + '0000', 'date': day[0], 'vehicleBrand': k},
                    {
                        '$set': daily_data}, upsert=True, return_document=ReturnDocument.AFTER)
                print(updated_data)
        else:
            for day in days:
                comments_num = 0  # 总数计数
                satisfied_num = 0  # 满意评论计数
                service_score = 0,
                price_score = 0,
                quality_score = 0,
                envir_score = 0,
                efficiency_score = 0
                all_comment = 0,
                # 统计各项指标
                for comment in v:
                    if in_date(day, comment.get('created')):
                        comments_num += 1
                        allc = comment.get('allComment')
                        if allc and isinstance(allc, (int, float)):
                            if allc >= 2:
                                satisfied_num += 1
                        service_score += comment.get('serviceScore'),
                        price_score += comment.get('priceScore'),
                        quality_score += comment.get('serviceScore'),
                        envir_score += comment.get('envirScore'),
                        efficiency_score += comment.get('efficiencyScore'),
                        all_comment += comment.get('allComment'),
                if comments_num > 0:
                    daily_data = {
                        'provinceCode': citycode[0:2] + '0000',
                        'cityCode': citycode,
                        'vehicleBrand': k,  # 品牌
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
                        'vehicleBrand': k,  # 品牌
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
                updated_data = mongo_client.statistics.vehiclebrand.find_one_and_update(
                    {'cityCode': citycode, 'provinceCode': citycode[0:2] + '0000', 'date': day[0],
                     'vehicleBrand': k},
                    {
                        '$set': daily_data}, upsert=True, return_document=ReturnDocument.AFTER)
                print(updated_data)

if __name__ == '__main__':
    statistics_vehiclebrand('371100')
