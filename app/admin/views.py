# -*-coding:utf-8 -*-
import calendar
from datetime import datetime, timedelta
from flask import request, jsonify, Blueprint
from pymongo import MongoClient
from app.base_class import CodeTable
from app.commontools import *

admin_bp = Blueprint('admin_bp', import_name=__name__)


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


@admin_bp.route(r'/commonapi/admin/statistics/complaints/total', methods=['POST'])
def complaints():
    """统计一段时间内各辖区的投诉量"""
    # 参数处理

    today = datetime.today()
    city_code = request.args.get('citycode')
    if not city_code:
        return jsonify({'code': '400'}), 400

    # 查询数据库
    mongo_client = MongoClient(host='127.0.0.1', port=27017)
    maintenaces_stats = mongo_client.statistics.maintenacesstatistics.find({'cityCode': city_code})

    # 获取区域代码
    province_code_abbr = city_code[0:2]
    city_code_abbr = city_code[2:4]
    codetable = CodeTable()
    countylist = codetable.get_belong_county_info(province_code_abbr, city_code_abbr)  # 获取市内区域代码列表

    # 对数据进行辖区划分
    area_relatived_record = {}
    for county_info in countylist:
        temp_statistics_list = []
        for tstats in maintenaces_stats:
            if str(int(tstats.get('countyCode'))) == county_info[1]:
                temp_statistics_list.append(tstats)
        area_relatived_record[(county_info[0], county_info[1])] = temp_statistics_list

    # 统计，全部历史数据
    totaldata = []
    for k, v in area_relatived_record.items():
        total_complaint_qty = 0
        total_maintenace_qty = 0
        for eachday in v:
            total_maintenace_qty += eachday.get('maintenaceQty')
            total_complaint_qty += eachday.get('complaintQty')
        area = {
            'countyCode': k[1],
            'cityCode': city_code,
            'maintenaceQty': total_maintenace_qty,
            'complaintQty': total_complaint_qty,
        }
        totaldata.append(area)

    # 上一周
    bias = calendar.weekday(today.year, today.month, today.day)
    start_week_day = datetime(today.year, today.month, today.day, tzinfo=None) - timedelta(bias + 7)
    end_week_day = start_week_day + timedelta(days=6)

    lastweek = []
    for k, v in area_relatived_record.items():
        total_complaint_qty = 0
        total_maintenace_qty = 0

        for eachday in v:
            # 选择上周时间内的统计数据
            if not in_week((start_week_day, end_week_day), eachday.get('date')):
                continue
            total_maintenace_qty += eachday.get('maintenaceQty')
            total_complaint_qty += eachday.get('complaintQty')
        area_last_week = {
            'countyCode': k[1],
            'cityCode': city_code,
            'maintenaceQty': total_maintenace_qty,
            'complaintQty': total_complaint_qty,
        }
        lastweek.append(area_last_week)

    # 上一月
    start_last_month, end_last_month = get_last_month_period(today)
    lastmonth = []
    for k, v in area_relatived_record.items():
        total_complaint_qty = 0
        total_maintenace_qty = 0
        for eachday in v:
            # 选择上周时间内的统计数据
            if not in_month((start_last_month, end_last_month), eachday.get('date')):
                continue
            total_maintenace_qty += eachday.get('maintenaceQty')
            total_complaint_qty += eachday.get('complaintQty')
        area_last_month = {
            'countyCode': k[1],
            'cityCode': city_code,
            'maintenaceQty': total_maintenace_qty,
            'complaintQty': total_complaint_qty,
        }
        lastmonth.append(area_last_month)

    # 上一季度
    start_season_day, end_season_day = get_last_season_period(today)
    lastseason = []
    for k, v in area_relatived_record.items():

        total_complaint_qty = 0
        total_maintenace_qty = 0
        for eachday in v:
            # 选择上周时间内的统计数据
            if not in_season((start_season_day, end_season_day), eachday.get('date')):
                continue
            total_maintenace_qty += eachday.get('maintenaceQty')
            total_complaint_qty += eachday.get('complaintQty')
        area_last_season = {
            'countyCode': k[1],
            'cityCode': city_code,
            'maintenaceQty': total_maintenace_qty,
            'complaintQty': total_complaint_qty,
        }
        lastseason.append(area_last_season)

    # ##########获取趋势数据##########
    #######################
    # 获取周趋势
    bias = calendar.weekday(today.year, today.month, today.day)
    start_trend_week_day = datetime(today.year, today.month, today.day, tzinfo=None) - timedelta(bias) - timedelta(
        6 * 7)
    end_trend_week_day = datetime(today.year, today.month, today.day, tzinfo=None) + timedelta(days=(6 - bias))
    # 生成各周范围列表
    weeks = create_week_list(start_trend_week_day.strftime('%Y-%m-%d'), end_trend_week_day.strftime('%Y-%m-%d'))
    weekly_trends = []
    for k, v in area_relatived_record.items():
        total_complaint_qty = 0
        total_maintenace_qty = 0

        for week in weeks:
            for eachday in v:
                # 选择周时间内的统计数据
                if not in_week(week, eachday.get('date')):
                    continue
                total_maintenace_qty += eachday.get('maintenaceQty')
                total_complaint_qty += eachday.get('complaintQty')
            area_per_week = {
                'countyCode': k[1],
                'cityCode': city_code,
                'maintenaceQty': total_maintenace_qty,
                'complaintQty': total_complaint_qty,
                'startPeriod': week[0].isoformat(),
                'endPeriod': week[1].isoformat(),
            }
            weekly_trends.append(area_per_week)
    #######################
    # 获取月趋势
    start_trend_month_day, end_trend_month_day = get_last_n_month_period(today)
    # 生成各周范围列表
    months = create_month_list(start_trend_month_day.strftime('%Y-%m-%d'), end_trend_month_day.strftime('%Y-%m-%d'))
    monthly_trends = []
    for k, v in area_relatived_record.items():

        total_complaint_qty = 0
        total_maintenace_qty = 0

        for month in months:
            for eachday in v:
                # 选择月时间内的统计数据
                if not in_month(month, eachday.get('date')):
                    continue
                total_maintenace_qty += eachday.get('maintenaceQty')
                total_complaint_qty += eachday.get('complaintQty')
            area_per_month = {
                'countyCode': k[1],
                'cityCode': city_code,
                'maintenaceQty': total_maintenace_qty,
                'complaintQty': total_complaint_qty,
                'startPeriod': month[0].isoformat(),
                'endPeriod': month[1].isoformat(),
            }
            monthly_trends.append(area_per_month)
    #######################
    # 获取季度趋势
    start_trend_season_day, end_trend_season_day = get_last_n_season_period(today)
    # 生成各周范围列表
    seasons = create_season_list(start_trend_season_day.strftime('%Y-%m-%d'), end_trend_season_day.strftime('%Y-%m-%d'))

    seasonly_trends = []
    for k, v in area_relatived_record.items():
        total_complaint_qty = 0
        total_maintenace_qty = 0

        for season in seasons:
            for eachday in v:
                # 选择周时间内的统计数据
                if not in_season(season, eachday.get('date')):
                    continue
                total_maintenace_qty += eachday.get('maintenaceQty')
                total_complaint_qty += eachday.get('complaintQty')
            area_per_season = {
                'countyCode': k[1],
                'cityCode': city_code,
                'maintenaceQty': total_maintenace_qty,
                'complaintQty': total_complaint_qty,
                'startPeriod': season[0].isoformat(),
                'endPeriod': season[1].isoformat(),
            }
            seasonly_trends.append(area_per_season)
