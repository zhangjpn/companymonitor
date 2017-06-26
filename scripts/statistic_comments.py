# -*-codint:utf-8 -*-

from pymongo import MongoClient
from datetime import datetime, timedelta, tzinfo
from app.base_class import CodeTable


class UTC(tzinfo):
    """UTC时区"""

    def __init__(self, offset=0):
        self._offset = offset

    def utcoffset(self, dt):
        return timedelta(hours=self._offset)

    def tzname(self, dt):
        return "UTC +%s" % self._offset

    def dst(self, dt):
        return timedelta(hours=self._offset)


def collect_comments(stats_day, citycode):
    """获取城市的满意度数据，全部历史数据，过去一周的，过去一个月的，过去一个季度的满意度数据







    """

    mongo_client = MongoClient(host='127.0.0.1', port=27017)

    # 日期处理
    recorded_date = datetime(stats_day.year, stats_day.month, stats_day.day, hour=0, minute=0, second=0, tzinfo=UTC(0))
    localtz = UTC(8)
    start_of_day = datetime(stats_day.year, stats_day.month, stats_day.day, hour=0, minute=0, second=0, tzinfo=localtz)
    end_of_day = start_of_day + timedelta(days=1)

    # 获取某个城市的评价数
    comments_cursor = mongo_client.statistics.commentsstatistics.find({}, {'commentIds': True, '_id': False})
    comments = [i for i in comments_cursor]  # 所有评论的列表
    comments_id = []
    comment_count = 0  # 总评论数
    for comment_list in comments:
        for comment in comment_list:
            if comment.get('cityCode') == citycode:
                comments_id.append(comment.get('_id'))
                comment_count += 1

    # 获取某个城市的评价数（原始数据）
    comments = mongo_client.spv1.comments.find({'status': 1})  # ,{'_id':True,'company':True}
    target_comments = []
    comments_count = 0
    for comment in comments:  # 需要重写
        relatived_company = mongo_client.spv1.companies.find_one(comment.get('company'))
        _city_code = str(int(relatived_company.get('cityCode', 0)))
        _county_code = str(int(relatived_company.get('countyCode', 0)))
        _province_code = str(int(relatived_company.get('provinceCode', 0)))
        if _city_code == citycode:
            comment['provinceCode'] = _province_code
            comment['cityCode'] = _city_code
            comment['countyCode'] = _county_code
            target_comments.append(comment)
            comments_count += 1

    # 获取某个城市的所有好评数
    satisfied_count = 0
    for tcomment in target_comments:
        if tcomment.get('allComment') >= 2:
            satisfied_count += 1
    # 总体满意度
    total_satisfied_rate = round(satisfied_count / comments_count, 3)  # 小数

    # 按照分区统计满意度数据
    province_code_abbr = citycode[0:2]
    city_code_abbr = citycode[2:4]
    codetable = CodeTable()
    countylist = codetable.get_belong_county_info(province_code_abbr, city_code_abbr)  # 获取市内区域代码列表
    # countylist = {
    #  [countyname , countycode, count]
    #  [countyname , countycode, count]
    # }

    area_relatived_comments = {}  # 按照分区储存评论数据
    for county_info in countylist:
        temp_comment_list = []
        for tcomment in target_comments:
            if tcomment.get('countyCode') == county_info[1]:
                temp_comment_list.append(tcomment)
        area_relatived_comments[(county_info[0],county_info[1])] = temp_comment_list  # [comment1, comment2, ]

    # 按照分区统计分区内各项评价指标
    final_comments = []
    for k, v in area_relatived_comments:
        # k是辖区名称，v是辖区内评论的列表
        service_score = 0
        price_score = 0
        quality_score = 0
        envir_score = 0
        efficiency_score = 0
        c_count = len(v)
        temp_count = 0
        for c in v:
            if c.get('allComment') >= 2:
                temp_count += 1
            service_score += c.get('serviceScore')
            price_score += c.get('priceScore')
            quality_score += c.get('qualityScore')
            envir_score += c.get('envirScore')
            efficiency_score += c.get('efficiencyScore')
        area_data = {
            'county': k[0],
            'countCode':k[1],
            'serviceScore': round(service_score / c_count, 1),
            'priceScore': round(price_score / c_count, 1),
            'qualityScore': round(quality_score / c_count, 1),
            'envirScore': round(envir_score / c_count, 1),
            'efficiencyScore': round(efficiency_score / c_count, 1),
            'allComment': round(temp_count / c_count, 3),
        }

        final_comments.append(area_data)

    cursor = mongo_client.statistics.comments.find({'created': {'$gte': start_of_day, '$lt': end_of_day}},
                                             {'_id': True, 'company': True})

    # 统计数据入库
    satisfactionInfo = {
        'citycode': '371100',
        'general': {
            'totalcomments': 1000,  # 总评论数
            'goodcomments': 800,  # 满意评价数
            'satisfactionrate': 0.8,  # 总体满意率
        },
        'area': {
            'total': {
                {'岚山区': {'服务态度': 1.1, '评价满意度': 0.9},
                 '东港区': {'服务态度': 1.1, '评价满意度': 0.9},
                 '市辖区': {'服务态度': 1.1, '评价满意度': 0.9},
                 },
            },
            'lastweek': {},
            'lastmonth': {},
            'lastseason': {},
        },
        'trends': {
            'weekly': {
                {'岚山区': [0.9, 0.4, 0.7],
                 '东港区': [0.9, 0.4, 0.7],
                 '市辖区': [0.9, 0.4, 0.7],
                 'date': [],
                 },
            },
            'monthly': {},
            'seasonly': {},
        },

    }
    # 获取
    comments = [comment for comment in cursor]
    comment_info = []  # 每天的所有评论信息
    for comment in comments:
        # 寻找评论所对应的维修企业信息
        company = mongo_client.spv1.companies.find_one({'_id': comment.get('company')})
        if company:
            info = {
                '_id': comment.get('_id'),
                'companyId': comment.get('company'),
                'provinceCode': str(int(company.get('provinceCode'))),
                'cityCode': str(int(company.get('cityCode'))),
                'countyCode': str(int(company.get('countyCode'))),
            }
            comment_info.append(info)

    print('%s-%s-%s 共 %s 条评价信息' % (stats_day.year, stats_day.month, stats_day.day, len(comments)))
    # 写入统计数据库
    mongo_client.statistics.commentsstatistics.replace_one({'date': recorded_date},
                                                           {'date': recorded_date, 'commentIds': comment_info},
                                                           upsert=True)
