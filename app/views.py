# -*-coding:utf-8 -*-

from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime
from .base_class import CodeTable

app = Flask(__name__)

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


@app.route(r'/monitor/admin/statistics/companies', methods=['GET'])
def census_companies():
    """统计一段时间内每天活跃企业数"""
    # 参数处理
    start = str_to_date(request.args.get('from'))
    end = str_to_date(request.args.get('to'))
    city_code = request.args.get('citycode')  # 城市编号，'00' 结尾
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
    countylist = codetable.get_belong_county_info(province_code_abbr, city_code_abbr) # 获取市内区域代码列表
    # 数据重组
    res_data = []
    for record in active_records:  # item是{'date':xx,'activeCompanyIds':[{'_id':xx,'provinceCode':'','countyCode':''},{}]}
        # 对每天每个区域的活跃企业数量做统计
        for k in countylist:  # 计数初始化置成0
            k[2] = 0

        for i in record.get('activeCompanyIds'):  # i是每个企业的编码
            # 分区域统计，如果
            for j in countylist:  # ['','',0]
                if str(i.get('countyCode')) == j[1]:
                    j[2] += 1
        everyday_data = {'date': record.get('date').strftime('%Y-%m-%d')}  # 每天的统计数据
        for countyinfo in countylist:
            everyday_data[countyinfo[0]] = countyinfo[2]
        res_data.append(everyday_data)
    # # 数据形式转换成
    # sorted_data = sorted(res_data, key=operator.itemgetter('date'))
    # final_data = {}
    # for county in countylist:
    #     temp_li = []
    #     for item in sorted_data:
    #         temp_li.append(item[county[0]])
    #     final_data[county[0]] = temp_li
    return jsonify({'code': '200', 'companies': res_data}), 200

@app.route(r'/monitor/admin/statistics/comments', methods=['GET'])
def census_comments():
    """统计一段时间内辖区评论数"""
    # 参数处理
    start = str_to_date(request.args.get('from'))
    end = str_to_date(request.args.get('to'))
    city_code = request.args.get('citycode')  # 城市编号，'00' 结尾
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
    countylist = codetable.get_belong_county_info(province_code_abbr, city_code_abbr) # 获取市内区域代码列表
    # 数据重组
    res_data = []
    for record in active_records:  # item是{'date':xx,'activeCompanyIds':[{'_id':xx,'provinceCode':'','countyCode':''},{}]}
        # 对每天每个区域的活跃企业数量做统计
        for k in countylist:  # 计数初始化置成0
            k[2] = 0

        for i in record.get('activeCompanyIds'):  # i是每个企业的编码
            # 分区域统计，如果
            for j in countylist:  # ['','',0]
                if str(i.get('countyCode')) == j[1]:
                    j[2] += 1
        everyday_data = {'date': record.get('date').strftime('%Y-%m-%d')}  # 每天的统计数据
        for countyinfo in countylist:
            everyday_data[countyinfo[0]] = countyinfo[2]
        res_data.append(everyday_data)
    # # 数据形式转换成
    # sorted_data = sorted(res_data, key=operator.itemgetter('date'))
    # final_data = {}
    # for county in countylist:
    #     temp_li = []
    #     for item in sorted_data:
    #         temp_li.append(item[county[0]])
    #     final_data[county[0]] = temp_li
    return jsonify({'code': '200', 'companies': res_data}), 200


@app.route(r'/monitor/admin/statistics/complaints', methods=['GET'])
def census_complaints():
    """统计一段时间内各辖区的投诉量"""
    # 参数处理
    start = str_to_date(request.args.get('from'))
    end = str_to_date(request.args.get('to'))
    city_code = request.args.get('citycode')  # 城市编号，'00' 结尾
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
    countylist = codetable.get_belong_county_info(province_code_abbr, city_code_abbr) # 获取市内区域代码列表
    # 数据重组
    res_data = []
    for record in active_records:  # item是{'date':xx,'activeCompanyIds':[{'_id':xx,'provinceCode':'','countyCode':''},{}]}
        # 对每天每个区域的活跃企业数量做统计
        for k in countylist:  # 计数初始化置成0
            k[2] = 0

        for i in record.get('activeCompanyIds'):  # i是每个企业的编码
            # 分区域统计，如果
            for j in countylist:  # ['','',0]
                if str(i.get('countyCode')) == j[1]:
                    j[2] += 1
        everyday_data = {'date': record.get('date').strftime('%Y-%m-%d')}  # 每天的统计数据
        for countyinfo in countylist:
            everyday_data[countyinfo[0]] = countyinfo[2]
        res_data.append(everyday_data)
    # # 数据形式转换成
    # sorted_data = sorted(res_data, key=operator.itemgetter('date'))
    # final_data = {}
    # for county in countylist:
    #     temp_li = []
    #     for item in sorted_data:
    #         temp_li.append(item[county[0]])
    #     final_data[county[0]] = temp_li
    return jsonify({'code': '200', 'companies': res_data}), 200
    return jsonify({}), 200