#####################
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


@admin_bp.route(r'/commonapi/admin/statistics/comments/vehiclebrand', methods=['GET'])
def vehicle_brand():
    """统计一段时间内各辖区的投诉量"""
    # 参数处理
    # request_api = {
    #     'satisfaction': 1,
    #     'repairtype': 2,
    #     'vehicletype': 3,
    #     'category': 4,
    #     'vehiclebrand': 5,
    # }
    # if dtype not in request_api:
    #     return jsonify({'code': 404}), 404
    # stat_type = request_api[dtype]
    today = datetime.today()
    city_code = request.args.get('citycode')
    if not city_code:
        return jsonify({'code': '400'}), 400



    # 查询数据库
    mongo_client = MongoClient(host='127.0.0.1', port=27017)
    comments_brand = mongo_client.statistics.vehiclebrand.find({'cityCode': city_code})

    # 获取车辆品牌列表
    vehiclebrandlist = mongo_client.spv1.maintenaces.distinct('vehicleBrand')

    # 对数据进行品牌划分
    brand_relatived_record = {}
    for brand in vehiclebrandlist:
        statistics_list = []
        for tstats in comments_brand:
            if str(tstats.get('vehicleBrand')) == brand:
                statistics_list.append(tstats)
        brand_relatived_record[brand] = statistics_list

    # 统计，全部历史数据
    totaldata = []
    for k, v in brand_relatived_record.items():
        comments_num = 0  # 总数计数
        satisfied_num = 0  # 满意评论计数
        service_score = 0,
        price_score = 0,
        quality_score = 0,
        envir_score = 0,
        efficiency_score = 0
        all_comment = 0,
        for eachday in v:
            comments_num += eachday.get('commentsQty')
            satisfied_num += eachday.get('satisfiedcommentsQty')
            service_score += eachday.get('serviceScore') * eachday.get('commentsQty')
            price_score += eachday.get('serviceScore') * eachday.get('commentsQty')
            quality_score += eachday.get('serviceScore') * eachday.get('commentsQty')
            envir_score += eachday.get('serviceScore') * eachday.get('commentsQty')
            efficiency_score += eachday.get('serviceScore') * eachday.get('commentsQty')
            all_comment += eachday.get('allComment') * eachday.get('commentsQty')
        brand_data = {
            'provinceCode': city_code[0:2] + '0000',
            'cityCode': city_code,
            'vehicleBrand': k,  # 品牌
            'commentsQty': comments_num,  # 维修量
            'satisfiedcommentsQty': satisfied_num,  # 满意评价数
            'serviceScore': round(service_score / comments_num, 1),
            'priceScore': round(price_score / comments_num, 1),
            'qualityScore': round(quality_score / comments_num, 1),
            'envirScore': round(envir_score / comments_num, 1),
            'efficiencyScore': round(efficiency_score / comments_num, 1),
            'allComment': round(all_comment / comments_num, 1),
        }
        totaldata.append(brand_data)
