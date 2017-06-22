# -*-coding:utf-8 -*-
"""定时统计任务"""
from datetime import tzinfo, timedelta, datetime, date
from pymongo import MongoClient
from bson import ObjectId


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


def stats(year, month, day):
    """统计一天的活跃维修企业数
    :param stats_day Date  被统计日期

    """

    now = datetime(year,month,day)
    localtz = UTC(8)
    start_of_day = datetime(now.year, now.month, now.day, hour=0, minute=0, second=0, tzinfo=localtz)
    end_of_day = datetime(now.year, now.month, now.day + 1, tzinfo=localtz)
    # 获取所有当天的上传维修记录
    mongo_client = MongoClient(host='127.0.0.1', port=27017)
    cursor = mongo_client.spv1.maintenaces.distinct('companyId', {'created': {'$gte': start_of_day, '$lt': end_of_day}
                                                                  })
    # 维修企业ID
    company_ids = [_id for _id in cursor]

    #

    print(company_ids)
    # for _id in cursor:
    #     ID = mongo_client.spv1.companies.find_one({'_id': _id},{'ID':True,'_id':False})
    #     print(ID, _id)


    # 写入统计数据库
    mongo_client.spv1.activecompanies.replace_one({'date': now, },
                                                  {'date': now, 'activeCompanyId': company_ids}, upsert=True)
    # mongo_client.spv1.activecompanies.insert_many({'date': stats_day, 'activeCompanyId': company_ids})


if __name__ == '__main__':
    stats_day = date(2017, 6, 19)
    stats(2017, 6, 19)
