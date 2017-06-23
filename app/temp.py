# -*-coding:utf-8 -*-

from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime
from app.base_class import CodeTable
import operator
def str_to_date(string=None):
    if not isinstance(string, str):
        return None
    string = string.strip()
    try:
        res = datetime.strptime(string, '%Y.%m.%d')
        return res
    except ValueError:
        try:
            res = datetime.strptime(string, '%Y-%m-%d')
            return res
        except ValueError:
            pass
    return None


def active_companies(startdate, enddate, citycode):
    """统计一段时间内每天活跃企业数"""
    # 参数处理
    start = str_to_date(startdate)  # request.args.get('startdate')
    end = str_to_date(enddate)  # request.args.get('enddate'))
    # provinceCode = request.args.get('provincecode')
    city_code = citycode  # request.args.get('citycode')
    if not start and not end:
        start_date = end_date = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    elif start is None or end is None:
        if start is None:
            start_date = end_date = end
        else:
            start_date = end_date = start
    else:
        start_date = start
        end_date = end
    # 查询数据库
    # spv1.activecompanies

    mongo_client = MongoClient(host='127.0.0.1', port=27017)
    active_records = mongo_client.spv1.activecompanies.find({'date': {'$gte': start_date, '$lte': end_date}},
                                                            {'date': True, 'activeCompanyIds': True, '_id': False})

    # 获取区域代码
    province_code_abbr = city_code[0:2]
    city_code_abbr = city_code[2:4]
    codetable = CodeTable()
    countylist = codetable.get_belong_county_info(province_code_abbr, city_code_abbr)
    print('countylist:', countylist)
    # 数据重组

    final_data = []
    # 返回 {'date':{'东港'：1,'xx':4...}}
    for record in active_records:  # item是{'date':xx,'activeCompanyIds':[{'_id':xx,'provinceCode':'','countyCode':''},{}]}
        # 对每天每个区域的活跃企业数量做统计
        for k in countylist:  # 计数初始化置成0
            k[2] = 0

        for i in record.get('activeCompanyIds'):  # i是每个企业的编码
            # 分区域统计，如果
            for j in countylist:  # ['','',0]
                if str(i.get('countyCode')) == j[1]:
                    j[2] += 1
        everyday_data = {'date': record.get('date')}  # 每天的统计数据
        for countyinfo in countylist:
            everyday_data[countyinfo[0]] = countyinfo[2]
        final_data.append(everyday_data)

    for each in final_data:
        print('统计数据：', each)
    # return jsonify({'code': '200', 'data': final_data}), 200


if __name__ == '__main__':
    # print(str_to_date())
    active_companies('2017-05-01', '2017-05-31', '371100')