####################
    # 上一周
    bias = calendar.weekday(today.year, today.month, today.day)
    start_week_day = datetime(today.year, today.month, today.day, tzinfo=None) - timedelta(bias + 7)
    end_week_day = start_week_day + timedelta(days=6)

    lastweek = []
    for k, v in brand_relatived_record.items():
        comments_num = 0  # 总数计数
        satisfied_num = 0  # 满意评论计数
        service_score = 0,
        price_score = 0,
        quality_score = 0,
        envir_score = 0,
        efficiency_score = 0
        all_comment = 0,
        for eachday in v:
            # 选择上周时间内的统计数据
            if not in_week((start_week_day, end_week_day), eachday.get('date')):
                continue
            comments_num += eachday.get('commentsQty')
            satisfied_num += eachday.get('satisfiedcommentsQty')
            service_score += eachday.get('serviceScore') * eachday.get('commentsQty')
            price_score += eachday.get('serviceScore') * eachday.get('commentsQty')
            quality_score += eachday.get('serviceScore') * eachday.get('commentsQty')
            envir_score += eachday.get('serviceScore') * eachday.get('commentsQty')
            efficiency_score += eachday.get('serviceScore') * eachday.get('commentsQty')
            all_comment += eachday.get('allComment') * eachday.get('commentsQty')
        brand_data = {
            'provinceCode': city_code[0:2] + '0000',
            'cityCode': city_code,
            'vehicleBrand': k,  # 品牌
            'commentsQty': comments_num,  # 维修量
            'satisfiedcommentsQty': satisfied_num,  # 满意评价数
            'serviceScore': round(service_score / comments_num, 1),
            'priceScore': round(price_score / comments_num, 1),
            'qualityScore': round(quality_score / comments_num, 1),
            'envirScore': round(envir_score / comments_num, 1),
            'efficiencyScore': round(efficiency_score / comments_num, 1),
            'allComment': round(all_comment / comments_num, 1),
        }
        lastweek.append(brand_data)

