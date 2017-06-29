# -*-coding:utf-8 -*-
"""定时统计任务"""

from datetime import tzinfo, timedelta, datetime, date
from pymongo import MongoClient


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


def census_companies(stats_day):
    """统计一天的活跃维修企业数
    :param stats_day date 被统计日期
    """
    record = datetime(stats_day.year, stats_day.month, stats_day.day, hour=0, minute=0, second=0, tzinfo=UTC(0))
    localtz = UTC(8)
    start_of_day = datetime(stats_day.year, stats_day.month, stats_day.day, hour=0, minute=0, second=0, tzinfo=localtz)
    end_of_day = start_of_day + timedelta(days=1)
    # 获取所有当天的上传维修记录的维修企业Id
    mongo_client = MongoClient(host='127.0.0.1', port=27017)
    cursor = mongo_client.spv1.maintenaces.distinct('companyId', {'created': {'$gte': start_of_day, '$lt': end_of_day}
                                                                  })
    # 维修企业ID
    company_ids = [_id for _id in cursor]
    company_info = []
    for _id in company_ids:
        company = mongo_client.spv1.companies.find_one({'_id': _id})
        if company:
            info = {
                '_id': _id,
                'provinceCode': str(int(company.get('provinceCode'))),
                'cityCode': str(int(company.get('cityCode'))),
                'countyCode': str(int(company.get('countyCode'))),
            }
            company_info.append(info)

    print('%s-%s-%s 共 %s 家企业上传了维修记录' % (stats_day.year, stats_day.month, stats_day.day, len(company_ids)))
    # 写入统计数据库
    mongo_client.statistics.companiesstatistics.replace_one({'date': record},
                                                            {'date': record, 'activeCompanyIds': company_info},
                                                            upsert=True)


def census_comments(stats_day):
    """统计一天的活跃维修企业数
    :param stats_day date 被统计日期
    """
    # 日期处理
    recorded_date = datetime(stats_day.year, stats_day.month, stats_day.day, hour=0, minute=0, second=0, tzinfo=UTC(0))
    localtz = UTC(8)
    start_of_day = datetime(stats_day.year, stats_day.month, stats_day.day, hour=0, minute=0, second=0, tzinfo=localtz)
    end_of_day = start_of_day + timedelta(days=1)

    # 获取所有当天的评价记录
    mongo_client = MongoClient(host='127.0.0.1', port=27017)
    cursor = mongo_client.spv1.comments.find({'created': {'$gte': start_of_day, '$lt': end_of_day}},
                                             {'_id': True, 'company': True})

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


def census_complaints(stats_day):
    """统计一天的活跃维修企业数
    :param stats_day date 被统计日期
    """
    # 日期处理
    recorded_date = datetime(stats_day.year, stats_day.month, stats_day.day, hour=0, minute=0, second=0, tzinfo=UTC(0))
    localtz = UTC(8)
    start_of_day = datetime(stats_day.year, stats_day.month, stats_day.day, hour=0, minute=0, second=0, tzinfo=localtz)
    end_of_day = start_of_day + timedelta(days=1)

    # 获取所有当天的评价记录
    mongo_client = MongoClient(host='127.0.0.1', port=27017)
    cursor = mongo_client.spv1.complaints.find({'created': {'$gte': start_of_day, '$lt': end_of_day}},
                                               {'_id': True, 'provinceCode': True, 'cityCode': True,
                                                'countyCode': True})
    complaints = [complaint for complaint in cursor]
    complaints_info = []  # 每天的所有投诉信息
    for complaint in complaints:
        # 寻找评论所对应的维修企业信息
        try:
            info = {
                '_id': complaint.get('_id'),
                'provinceCode': str(int(complaint.get('provinceCode'))),
                'cityCode': str(int(complaint.get('cityCode'))),
                'countyCode': str(int(complaint.get('countyCode'))),
            }
            complaints_info.append(info)
        except Exception as e:
            print(e)
    print('%s-%s-%s 共 %s 条评价信息' % (stats_day.year, stats_day.month, stats_day.day, len(complaints)))
    # 写入统计数据库
    mongo_client.statistics.complaintsstatistics.replace_one({'date': recorded_date},
                                                             {'date': recorded_date, 'complaintIds': complaints_info},
                                                             upsert=True)


if __name__ == '__main__':
    basedate = date(2017, 1, 1)
    delta = timedelta(1)
    for i in range(300):
        census_companies(basedate)
        census_comments(basedate)
        census_complaints(basedate)
        basedate += delta
