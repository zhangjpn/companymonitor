# -*-coding:utf-8 -*-
import calendar
from datetime import datetime, timedelta
from flask import request, jsonify, Blueprint
from pymongo import MongoClient
from app.base_class import CodeTable
from app.commontools import get_last_month_period, get_last_season_period, get_last_n_month_period, \
    get_last_n_season_period

admin_bp = Blueprint('admin_bp', import_name=__name__)


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


@admin_bp.route(r'/commonapi/admin/statistics/companies', methods=['GET'])
def census_companies():
    """统计一段时间内每天活跃企业数"""
    # 参数处理
    start = str_to_date(request.args.get('from'))
    end = str_to_date(request.args.get('to'))
    city_code = request.args.get('citycode', '371100')  # 城市编号，'00' 结尾
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
    mongo_client = MongoClient(host='127.0.0.1', port=27017)
    active_records = mongo_client.statistics.companiesstatistics.find({'date': {'$gte': start_date, '$lte': end_date}},
                                                                      {'date': True, 'activeCompanyIds': True,
                                                                       '_id': False})
    # 获取区域代码
    province_code_abbr = city_code[0:2]
    city_code_abbr = city_code[2:4]
    codetable = CodeTable()
    countylist = codetable.get_belong_county_info(province_code_abbr, city_code_abbr)  # 获取市内区域代码列表
    # 数据重组
    res_data = []
    for record in active_records:  # {'date':xx,'activeCompanyIds':[{'_id':xx,'provinceCode':'','countyCode':''},{}]}
        # 对每天每个区域的活跃企业数量做统计
        for k in countylist:  # 计数初始化置成0
            k[2] = 0

        for i in record.get('activeCompanyIds'):  # i是每个企业的数据
            # 分区域统计
            for j in countylist:
                if i.get('countyCode') == j[1]:
                    j[2] += 1
        everyday_data = {'date': record.get('date')}  # 每天的统计数据
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
    return jsonify({'code': '200', 'rows': res_data}), 200


@admin_bp.route(r'/commonapi/admin/statistics/comments', methods=['GET'])
def census_comments():
    """统计一段时间内辖区评论数"""
    # 参数处理
    start = str_to_date(request.args.get('from'))
    end = str_to_date(request.args.get('to'))
    city_code = request.args.get('citycode', '371100')  # 城市编号，'00' 结尾
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
    # spv1.commentsstatistics
    # 数据库形式
    # 行：{ 'date':'2017-07-01',
    #       'commentInfo':[{'companyId':'', 'commentId':'','provinceCode':371001,'citycode':,'countycode':}
    #       ]}
    mongo_client = MongoClient(host='127.0.0.1', port=27017)
    active_records = mongo_client.statistics.commentsstatistics.find({'date': {'$gte': start_date, '$lte': end_date}},
                                                                     {'date': True, 'commentIds': True, '_id': False})
    # 获取区域代码
    province_code_abbr = city_code[0:2]
    city_code_abbr = city_code[2:4]
    codetable = CodeTable()

    countylist = codetable.get_belong_county_info(province_code_abbr, city_code_abbr)  # 获取市内区域代码列表
    # countylist = {
    #  [countyname , countycode, count]
    #  [countyname , countycode, count]
    # }

    # 数据重组
    rows = []
    # 按照每天进行处理
    # {'date': xx, 'activeCompanyIds': [{'_id': xx, 'provinceCode': '', 'countyCode': ''}, {}]}
    for record in active_records:
        # 对每天每个区域的活跃企业数量做统计
        for k in countylist:  # 计数初始化置成0
            k[2] = 0
        # 分区域统计
        for i in record.get('commentIds'):  # i代表每天的每条评论信息

            for j in countylist:
                if i.get('countyCode') == j[1]:
                    j[2] += 1
        everyday_data = {'date': record.get('date')}  # 每天的统计数据
        for countyinfo in countylist:
            everyday_data[countyinfo[0]] = countyinfo[2]
        rows.append(everyday_data)
    # # 数据形式转换成
    # sorted_data = sorted(rows, key=operator.itemgetter('date'))
    # final_data = {}
    # date_list = []  # 返回一个日期数组
    # for county in countylist:
    #     temp_li = []
    #     for item in sorted_data:
    #         temp_li.append(item[county[0]])
    #     final_data[county[0]] = temp_li
    # final_data['date'] = date_list
    return jsonify({'code': '200', 'rows': rows}), 200