####################
    # 上一月
    start_last_month, end_last_month = get_last_month_period(today)
    lastmonth = []
    for k, v in brand_relatived_record.items():
        comments_num = 0  # 总数计数
        satisfied_num = 0  # 满意评论计数
        service_score = 0,
        price_score = 0,
        quality_score = 0,
        envir_score = 0,
        efficiency_score = 0
        all_comment = 0,
        for eachday in v:
            # 选择上周时间内的统计数据
            if not in_month((start_last_month, end_last_month), eachday.get('date')):
                continue
            comments_num += eachday.get('commentsQty')
            satisfied_num += eachday.get('satisfiedcommentsQty')
            service_score += eachday.get('serviceScore') * eachday.get('commentsQty')
            price_score += eachday.get('serviceScore') * eachday.get('commentsQty')
            quality_score += eachday.get('serviceScore') * eachday.get('commentsQty')
            envir_score += eachday.get('serviceScore') * eachday.get('commentsQty')
            efficiency_score += eachday.get('serviceScore') * eachday.get('commentsQty')
            all_comment += eachday.get('allComment') * eachday.get('commentsQty')
        brand_data = {
            'provinceCode': city_code[0:2] + '0000',
            'cityCode': city_code,
            'vehicleBrand': k,  # 品牌
            'commentsQty': comments_num,  # 维修量
            'satisfiedcommentsQty': satisfied_num,  # 满意评价数
            'serviceScore': round(service_score / comments_num, 1),
            'priceScore': round(price_score / comments_num, 1),
            'qualityScore': round(quality_score / comments_num, 1),
            'envirScore': round(envir_score / comments_num, 1),
            'efficiencyScore': round(efficiency_score / comments_num, 1),
            'allComment': round(all_comment / comments_num, 1),
        }
        lastmonth.append(brand_data)
####################
    # 上一季度
    start_season_day, end_season_day = get_last_season_period(today)
    lastseason = []
    for k, v in brand_relatived_record.items():
        comments_num = 0  # 总数计数
        satisfied_num = 0  # 满意评论计数
        service_score = 0,
        price_score = 0,
        quality_score = 0,
        envir_score = 0,
        efficiency_score = 0
        all_comment = 0,
        for eachday in v:
            # 选择上周时间内的统计数据
            if not in_season((start_season_day, end_season_day), eachday.get('date')):
                continue
            comments_num += eachday.get('commentsQty')
            satisfied_num += eachday.get('satisfiedcommentsQty')
            service_score += eachday.get('serviceScore') * eachday.get('commentsQty')
            price_score += eachday.get('serviceScore') * eachday.get('commentsQty')
            quality_score += eachday.get('serviceScore') * eachday.get('commentsQty')
            envir_score += eachday.get('serviceScore') * eachday.get('commentsQty')
            efficiency_score += eachday.get('serviceScore') * eachday.get('commentsQty')
            all_comment += eachday.get('allComment') * eachday.get('commentsQty')
        brand_data = {
            'provinceCode': city_code[0:2] + '0000',
            'cityCode': city_code,
            'vehicleBrand': k,  # 品牌
            'commentsQty': comments_num,  # 维修量
            'satisfiedcommentsQty': satisfied_num,  # 满意评价数
            'serviceScore': round(service_score / comments_num, 1),
            'priceScore': round(price_score / comments_num, 1),
            'qualityScore': round(quality_score / comments_num, 1),
            'envirScore': round(envir_score / comments_num, 1),
            'efficiencyScore': round(efficiency_score / comments_num, 1),
            'allComment': round(all_comment / comments_num, 1),
        }
        lastseason.append(brand_data)
