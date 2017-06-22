# -*-coding:utf-8 -*-

from flask import Flask, request, jsonify
from pymongo import MongoClient

app = Flask(__name__)


@app.route(r'/', methods=['GET'])
def active_companies():
    """统计一段时间内每天活跃企业数"""
    data = []
    start_date = request.args.get('from')
    end_date = request.args.get('to')

    # 参数处理
    if not start_date or not end_date:

    #
    start = start_date
    end = end_date
    # 查询数据库
    # spv1.activecompanies
    mongo_client = MongoClient(host='127.0.0.1', port=27017)
    active_record = mongo_client.spv1.activecompanies.find({'date':{'$gt':start,'$lt':end}})
    for eachday in active_record:
        eachday.get('')
    return jsonify({'code':'200', 'data':data}), 200