# -*-coding:utf-8 -*-
"""定时统计任务"""
from datetime import tzinfo, timedelta, datetime, date
from pymongo import MongoClient


class UTC(tzinfo):
    """UTC"""

    def __init__(self, offset=0):
        self._offset = offset

    def utcoffset(self, dt):
        return timedelta(hours=self._offset)

    def tzname(self, dt):
        return "UTC +%s" % self._offset

    def dst(self, dt):
        return timedelta(hours=self._offset)


def stats(stats_day):
    """统计一天的活跃维修企业数
    :param stats_day date 被统计日期
    """
    record = datetime(stats_day.year, stats_day.month, stats_day.day, hour=0, minute=0, second=0,tzinfo=UTC(0))
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
                'provinceCode': company.get('provinceCode'),
                'cityCode': company.get('cityCode'),
                'countyCode': company.get('countyCode'),
            }
            company_info.append(info)

    print('%s-%s-%s 共 %s 家企业上传了维修记录' % (stats_day.year, stats_day.month, stats_day.day, len(company_ids)))
    # 写入统计数据库
    mongo_client.spv1.activecompanies.replace_one({'date': record},
                                                  {'date': record, 'activeCompanyIds': company_info}, upsert=True)

if __name__ == '__main__':
    basedate = date(2017, 1, 1)
    delta = timedelta(1)
    for i in range(180):
        stats(basedate)
        basedate += delta