########################################################################未完待续######################
    # ##########获取趋势数据##########
    #######################
    # 获取周趋势
    bias = calendar.weekday(today.year, today.month, today.day)
    start_trend_week_day = datetime(today.year, today.month, today.day, tzinfo=None) - timedelta(bias) - timedelta(
        6 * 7)
    end_trend_week_day = datetime(today.year, today.month, today.day, tzinfo=None) + timedelta(days=(6 - bias))
    # 生成各周范围列表
    weeks = create_week_list(start_trend_week_day.strftime('%Y-%m-%d'), end_trend_week_day.strftime('%Y-%m-%d'))
    weekly_trends = []
    for k, v in brand_relatived_record.items():
        total_complaint_qty = 0
        total_maintenace_qty = 0

        for week in weeks:
            for eachday in v:
                # 选择周时间内的统计数据
                if not in_week(week, eachday.get('date')):
                    continue
                total_maintenace_qty += eachday.get('maintenaceQty')
                total_complaint_qty += eachday.get('complaintQty')
            area_per_week = {
                'countyCode': k[1],
                'cityCode': city_code,
                'maintenaceQty': total_maintenace_qty,
                'complaintQty': total_complaint_qty,
                'startPeriod': week[0].isoformat(),
                'endPeriod': week[1].isoformat(),
            }
            weekly_trends.append(area_per_week)
    #######################
    # 获取月趋势
    start_trend_month_day, end_trend_month_day = get_last_n_month_period(today)
    # 生成各周范围列表
    months = create_month_list(start_trend_month_day.strftime('%Y-%m-%d'), end_trend_month_day.strftime('%Y-%m-%d'))
    monthly_trends = []
    for k, v in brand_relatived_record.items():

        total_complaint_qty = 0
        total_maintenace_qty = 0

        for month in months:
            for eachday in v:
                # 选择月时间内的统计数据
                if not in_month(month, eachday.get('date')):
                    continue
                total_maintenace_qty += eachday.get('maintenaceQty')
                total_complaint_qty += eachday.get('complaintQty')
            area_per_month = {
                'countyCode': k[1],
                'cityCode': city_code,
                'maintenaceQty': total_maintenace_qty,
                'complaintQty': total_complaint_qty,
                'startPeriod': month[0].isoformat(),
                'endPeriod': month[1].isoformat(),
            }
            monthly_trends.append(area_per_month)
    #######################
    # 获取季度趋势
    start_trend_season_day, end_trend_season_day = get_last_n_season_period(today)
    # 生成各周范围列表
    seasons = create_season_list(start_trend_season_day.strftime('%Y-%m-%d'), end_trend_season_day.strftime('%Y-%m-%d'))

    seasonly_trends = []
    for k, v in brand_relatived_record.items():
        total_complaint_qty = 0
        total_maintenace_qty = 0

        for season in seasons:
            for eachday in v:
                # 选择周时间内的统计数据
                if not in_season(season, eachday.get('date')):
                    continue
                total_maintenace_qty += eachday.get('maintenaceQty')
                total_complaint_qty += eachday.get('complaintQty')
            area_per_season = {
                'countyCode': k[1],
                'cityCode': city_code,
                'maintenaceQty': total_maintenace_qty,
                'complaintQty': total_complaint_qty,
                'startPeriod': season[0].isoformat(),
                'endPeriod': season[1].isoformat(),
            }
            seasonly_trends.append(area_per_season)
#####################
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