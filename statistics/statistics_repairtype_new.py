# -*-coding:utf-8 -*-
"""根据维修类别对评论进行分地区、分时期统计"""

from datetime import datetime
from pymongo import MongoClient, ReturnDocument
from app.commontools import create_day_list, in_date


def statistics_repairtype(citycode, startdate='2016-01-01'):
    """
    根据评价所对应的维修类别分城市分类别按天进行统计
    :param startdate: 统计开始的日期 '2016-01-01'
    :param citycode: 城市代码
    :return: None
    """
    mongo_client = MongoClient(host='127.0.0.1', port=27017)
    today = datetime.today().strftime('%Y-%m-%d')

    comments = mongo_client.spv1.comments.aggregate(
        [{'$match': {'status': 1}},
         {'$lookup': {'from': 'companies', 'localField': 'company', 'foreignField': '_id',
                      'as': 'companyInfo'}},
         {'$project': {'_id': 0, 'companyInfo': 1, 'allComment': 1, 'serviceScore': 1,
                       'repairType': 1, 'priceScore': 1, 'qualityScore': 1, 'envirScore': 1, 'efficiencyScore': 1}}
         ])
    # 过滤目标城市的评价数据
    target_comments = []
    for comment in comments:
        if str(int(comment.get('companyInfo')[0].get('cityCode'))) == citycode:
            target_comments.append(comment)

    # 获取维修类别列表
    repairtypelist = [
        ['日常维护', 10],
        ['一级维护', 20],
        ['二级维护', 30],
        ['汽车小修', 40],
        ['汽车大修', 50],
        ['总成修理', 60],
        ['零件修理', 70],
        ['其它', 90]
    ]
    # 按照维修类别分类评价数据
    repairtype_relatived_comments = {}
    for repairtype_info in repairtypelist:
        temp_comment_list = []
        for tcomment in target_comments:
            if int(tcomment.get('repairType')) == repairtype_info[1]:
                temp_comment_list.append(tcomment)
        repairtype_relatived_comments[(repairtype_info[0], repairtype_info[1])] = temp_comment_list
    # 全部数据，按照维修类别统计各项评价指标
    for k, v in repairtype_relatived_comments.items():
        # 生成按照天的时间段
        days = create_day_list(startdate, today)
        if len(v) == 0:  # 如果某个地区的投诉为0,则全部置为0
            for day in days:
                daily_data = {
                    'provinceCode': citycode[0:2] + '0000',
                    'cityCode': citycode,
                    'repairType': k[1],
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
                mongo_client.statistics.repairtype.find_one_and_update(
                    {'cityCode': citycode, 'provinceCode': citycode[0:2] + '0000', 'date': day[0], 'repairType': k[1]},
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
                        'repairType': k[1],
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
                        'repairType': k[1],
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
                updated_data = mongo_client.statistics.vehiclebrand.find_one_and_update(
                    {'cityCode': citycode, 'provinceCode': citycode[0:2] + '0000', 'date': day[0],
                     'repairType': k[1]},
                    {
                        '$set': daily_data}, upsert=True, return_document=ReturnDocument.AFTER)
                print(updated_data)


if __name__ == '__main__':
    statistics_repairtype('371100', startdate='2015-09-09')