@admin_bp.route(r'/commonapi/admin/statistics/comments/<dtype>', methods=['GET'])
def comments(dtype):
    """维修评价统计"""
    request_api = {
        'satisfaction': 1,
        'repairtype': 2,
        'vehicletype': 3,
        'category': 4,
    }
    if dtype not in request_api:
        return jsonify({'code': 404}), 404
    stat_type = request_api[dtype]
    mongo_client = MongoClient(host='127.0.0.1', port=27017)
    today = datetime.today()
    default_time = datetime(2000, 1, 1)
    # 参数处理
    city_code = request.args.get('citycode')
    codetable = CodeTable()
    if not codetable.varify_citycode(city_code):
        return jsonify({'code': 400}), 400
    # 中间区域，全体数据
    history_total = mongo_client.statistics.commentsstatistics.find(
        {'statsType': stat_type, 'dataType': 1, 'cityCode': city_code, 'periodStart': default_time,
         'periodEnd': default_time},
        {'_id': False, 'dataType': False, 'statsType': False})
    totaldata = []
    for w in history_total:
        w['periodStart'] = w.get('periodStart').isoformat()
        w['periodEnd'] = w.get('periodEnd').isoformat()
        totaldata.append(w)

    # 上一周
    bias = calendar.weekday(today.year, today.month, today.day)
    start_week_day = datetime(today.year, today.month, today.day, tzinfo=None) - timedelta(bias + 7)
    end_week_day = start_week_day + timedelta(days=6)

    week_cursor = mongo_client.statistics.commentsstatistics.find(
        {'periodStart': start_week_day, 'periodEnd': end_week_day, 'statsType': stat_type, 'dataType': 2,
         'cityCode': city_code},
        {'_id': False, 'dataType': False, 'statsType': False})
    lastweek = []
    for w in week_cursor:
        w['periodStart'] = w.get('periodStart').isoformat()
        w['periodEnd'] = w.get('periodEnd').isoformat()
        lastweek.append(w)

    # 上一月
    start_last_month, end_last_month = get_last_month_period(today)
    month_cursor = mongo_client.statistics.commentsstatistics.find(
        {'cityCode': city_code, 'statsType': stat_type, 'periodStart': start_last_month, 'periodEnd': end_last_month,
         'dataType': 3},
        {'_id': False, 'dataType': False, 'statsType': False})
    lastmonth = []
    for w in month_cursor:
        w['periodStart'] = w.get('periodStart').isoformat()
        w['periodEnd'] = w.get('periodEnd').isoformat()
        lastmonth.append(w)

    # 上一季度
    start_season_day, end_season_day = get_last_season_period(today)
    season_cursor = mongo_client.statistics.commentsstatistics.find(
        {'statsType': stat_type, 'dataType': 4, 'cityCode': city_code, 'periodStart': start_season_day,
         'periodEnd': end_season_day},
        {'_id': False, 'dataType': False, 'statsType': False})
    lastseason = []
    for w in season_cursor:
        w['periodStart'] = w.get('periodStart').isoformat()
        w['periodEnd'] = w.get('periodEnd').isoformat()
        lastseason.append(w)

    # 获取趋势数据
    # 获取周趋势
    bias = calendar.weekday(today.year, today.month, today.day)
    start_trend_week_day = datetime(today.year, today.month, today.day, tzinfo=None) - timedelta(bias) - timedelta(
        6 * 7)
    end_trend_week_day = datetime(today.year, today.month, today.day, tzinfo=None) + timedelta(days=(6 - bias))

    weekly_trend_cursor = mongo_client.statistics.commentsstatistics.find(
        {'dataType': 2, 'statsType': stat_type, 'cityCode': city_code, 'periodStart': {'$gte': start_trend_week_day},
         'periodEnd': {'$lte': end_trend_week_day}},
        {'_id': False, 'dataType': False, 'statsType': False})
    weekly_trends = []
    for w in weekly_trend_cursor:
        w['periodStart'] = w.get('periodStart').isoformat()
        w['periodEnd'] = w.get('periodEnd').isoformat()
        weekly_trends.append(w)

    # 获取月趋势
    start_trend_month_day, end_trend_month_day = get_last_n_month_period(today)
    monthly_trend_cursor = mongo_client.statistics.commentsstatistics.find(
        {'dataType': 3, 'statsType': stat_type, 'cityCode': city_code, 'periodStart': {'$gte': start_trend_month_day},
         'periodEnd': {'$lte': end_trend_month_day}},
        {'_id': False, 'dataType': False, 'statsType': False})
    monthly_trends = []
    for w in monthly_trend_cursor:
        w['periodStart'] = w.get('periodStart').isoformat()
        w['periodEnd'] = w.get('periodEnd').isoformat()
        monthly_trends.append(w)

    # 获取季度趋势
    start_trend_season_day, end_trend_season_day = get_last_n_season_period(today)
    seasonly_trend_cursor = mongo_client.statistics.commentsstatistics.find(
        {'dataType': 4, 'statsType': stat_type, 'cityCode': city_code, 'periodStart': {'$gte': start_trend_season_day},
         'periodEnd': {'$lte': end_trend_season_day}},
        {'_id': False, 'dataType': False, 'statsType': False})

    seasonly_trends = []
    for w in seasonly_trend_cursor:
        w['periodStart'] = w.get('periodStart').isoformat()
        w['periodEnd'] = w.get('periodEnd').isoformat()
        seasonly_trends.append(w)

    res_data = {
        'section': {
            'total': totaldata,
            'lastweek': lastweek,
            'lastmonth': lastmonth,
            'lastseason': lastseason,
        },
        'trends': {
            'weekly': weekly_trends,
            'monthly': monthly_trends,
            'seasonly': seasonly_trends,
        },
    }
    return jsonify(res_data), 200


