# -*-codint:utf-8 -*-# -*-coding:utf-8 -*-
"""根据车辆类型对评论进行分车辆类型进行统计"""

from pymongo import MongoClient, ReturnDocument
from datetime import datetime, timedelta
from app.commontools import create_week_list, create_month_list, create_season_list, create_day_list, in_date


def statistics_vehicletype(citycode, startdate='2016-01-01'):
    """

    :param startdate: 统计开始的日期 '2016-01-01'
    :param citycode: 城市代码
    :return: None
    """
    mongo_client = MongoClient(host='127.0.0.1', port=27017)
    today = datetime.today().strftime('%Y-%m-%d')

    # 获取所有评价
    comments = mongo_client.spv1.comments.aggregate(
        [{'$match': {'status': 1}},  # 过滤评论状态
         {'$lookup': {'from': 'companies', 'localField': 'company', 'foreignField': '_id',
                      'as': 'companyInfo'}},  # 获取城市代码
         {'$lookup': {'from': 'maintenaces', 'localField': 'maintenace', 'foreignField': '_id',
                      'as': 'maintenaceInfo'}},  # 获取维修类型
         {'$project': {'_id': 0, 'companyInfo': 1, 'maintenaceInfo': 1, 'allComment': 1, 'serviceScore': 1,
                       'priceScore': 1, 'qualityScore': 1, 'envirScore': 1, 'efficiencyScore': 1}}
         ])

    # 过滤某个城市的维修单数据
    target_comments = []
    for comment in comments:
        if str(int(comment.get('companyInfo')[0].get('cityCode'))) == citycode:
            target_comments.append(comment)

    # 获取车辆类型列表
    vehicletypelist = [
        ['小型车', 1],
        ['大中型客车', 2],
        ['大型货车', 3],
        ['其它', 9],
    ]
    # 按照车辆类型分类评价数据
    vehicletype_relatived_comments = {}
    for vehicletype_info in vehicletypelist:
        temp_comment_list = []
        for tcomment in target_comments:
            if int(tcomment.get('maintenaceInfo')[0].get('vehicleType')) == vehicletype_info[1]:
                temp_comment_list.append(tcomment)
        vehicletype_relatived_comments[(vehicletype_info[0], vehicletype_info[1])] = temp_comment_list
    # 全部数据，按照车辆类型统计各项评价指标
    for k, v in vehicletype_relatived_comments.items():
        days = create_day_list(startdate, today)
        if len(v) == 0:  # 如果某个地区的投诉为0,则全部置为0
            for day in days:
                daily_data = {
                    'provinceCode': citycode[0:2] + '0000',
                    'cityCode': citycode,
                    'vehicleType': k[1],  # 车辆类型
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
                mongo_client.statistics.vehicletype.find_one_and_update(
                    {'cityCode': citycode, 'provinceCode': citycode[0:2] + '0000', 'date': day[0], 'vehicleType': k[1]},
                    {
                        '$set': daily_data}, upsert=True, return_document=ReturnDocument.AFTER)
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
                        'vehicleType': k[1],  # 品牌
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
                        'vehicleType': k[1],  # 品牌
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
                updated_data = mongo_client.statistics.vehicletype.find_one_and_update(
                    {'cityCode': citycode, 'provinceCode': citycode[0:2] + '0000', 'date': day[0],
                     'vehicleType': k[1]},
                    {
                        '$set': daily_data}, upsert=True, return_document=ReturnDocument.AFTER)
                print(updated_data)
if __name__ == '__main__':
    statistics_vehicletype('371100')
