# -*-coding:utf-8 -*-
"""根据企业经营类别对评论进行分地区、分时期统计"""

from datetime import datetime
from pymongo import MongoClient, ReturnDocument
from app.commontools import create_day_list, in_date


def statistics_category(citycode, startdate='2016-01-01'):
    """
    根据评价所对应的维修类别分城市分类别按天进行统计
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
         {'$project': {'_id': 0, 'companyInfo': 1, 'maintenaceInfo': 1, 'allComment': 1, 'serviceScore': 1,
                       'category': 1, 'priceScore': 1, 'qualityScore': 1, 'envirScore': 1, 'efficiencyScore': 1}}
         ])
    # 过滤目标城市的评价数据
    target_comments = []
    for comment in comments:
        if str(int(comment.get('companyInfo')[0].get('cityCode'))) == citycode:
            target_comments.append(comment)
    # 获取企业经营类别列表
    categorylist = [
        ['一类', 1],
        ['二类', 2],
        ['三类', 3],
        ['其它', 99],
    ]
    # 按照企业经营类别分类评价数据
    category_relatived_comments = {}
    for category_info in categorylist:
        temp_comment_list = []
        for tcomment in target_comments:
            if int(tcomment.get('companyInfo')[0].get('category')) == category_info[1]:
                temp_comment_list.append(tcomment)
        category_relatived_comments[(category_info[0], category_info[1])] = temp_comment_list
    # 全部数据，按照企业经营类别统计各项评价指标
    for k, v in category_relatived_comments.items():
        days = create_day_list(startdate, today)
        if len(v) == 0:  # 如果某个类别的评价数为0,则全部置为0
            for day in days:
                daily_data = {
                    'provinceCode': citycode[0:2] + '0000',
                    'cityCode': citycode,
                    'category': k[1],
                    'date': day[0],
                    'commentsQty': 0,
                    'satisfiedcommentsQty': 0,
                    'allComment': 0,
                    'serviceScore': 0,
                    'priceScore': 0,
                    'qualityScore': 0,
                    'envirScore': 0,
                    'efficiencyScore': 0,
                }
                mongo_client.statistics.category.find_one_and_update(
                    {'cityCode': citycode, 'provinceCode': citycode[0:2] + '0000', 'date': day[0], 'category': k[1]},
                    {
                        '$set': daily_data}, upsert=True, return_document=ReturnDocument.AFTER)
        else:
            for day in days:
                comments_num = 0
                satisfied_num = 0
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
                        'category': k[1],
                        'date': day[0],
                        'commentsQty': comments_num,
                        'satisfiedcommentsQty': satisfied_num,
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
                        'category': k[1],
                        'date': day[0],
                        'commentsQty': 0,
                        'satisfiedcommentsQty': 0,
                        'allComment': 0,
                        'serviceScore': 0,
                        'priceScore': 0,
                        'qualityScore': 0,
                        'envirScore': 0,
                        'efficiencyScore': 0,
                    }
                updated_data = mongo_client.statistics.category.find_one_and_update(
                    {'cityCode': citycode, 'provinceCode': citycode[0:2] + '0000', 'date': day[0],
                     'category': k[1]},
                    {
                        '$set': daily_data}, upsert=True, return_document=ReturnDocument.AFTER)
                print(updated_data)

if __name__ == '__main__':
    statistics_category('371100')