@admin_bp.route(r'/commonapi/admin/statistics/complaints/total', methods=['GET'])
def complaints():
    """统计一段时间内各辖区的投诉量"""
    # 参数处理
    start = str_to_date(request.args.get('from'))
    end = str_to_date(request.args.get('to'))
    city_code = request.args.get('citycode', '371100')  # 城市编号，'00' 结尾
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
    # spv1.complaintsstatistics

    mongo_client = MongoClient(host='127.0.0.1', port=27017)
    active_records = mongo_client.statistics.complaintsstatistics.find({'date': {'$gte': start_date, '$lte': end_date}},
                                                                       {'date': True, 'complaintIds': True,
                                                                        '_id': False})
    # 获取区域代码
    province_code_abbr = city_code[0:2]
    city_code_abbr = city_code[2:4]
    codetable = CodeTable()
    countylist = codetable.get_belong_county_info(province_code_abbr, city_code_abbr)  # 获取市内区域代码列表

    # 数据重组
    rows = []
    for record in active_records:  # {'date':xx,'activeCompanyIds':[{'_id':xx,'provinceCode':'','countyCode':''},{}]}
        # 对每天每个区域的活跃企业数量做统计
        for k in countylist:  # 计数初始化置成0
            k[2] = 0

        for i in record.get('complaintIds'):  # i是每条投诉的信息
            # j是每个区域
            for j in countylist:
                if i.get('countyCode') == j[1]:
                    j[2] += 1
        everyday_data = {'date': record.get('date')}  # 每天的统计数据
        for countyinfo in countylist:
            everyday_data[countyinfo[0]] = countyinfo[2]
        rows.append(everyday_data)
    # # 数据形式转换成
    # sorted_data = sorted(res_data, key=operator.itemgetter('date'))
    # final_data = {}
    # for county in countylist:
    #     temp_li = []
    #     for item in sorted_data:
    #         temp_li.append(item[county[0]])
    #     final_data[county[0]] = temp_li

    return jsonify({'code': '200', 'rows': rows}), 200
