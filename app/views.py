# -*-coding:utf-8 -*-

from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime, date

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


@app.route(r'/', methods=['GET'])
def active_companies():
    """统计一段时间内每天活跃企业数"""
    data = []
    # 参数处理
    start = str_to_date(request.args.get('from'))
    end = str_to_date(request.args.get('to'))
    provinceCode = request.args.get('provincecode')
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
    active_record = mongo_client.spv1.activecompanies.find({'date': {'$gte': start_date, '$lte': end_date}},
                                                           {'date': True, 'activeCompanyIds': True, '_id': False})

    # 数据重组


    return jsonify({'code': '200', 'data': None}), 200


if __name__ == '__main__':
    print(str_to_date())
