# -*-coding:utf-8 -*-
from flask import request, jsonify, Blueprint
from pymongo import MongoClient
from app.base_class import CodeTable
from app.commontools import *

admin_bp = Blueprint('admin_bp', import_name=__name__)


@admin_bp.route(r'/commonapi/admin/statistics/query/', methods=['GET', 'POST'])
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


@admin_bp.route(r'/commonapi/admin/statistics/comments', methods=['GET', 'POST'])
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


@admin_bp.route(r'/commonapi/admin/statistics/complaints/total', methods=['GET','POST'])
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

    # 获取周趋势
    bias = calendar.weekday(today.year, today.month, today.day)
    start_trend_week_day = datetime(today.year, today.month, today.day, tzinfo=None) - timedelta(bias) - timedelta(
        6 * 7)
    end_trend_week_day = datetime(today.year, today.month, today.day, tzinfo=None) + timedelta(days=(6 - bias))
    # 生成各周范围列表
    weeks = create_week_list(start_trend_week_day.strftime('%Y-%m-%d'), end_trend_week_day.strftime('%Y-%m-%d'))
    weekly_trends = []
    for k, v in area_relatived_record.items():
        for week in weeks:
            total_complaint_qty = 0
            total_maintenace_qty = 0
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
                'periodStart': week[0].isoformat(),
                'periodEnd': week[1].isoformat(),
            }
            weekly_trends.append(area_per_week)
    # 获取月趋势
    start_trend_month_day, end_trend_month_day = get_last_n_month_period(today)
    # 生成各周范围列表
    months = create_month_list(start_trend_month_day.strftime('%Y-%m-%d'), end_trend_month_day.strftime('%Y-%m-%d'))
    monthly_trends = []
    for k, v in area_relatived_record.items():
        for month in months:
            total_complaint_qty = 0
            total_maintenace_qty = 0
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
                'periodStart': month[0].isoformat(),
                'periodEnd': month[1].isoformat(),
            }
            monthly_trends.append(area_per_month)
    # 获取季度趋势
    start_trend_season_day, end_trend_season_day = get_last_n_season_period(today)
    # 生成各周范围列表
    seasons = create_season_list(start_trend_season_day.strftime('%Y-%m-%d'), end_trend_season_day.strftime('%Y-%m-%d'))

    seasonly_trends = []
    for k, v in area_relatived_record.items():

        for season in seasons:
            total_complaint_qty = 0
            total_maintenace_qty = 0
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
                'periodStart': season[0].isoformat(),
                'periodEnd': season[1].isoformat(),
            }
            seasonly_trends.append(area_per_season)
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


@admin_bp.route(r'/commonapi/admin/statistics/comments/vehiclebrand', methods=['GET', 'POST'])
def vehicle_brand():
    """统计一段时间内各品牌的评价量"""

    today = datetime.today()
    city_code = request.args.get('citycode')
    selected_from = request.args.get('from')
    selected_to = request.args.get('to')
    if not city_code:
        return jsonify({'code': '400'}), 400

    mongo_client = MongoClient(host='127.0.0.1', port=27017)
    comments_brand = mongo_client.statistics.vehiclebrand.find({'cityCode': city_code})

    # 获取车辆品牌列表
    vehiclebrandlist = mongo_client.statistics.vehiclebrand.distinct('vehicleBrand')

    # 对数据进行品牌划分
    brand_relatived_record = {}
    for brand in vehiclebrandlist:
        statistics_list = []
        for tstats in comments_brand:
            if str(tstats.get('vehicleBrand')) == brand:
                statistics_list.append(tstats)
        brand_relatived_record[brand] = statistics_list

    if selected_from and selected_to:
        head = str_to_date(selected_from)
        tail = str_to_date(selected_to)
        if not head or not tail or head > tail:
            return jsonify({'code': 400}), 400
        # 统计，部分历史数据
        totaldata = []
        for k, v in brand_relatived_record.items():
            comments_num = 0  # 总数计数
            satisfied_num = 0  # 满意评论计数
            service_score = 0
            price_score = 0
            quality_score = 0
            envir_score = 0
            efficiency_score = 0
            all_comment = 0
            for eachday in v:
                if not in_period((head, tail), eachday.get('date')):
                    continue
                qty = eachday.get('commentsQty')
                comments_num += eachday.get('commentsQty')
                satisfied_num += eachday.get('satisfiedcommentsQty')
                service_score += eachday.get('serviceScore') * qty
                price_score += eachday.get('serviceScore') * qty
                quality_score += eachday.get('serviceScore') * qty
                envir_score += eachday.get('serviceScore') * qty
                efficiency_score += eachday.get('serviceScore') * qty
                all_comment += eachday.get('allComment') * qty
            if comments_num > 0:
                brand_data = {
                    'provinceCode': city_code[0:2] + '0000',
                    'cityCode': city_code,
                    'vehicleBrand': k,  # 品牌
                    'commentsQty': comments_num,
                    'satisfiedcommentsQty': satisfied_num,
                    'serviceScore': round(service_score / comments_num, 1),
                    'priceScore': round(price_score / comments_num, 1),
                    'qualityScore': round(quality_score / comments_num, 1),
                    'envirScore': round(envir_score / comments_num, 1),
                    'efficiencyScore': round(efficiency_score / comments_num, 1),
                    'allComment': round(all_comment / comments_num, 1),
                }
            else:
                brand_data = {
                    'provinceCode': city_code[0:2] + '0000',
                    'cityCode': city_code,
                    'vehicleBrand': k,  # 品牌
                    'commentsQty': comments_num,  # 维修量
                    'satisfiedcommentsQty': satisfied_num,  # 满意评价数
                    'serviceScore': 0,
                    'priceScore': 0,
                    'qualityScore': 0,
                    'envirScore': 0,
                    'efficiencyScore': 0,
                    'allComment': 0,
                }
            totaldata.append(brand_data)
    else:
        # 统计，全部历史数据
        totaldata = []
        for k, v in brand_relatived_record.items():
            comments_num = 0  # 总数计数
            satisfied_num = 0  # 满意评论计数
            service_score = 0
            price_score = 0
            quality_score = 0
            envir_score = 0
            efficiency_score = 0
            all_comment = 0
            for eachday in v:
                qty = eachday.get('commentsQty')
                comments_num += eachday.get('commentsQty')
                satisfied_num += eachday.get('satisfiedcommentsQty')
                service_score += eachday.get('serviceScore') * qty
                price_score += eachday.get('serviceScore') * qty
                quality_score += eachday.get('serviceScore') * qty
                envir_score += eachday.get('serviceScore') * qty
                efficiency_score += eachday.get('serviceScore') * qty
                all_comment += eachday.get('allComment') * qty
            if comments_num > 0:
                brand_data = {
                    'provinceCode': city_code[0:2] + '0000',
                    'cityCode': city_code,
                    'vehicleBrand': k,  # 品牌
                    'commentsQty': comments_num,
                    'satisfiedcommentsQty': satisfied_num,
                    'serviceScore': round(service_score / comments_num, 1),
                    'priceScore': round(price_score / comments_num, 1),
                    'qualityScore': round(quality_score / comments_num, 1),
                    'envirScore': round(envir_score / comments_num, 1),
                    'efficiencyScore': round(efficiency_score / comments_num, 1),
                    'allComment': round(all_comment / comments_num, 1),
                }
            else:
                brand_data = {
                    'provinceCode': city_code[0:2] + '0000',
                    'cityCode': city_code,
                    'vehicleBrand': k,  # 品牌
                    'commentsQty': comments_num,
                    'satisfiedcommentsQty': satisfied_num,
                    'serviceScore': 0,
                    'priceScore': 0,
                    'qualityScore': 0,
                    'envirScore': 0,
                    'efficiencyScore': 0,
                    'allComment': 0,
                }
            totaldata.append(brand_data)
    # 上一周
    bias = calendar.weekday(today.year, today.month, today.day)
    start_week_day = datetime(today.year, today.month, today.day, tzinfo=None) - timedelta(bias + 7)
    end_week_day = start_week_day + timedelta(days=6)

    lastweek = []
    for k, v in brand_relatived_record.items():
        comments_num = 0  # 总数计数
        satisfied_num = 0  # 满意评论计数
        service_score = 0
        price_score = 0
        quality_score = 0
        envir_score = 0
        efficiency_score = 0
        all_comment = 0
        for eachday in v:
            if not in_week((start_week_day, end_week_day), eachday.get('date')):
                continue
            qty = eachday.get('commentsQty')
            comments_num += qty
            satisfied_num += eachday.get('satisfiedcommentsQty')
            service_score += eachday.get('serviceScore') * qty
            price_score += eachday.get('serviceScore') * qty
            quality_score += eachday.get('serviceScore') * qty
            envir_score += eachday.get('serviceScore') * qty
            efficiency_score += eachday.get('serviceScore') * qty
            all_comment += eachday.get('allComment') * qty
        if comments_num > 0:
            brand_data = {
                'provinceCode': city_code[0:2] + '0000',
                'cityCode': city_code,
                'vehicleBrand': k,  # 品牌
                'commentsQty': comments_num,
                'satisfiedcommentsQty': satisfied_num,
                'serviceScore': round(service_score / comments_num, 1),
                'priceScore': round(price_score / comments_num, 1),
                'qualityScore': round(quality_score / comments_num, 1),
                'envirScore': round(envir_score / comments_num, 1),
                'efficiencyScore': round(efficiency_score / comments_num, 1),
                'allComment': round(all_comment / comments_num, 1),
            }
        else:
            brand_data = {
                'provinceCode': city_code[0:2] + '0000',
                'cityCode': city_code,
                'vehicleBrand': k,  # 品牌
                'commentsQty': comments_num,
                'satisfiedcommentsQty': satisfied_num,
                'serviceScore': 0,
                'priceScore': 0,
                'qualityScore': 0,
                'envirScore': 0,
                'efficiencyScore': 0,
                'allComment': 0,
            }
        lastweek.append(brand_data)

    # 上一月
    start_last_month, end_last_month = get_last_month_period(today)
    lastmonth = []
    for k, v in brand_relatived_record.items():
        comments_num = 0  # 总数计数
        satisfied_num = 0  # 满意评论计数
        service_score = 0
        price_score = 0
        quality_score = 0
        envir_score = 0
        efficiency_score = 0
        all_comment = 0
        for eachday in v:
            if not in_month((start_last_month, end_last_month), eachday.get('date')):
                continue
            qty = eachday.get('commentsQty')
            comments_num += qty
            satisfied_num += eachday.get('satisfiedcommentsQty')
            service_score += eachday.get('serviceScore') * qty
            price_score += eachday.get('serviceScore') * qty
            quality_score += eachday.get('serviceScore') * qty
            envir_score += eachday.get('serviceScore') * qty
            efficiency_score += eachday.get('serviceScore') * qty
            all_comment += eachday.get('allComment') * qty
        if comments_num > 0:
            brand_data = {
                'provinceCode': city_code[0:2] + '0000',
                'cityCode': city_code,
                'vehicleBrand': k,  # 品牌
                'commentsQty': comments_num,
                'satisfiedcommentsQty': satisfied_num,
                'serviceScore': round(service_score / comments_num, 1),
                'priceScore': round(price_score / comments_num, 1),
                'qualityScore': round(quality_score / comments_num, 1),
                'envirScore': round(envir_score / comments_num, 1),
                'efficiencyScore': round(efficiency_score / comments_num, 1),
                'allComment': round(all_comment / comments_num, 1),
            }
        else:
            brand_data = {
                'provinceCode': city_code[0:2] + '0000',
                'cityCode': city_code,
                'vehicleBrand': k,  # 品牌
                'commentsQty': comments_num,
                'satisfiedcommentsQty': satisfied_num,
                'serviceScore': 0,
                'priceScore': 0,
                'qualityScore': 0,
                'envirScore': 0,
                'efficiencyScore': 0,
                'allComment': 0,
            }
        lastmonth.append(brand_data)
    # 上一季度
    start_season_day, end_season_day = get_last_season_period(today)
    lastseason = []
    for k, v in brand_relatived_record.items():
        comments_num = 0  # 总数计数
        satisfied_num = 0  # 满意评论计数
        service_score = 0
        price_score = 0
        quality_score = 0
        envir_score = 0
        efficiency_score = 0
        all_comment = 0
        for eachday in v:
            # 选择上周时间内的统计数据
            if not in_season((start_season_day, end_season_day), eachday.get('date')):
                continue
            qty = eachday.get('commentsQty')
            comments_num += qty
            satisfied_num += eachday.get('satisfiedcommentsQty')
            service_score += eachday.get('serviceScore') * qty
            price_score += eachday.get('serviceScore') * qty
            quality_score += eachday.get('serviceScore') * qty
            envir_score += eachday.get('serviceScore') * qty
            efficiency_score += eachday.get('serviceScore') * qty
            all_comment += eachday.get('allComment') * qty
        if comments_num > 0:
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
        else:
            brand_data = {
                'provinceCode': city_code[0:2] + '0000',
                'cityCode': city_code,
                'vehicleBrand': k,  # 品牌
                'commentsQty': comments_num,  # 维修量
                'satisfiedcommentsQty': satisfied_num,  # 满意评价数
                'serviceScore': 0,
                'priceScore': 0,
                'qualityScore': 0,
                'envirScore': 0,
                'efficiencyScore': 0,
                'allComment': 0,
            }
        lastseason.append(brand_data)
    # 获取周趋势
    bias = calendar.weekday(today.year, today.month, today.day)
    start_trend_week_day = datetime(today.year, today.month, today.day, tzinfo=None) - timedelta(bias) - timedelta(
        6 * 7)
    end_trend_week_day = datetime(today.year, today.month, today.day, tzinfo=None) + timedelta(days=(6 - bias))
    weeks = create_week_list(start_trend_week_day.strftime('%Y-%m-%d'), end_trend_week_day.strftime('%Y-%m-%d'))
    weekly_trends = []
    for k, v in brand_relatived_record.items():
        for week in weeks:
            comments_num = 0  # 总数计数
            satisfied_num = 0  # 满意评价计数
            service_score = 0
            price_score = 0
            quality_score = 0
            envir_score = 0
            efficiency_score = 0
            all_comment = 0
            for eachday in v:
                if not in_week(week, eachday.get('date')):
                    continue
                qty = eachday.get('commentsQty')
                comments_num += qty
                satisfied_num += eachday.get('satisfiedcommentsQty')
                service_score += eachday.get('serviceScore') * qty
                price_score += eachday.get('serviceScore') * qty
                quality_score += eachday.get('serviceScore') * qty
                envir_score += eachday.get('serviceScore') * qty
                efficiency_score += eachday.get('serviceScore') * qty
                all_comment += eachday.get('allComment') * qty
            if comments_num > 0:
                brand_per_week = {
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
                    'periodStart': week[0].isoformat(),
                    'periodEnd': week[1].isoformat(),
                }
            else:
                brand_per_week = {
                    'provinceCode': city_code[0:2] + '0000',
                    'cityCode': city_code,
                    'vehicleBrand': k,  # 品牌
                    'commentsQty': comments_num,  # 维修量
                    'satisfiedcommentsQty': satisfied_num,  # 满意评价数
                    'serviceScore': 0,
                    'priceScore': 0,
                    'qualityScore': 0,
                    'envirScore': 0,
                    'efficiencyScore': 0,
                    'allComment': 0,
                    'periodStart': week[0].isoformat(),
                    'periodEnd': week[1].isoformat(),
                }
            weekly_trends.append(brand_per_week)
    # 获取月趋势
    start_trend_month_day, end_trend_month_day = get_last_n_month_period(today)
    months = create_month_list(start_trend_month_day.strftime('%Y-%m-%d'), end_trend_month_day.strftime('%Y-%m-%d'))
    monthly_trends = []
    for k, v in brand_relatived_record.items():
        for month in months:
            comments_num = 0  # 总数计数
            satisfied_num = 0  # 满意评论计数
            service_score = 0
            price_score = 0
            quality_score = 0
            envir_score = 0
            efficiency_score = 0
            all_comment = 0
            for eachday in v:
                if not in_month(month, eachday.get('date')):
                    continue
                qty = eachday.get('commentsQty')
                comments_num += qty
                satisfied_num += eachday.get('satisfiedcommentsQty')
                service_score += eachday.get('serviceScore') * qty
                price_score += eachday.get('serviceScore') * qty
                quality_score += eachday.get('serviceScore') * qty
                envir_score += eachday.get('serviceScore') * qty
                efficiency_score += eachday.get('serviceScore') * qty
                all_comment += eachday.get('allComment') * qty
            if comments_num > 0:

                brand_per_month = {
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
                    'periodStart': month[0].isoformat(),
                    'periodEnd': month[1].isoformat(),
                }
            else:
                brand_per_month = {
                    'provinceCode': city_code[0:2] + '0000',
                    'cityCode': city_code,
                    'vehicleBrand': k,  # 品牌
                    'commentsQty': comments_num,  # 维修量
                    'satisfiedcommentsQty': satisfied_num,  # 满意评价数
                    'serviceScore': 0,
                    'priceScore': 0,
                    'qualityScore': 0,
                    'envirScore': 0,
                    'efficiencyScore': 0,
                    'allComment': 0,
                    'periodStart': month[0].isoformat(),
                    'periodEnd': month[1].isoformat(),
                }
            monthly_trends.append(brand_per_month)
    # 获取季度趋势
    start_trend_season_day, end_trend_season_day = get_last_n_season_period(today)
    seasons = create_season_list(start_trend_season_day.strftime('%Y-%m-%d'), end_trend_season_day.strftime('%Y-%m-%d'))
    seasonly_trends = []
    for k, v in brand_relatived_record.items():
        for season in seasons:
            comments_num = 0  # 总数计数
            satisfied_num = 0  # 满意评论计数
            service_score = 0
            price_score = 0
            quality_score = 0
            envir_score = 0
            efficiency_score = 0
            all_comment = 0
            for eachday in v:
                if not in_season(season, eachday.get('date')):
                    continue
                qty = eachday.get('commentsQty')
                comments_num += qty
                satisfied_num += eachday.get('satisfiedcommentsQty')
                service_score += eachday.get('serviceScore') * qty
                price_score += eachday.get('serviceScore') * qty
                quality_score += eachday.get('serviceScore') * qty
                envir_score += eachday.get('serviceScore') * qty
                efficiency_score += eachday.get('serviceScore') * qty
                all_comment += eachday.get('allComment') * qty
            if comments_num > 0:
                brand_per_season = {
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
                    'periodStart': season[0].isoformat(),
                    'periodEnd': season[1].isoformat(),
                }
            else:
                brand_per_season = {
                    'provinceCode': city_code[0:2] + '0000',
                    'cityCode': city_code,
                    'vehicleBrand': k,  # 品牌
                    'commentsQty': comments_num,  # 维修量
                    'satisfiedcommentsQty': satisfied_num,  # 满意评价数
                    'serviceScore': 0,
                    'priceScore': 0,
                    'qualityScore': 0,
                    'envirScore': 0,
                    'efficiencyScore': 0,
                    'allComment': 0,
                    'periodStart': season[0].isoformat(),
                    'periodEnd': season[1].isoformat(),
                }
            seasonly_trends.append(brand_per_season)
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


@admin_bp.route(r'/commonapi/admin/statistics/comments/vehicletype', methods=['GET', 'POST'])
def vehicle_type():
    """统计一段时间内各车辆类型的评价量"""

    today = datetime.today()
    city_code = request.args.get('citycode')
    if not city_code:
        return jsonify({'code': '400'}), 400

    mongo_client = MongoClient(host='127.0.0.1', port=27017)
    comments_type = mongo_client.statistics.vehicletype.find({'cityCode': city_code})

    # 获取车辆类型列表
    vehicletypelist = [
        ['小型车', 1],
        ['大中型客车', 2],
        ['大型货车', 3],
        ['其它', 9],
    ]
    # 对数据进行品牌划分
    type_relatived_record = {}
    for brand in vehicletypelist:
        statistics_list = []
        for tstats in comments_type:
            if tstats.get('vehicleType') == brand[1]:
                statistics_list.append(tstats)
        type_relatived_record[(brand[0], brand[1])] = statistics_list

    # 统计，全部历史数据
    totaldata = []
    for k, v in type_relatived_record.items():
        comments_num = 0  # 总数计数
        satisfied_num = 0  # 满意评论计数
        service_score = 0
        price_score = 0
        quality_score = 0
        envir_score = 0
        efficiency_score = 0
        all_comment = 0
        for eachday in v:
            qty = eachday.get('commentsQty')
            comments_num += eachday.get('commentsQty')
            satisfied_num += eachday.get('satisfiedcommentsQty')
            service_score += eachday.get('serviceScore') * qty
            price_score += eachday.get('serviceScore') * qty
            quality_score += eachday.get('serviceScore') * qty
            envir_score += eachday.get('serviceScore') * qty
            efficiency_score += eachday.get('serviceScore') * qty
            all_comment += eachday.get('allComment') * qty
        if comments_num > 0:
            type_data = {
                'provinceCode': city_code[0:2] + '0000',
                'cityCode': city_code,
                'vehicleType': k[1],
                'commentsQty': comments_num,  # 维修量
                'satisfiedcommentsQty': satisfied_num,  # 满意评价数
                'serviceScore': round(service_score / comments_num, 1),
                'priceScore': round(price_score / comments_num, 1),
                'qualityScore': round(quality_score / comments_num, 1),
                'envirScore': round(envir_score / comments_num, 1),
                'efficiencyScore': round(efficiency_score / comments_num, 1),
                'allComment': round(all_comment / comments_num, 1),
            }
        else:
            type_data = {
                'provinceCode': city_code[0:2] + '0000',
                'cityCode': city_code,
                'vehicleType': k[1],
                'commentsQty': comments_num,  # 维修量
                'satisfiedcommentsQty': satisfied_num,  # 满意评价数
                'serviceScore': 0,
                'priceScore': 0,
                'qualityScore': 0,
                'envirScore': 0,
                'efficiencyScore': 0,
                'allComment': 0,
            }
        totaldata.append(type_data)
    # 上一周
    bias = calendar.weekday(today.year, today.month, today.day)
    start_week_day = datetime(today.year, today.month, today.day, tzinfo=None) - timedelta(bias + 7)
    end_week_day = start_week_day + timedelta(days=6)

    lastweek = []
    for k, v in type_relatived_record.items():
        comments_num = 0  # 总数计数
        satisfied_num = 0  # 满意评论计数
        service_score = 0
        price_score = 0
        quality_score = 0
        envir_score = 0
        efficiency_score = 0
        all_comment = 0
        for eachday in v:
            if not in_week((start_week_day, end_week_day), eachday.get('date')):
                continue
            qty = eachday.get('commentsQty')
            comments_num += qty
            satisfied_num += eachday.get('satisfiedcommentsQty')
            service_score += eachday.get('serviceScore') * qty
            price_score += eachday.get('serviceScore') * qty
            quality_score += eachday.get('serviceScore') * qty
            envir_score += eachday.get('serviceScore') * qty
            efficiency_score += eachday.get('serviceScore') * qty
            all_comment += eachday.get('allComment') * qty
        if comments_num > 0:
            type_data = {
                'provinceCode': city_code[0:2] + '0000',
                'cityCode': city_code,
                'vehicleBrand': k[1],  # 品牌
                'commentsQty': comments_num,  # 维修量
                'satisfiedcommentsQty': satisfied_num,  # 满意评价数
                'serviceScore': round(service_score / comments_num, 1),
                'priceScore': round(price_score / comments_num, 1),
                'qualityScore': round(quality_score / comments_num, 1),
                'envirScore': round(envir_score / comments_num, 1),
                'efficiencyScore': round(efficiency_score / comments_num, 1),
                'allComment': round(all_comment / comments_num, 1),
            }
        else:
            type_data = {
                'provinceCode': city_code[0:2] + '0000',
                'cityCode': city_code,
                'vehicleBrand': k[1],
                'commentsQty': comments_num,
                'satisfiedcommentsQty': satisfied_num,
                'serviceScore': 0,
                'priceScore': 0,
                'qualityScore': 0,
                'envirScore': 0,
                'efficiencyScore': 0,
                'allComment': 0,
            }
        lastweek.append(type_data)
    # 上一月
    start_last_month, end_last_month = get_last_month_period(today)
    lastmonth = []
    for k, v in type_relatived_record.items():
        comments_num = 0  # 总数计数
        satisfied_num = 0  # 满意评论计数
        service_score = 0
        price_score = 0
        quality_score = 0
        envir_score = 0
        efficiency_score = 0
        all_comment = 0
        for eachday in v:
            if not in_month((start_last_month, end_last_month), eachday.get('date')):
                continue
            qty = eachday.get('commentsQty')
            comments_num += qty
            satisfied_num += eachday.get('satisfiedcommentsQty')
            service_score += eachday.get('serviceScore') * qty
            price_score += eachday.get('serviceScore') * qty
            quality_score += eachday.get('serviceScore') * qty
            envir_score += eachday.get('serviceScore') * qty
            efficiency_score += eachday.get('serviceScore') * qty
            all_comment += eachday.get('allComment') * qty
        if comments_num > 0:
            type_data = {
                'provinceCode': city_code[0:2] + '0000',
                'cityCode': city_code,
                'vehicleType': k[1],
                'commentsQty': comments_num,
                'satisfiedcommentsQty': satisfied_num,
                'serviceScore': round(service_score / comments_num, 1),
                'priceScore': round(price_score / comments_num, 1),
                'qualityScore': round(quality_score / comments_num, 1),
                'envirScore': round(envir_score / comments_num, 1),
                'efficiencyScore': round(efficiency_score / comments_num, 1),
                'allComment': round(all_comment / comments_num, 1),
            }
        else:
            type_data = {
                'provinceCode': city_code[0:2] + '0000',
                'cityCode': city_code,
                'vehicleType': k[1],
                'commentsQty': comments_num,
                'satisfiedcommentsQty': satisfied_num,
                'serviceScore': 0,
                'priceScore': 0,
                'qualityScore': 0,
                'envirScore': 0,
                'efficiencyScore': 0,
                'allComment': 0,
            }
        lastmonth.append(type_data)
    # 上一季度
    start_season_day, end_season_day = get_last_season_period(today)
    lastseason = []
    for k, v in type_relatived_record.items():
        comments_num = 0  # 总数计数
        satisfied_num = 0  # 满意评论计数
        service_score = 0
        price_score = 0
        quality_score = 0
        envir_score = 0
        efficiency_score = 0
        all_comment = 0
        for eachday in v:
            # 选择上周时间内的统计数据
            if not in_season((start_season_day, end_season_day), eachday.get('date')):
                continue
            qty = eachday.get('commentsQty')
            comments_num += qty
            satisfied_num += eachday.get('satisfiedcommentsQty')
            service_score += eachday.get('serviceScore') * qty
            price_score += eachday.get('serviceScore') * qty
            quality_score += eachday.get('serviceScore') * qty
            envir_score += eachday.get('serviceScore') * qty
            efficiency_score += eachday.get('serviceScore') * qty
            all_comment += eachday.get('allComment') * qty
        if comments_num > 0:
            type_data = {
                'provinceCode': city_code[0:2] + '0000',
                'cityCode': city_code,
                'vehicleType': k[1],
                'commentsQty': comments_num,
                'satisfiedcommentsQty': satisfied_num,
                'serviceScore': round(service_score / comments_num, 1),
                'priceScore': round(price_score / comments_num, 1),
                'qualityScore': round(quality_score / comments_num, 1),
                'envirScore': round(envir_score / comments_num, 1),
                'efficiencyScore': round(efficiency_score / comments_num, 1),
                'allComment': round(all_comment / comments_num, 1),
            }
        else:
            type_data = {
                'provinceCode': city_code[0:2] + '0000',
                'cityCode': city_code,
                'vehicleType': k[1],
                'commentsQty': comments_num,
                'satisfiedcommentsQty': satisfied_num,
                'serviceScore': 0,
                'priceScore': 0,
                'qualityScore': 0,
                'envirScore': 0,
                'efficiencyScore': 0,
                'allComment': 0,
            }
        lastseason.append(type_data)
    # 获取周趋势
    bias = calendar.weekday(today.year, today.month, today.day)
    start_trend_week_day = datetime(today.year, today.month, today.day, tzinfo=None) - timedelta(bias) - timedelta(
        6 * 7)
    end_trend_week_day = datetime(today.year, today.month, today.day, tzinfo=None) + timedelta(days=(6 - bias))
    weeks = create_week_list(start_trend_week_day.strftime('%Y-%m-%d'), end_trend_week_day.strftime('%Y-%m-%d'))
    weekly_trends = []
    for k, v in type_relatived_record.items():
        for week in weeks:
            comments_num = 0  # 总数计数
            satisfied_num = 0  # 满意评价计数
            service_score = 0
            price_score = 0
            quality_score = 0
            envir_score = 0
            efficiency_score = 0
            all_comment = 0
            for eachday in v:
                if not in_week(week, eachday.get('date')):
                    continue
                qty = eachday.get('commentsQty')
                comments_num += qty
                satisfied_num += eachday.get('satisfiedcommentsQty')
                service_score += eachday.get('serviceScore') * qty
                price_score += eachday.get('serviceScore') * qty
                quality_score += eachday.get('serviceScore') * qty
                envir_score += eachday.get('serviceScore') * qty
                efficiency_score += eachday.get('serviceScore') * qty
                all_comment += eachday.get('allComment') * qty
            if comments_num > 0:
                type_per_week = {
                    'provinceCode': city_code[0:2] + '0000',
                    'cityCode': city_code,
                    'vehicleType': k[1],
                    'commentsQty': comments_num,
                    'satisfiedcommentsQty': satisfied_num,
                    'serviceScore': round(service_score / comments_num, 1),
                    'priceScore': round(price_score / comments_num, 1),
                    'qualityScore': round(quality_score / comments_num, 1),
                    'envirScore': round(envir_score / comments_num, 1),
                    'efficiencyScore': round(efficiency_score / comments_num, 1),
                    'allComment': round(all_comment / comments_num, 1),
                    'periodStart': week[0].isoformat(),
                    'periodEnd': week[1].isoformat(),
                }
            else:
                type_per_week = {
                    'provinceCode': city_code[0:2] + '0000',
                    'cityCode': city_code,
                    'vehicleType': k[1],
                    'commentsQty': comments_num,
                    'satisfiedcommentsQty': satisfied_num,
                    'serviceScore': 0,
                    'priceScore': 0,
                    'qualityScore': 0,
                    'envirScore': 0,
                    'efficiencyScore': 0,
                    'allComment': 0,
                    'periodStart': week[0].isoformat(),
                    'periodEnd': week[1].isoformat(),
                }
            weekly_trends.append(type_per_week)
    # 获取月趋势
    start_trend_month_day, end_trend_month_day = get_last_n_month_period(today)
    months = create_month_list(start_trend_month_day.strftime('%Y-%m-%d'), end_trend_month_day.strftime('%Y-%m-%d'))
    monthly_trends = []
    for k, v in type_relatived_record.items():
        for month in months:
            comments_num = 0  # 总数计数
            satisfied_num = 0  # 满意评论计数
            service_score = 0
            price_score = 0
            quality_score = 0
            envir_score = 0
            efficiency_score = 0
            all_comment = 0
            for eachday in v:
                # 选择周时间内的统计数据
                if not in_month(month, eachday.get('date')):
                    continue
                qty = eachday.get('commentsQty')
                comments_num += qty
                satisfied_num += eachday.get('satisfiedcommentsQty')
                service_score += eachday.get('serviceScore') * qty
                price_score += eachday.get('serviceScore') * qty
                quality_score += eachday.get('serviceScore') * qty
                envir_score += eachday.get('serviceScore') * qty
                efficiency_score += eachday.get('serviceScore') * qty
                all_comment += eachday.get('allComment') * qty
            if comments_num > 0:

                brand_per_month = {
                    'provinceCode': city_code[0:2] + '0000',
                    'cityCode': city_code,
                    'vehicleType': k[1],
                    'commentsQty': comments_num,
                    'satisfiedcommentsQty': satisfied_num,
                    'serviceScore': round(service_score / comments_num, 1),
                    'priceScore': round(price_score / comments_num, 1),
                    'qualityScore': round(quality_score / comments_num, 1),
                    'envirScore': round(envir_score / comments_num, 1),
                    'efficiencyScore': round(efficiency_score / comments_num, 1),
                    'allComment': round(all_comment / comments_num, 1),
                    'periodStart': month[0].isoformat(),
                    'periodEnd': month[1].isoformat(),
                }
            else:
                brand_per_month = {
                    'provinceCode': city_code[0:2] + '0000',
                    'cityCode': city_code,
                    'vehicleType': k[1],  # 品牌
                    'commentsQty': comments_num,  # 维修量
                    'satisfiedcommentsQty': satisfied_num,  # 满意评价数
                    'serviceScore': 0,
                    'priceScore': 0,
                    'qualityScore': 0,
                    'envirScore': 0,
                    'efficiencyScore': 0,
                    'allComment': 0,
                    'periodStart': month[0].isoformat(),
                    'periodEnd': month[1].isoformat(),
                }
            monthly_trends.append(brand_per_month)
    # 获取季度趋势
    start_trend_season_day, end_trend_season_day = get_last_n_season_period(today)
    seasons = create_season_list(start_trend_season_day.strftime('%Y-%m-%d'),
                                 end_trend_season_day.strftime('%Y-%m-%d'))
    seasonly_trends = []
    for k, v in type_relatived_record.items():
        for season in seasons:
            comments_num = 0
            satisfied_num = 0
            service_score = 0
            price_score = 0
            quality_score = 0
            envir_score = 0
            efficiency_score = 0
            all_comment = 0
            for eachday in v:
                if not in_season(season, eachday.get('date')):
                    continue
                qty = eachday.get('commentsQty')
                comments_num += qty
                satisfied_num += eachday.get('satisfiedcommentsQty')
                service_score += eachday.get('serviceScore') * qty
                price_score += eachday.get('serviceScore') * qty
                quality_score += eachday.get('serviceScore') * qty
                envir_score += eachday.get('serviceScore') * qty
                efficiency_score += eachday.get('serviceScore') * qty
                all_comment += eachday.get('allComment') * qty
            if comments_num > 0:
                type_per_season = {
                    'provinceCode': city_code[0:2] + '0000',
                    'cityCode': city_code,
                    'vehicleType': k[1],
                    'commentsQty': comments_num,
                    'satisfiedcommentsQty': satisfied_num,
                    'serviceScore': round(service_score / comments_num, 1),
                    'priceScore': round(price_score / comments_num, 1),
                    'qualityScore': round(quality_score / comments_num, 1),
                    'envirScore': round(envir_score / comments_num, 1),
                    'efficiencyScore': round(efficiency_score / comments_num, 1),
                    'allComment': round(all_comment / comments_num, 1),
                    'periodStart': season[0].isoformat(),
                    'periodEnd': season[1].isoformat(),
                }
            else:
                type_per_season = {
                    'provinceCode': city_code[0:2] + '0000',
                    'cityCode': city_code,
                    'vehicleType': k[1],
                    'commentsQty': comments_num,
                    'satisfiedcommentsQty': satisfied_num,
                    'serviceScore': 0,
                    'priceScore': 0,
                    'qualityScore': 0,
                    'envirScore': 0,
                    'efficiencyScore': 0,
                    'allComment': 0,
                    'periodStart': season[0].isoformat(),
                    'periodEnd': season[1].isoformat(),
                }
            seasonly_trends.append(type_per_season)
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


@admin_bp.route(r'/commonapi/admin/statistics/comments/county', methods=['GET', 'POST'])
def county():
    """统计一段时间内各车辆类型的评价量"""

    today = datetime.today()
    city_code = request.args.get('citycode')
    if not city_code:
        return jsonify({'code': '400'}), 400

    mongo_client = MongoClient(host='127.0.0.1', port=27017)
    comments_type = mongo_client.statistics.vehicletype.find({'cityCode': city_code})

    # 获取辖区列表
    province_code_abbr = city_code[0:2]
    city_code_abbr = city_code[2:4]
    codetable = CodeTable()
    countylist = codetable.get_belong_county_info(province_code_abbr, city_code_abbr)  # 获取市内区域代码列表

    # 对数据进行品牌划分
    area_relatived_record = {}
    for _county in countylist:
        statistics_list = []
        for tstats in comments_type:
            if tstats.get('countyCode') == _county[1]:
                statistics_list.append(tstats)
        area_relatived_record[(_county[0], _county[1])] = statistics_list

    # 统计，全部历史数据
    totaldata = []
    for k, v in area_relatived_record.items():
        comments_num = 0  # 总数计数
        satisfied_num = 0  # 满意评论计数
        service_score = 0
        price_score = 0
        quality_score = 0
        envir_score = 0
        efficiency_score = 0
        all_comment = 0
        for eachday in v:
            qty = eachday.get('commentsQty')
            comments_num += eachday.get('commentsQty')
            satisfied_num += eachday.get('satisfiedcommentsQty')
            service_score += eachday.get('serviceScore') * qty
            price_score += eachday.get('serviceScore') * qty
            quality_score += eachday.get('serviceScore') * qty
            envir_score += eachday.get('serviceScore') * qty
            efficiency_score += eachday.get('serviceScore') * qty
            all_comment += eachday.get('allComment') * qty
        if comments_num > 0:
            area_data = {
                'provinceCode': city_code[0:2] + '0000',
                'cityCode': city_code,
                'countyCode': k[1],
                'commentsQty': comments_num,  # 维修量
                'satisfiedcommentsQty': satisfied_num,  # 满意评价数
                'serviceScore': round(service_score / comments_num, 1),
                'priceScore': round(price_score / comments_num, 1),
                'qualityScore': round(quality_score / comments_num, 1),
                'envirScore': round(envir_score / comments_num, 1),
                'efficiencyScore': round(efficiency_score / comments_num, 1),
                'allComment': round(all_comment / comments_num, 1),
            }
        else:
            area_data = {
                'provinceCode': city_code[0:2] + '0000',
                'cityCode': city_code,
                'countyCode': k[1],
                'commentsQty': comments_num,  # 维修量
                'satisfiedcommentsQty': satisfied_num,  # 满意评价数
                'serviceScore': 0,
                'priceScore': 0,
                'qualityScore': 0,
                'envirScore': 0,
                'efficiencyScore': 0,
                'allComment': 0,
            }
        totaldata.append(area_data)
    # 上一周
    bias = calendar.weekday(today.year, today.month, today.day)
    start_week_day = datetime(today.year, today.month, today.day, tzinfo=None) - timedelta(bias + 7)
    end_week_day = start_week_day + timedelta(days=6)

    lastweek = []
    for k, v in area_relatived_record.items():
        comments_num = 0  # 总数计数
        satisfied_num = 0  # 满意评论计数
        service_score = 0
        price_score = 0
        quality_score = 0
        envir_score = 0
        efficiency_score = 0
        all_comment = 0
        for eachday in v:
            if not in_week((start_week_day, end_week_day), eachday.get('date')):
                continue
            qty = eachday.get('commentsQty')
            comments_num += qty
            satisfied_num += eachday.get('satisfiedcommentsQty')
            service_score += eachday.get('serviceScore') * qty
            price_score += eachday.get('serviceScore') * qty
            quality_score += eachday.get('serviceScore') * qty
            envir_score += eachday.get('serviceScore') * qty
            efficiency_score += eachday.get('serviceScore') * qty
            all_comment += eachday.get('allComment') * qty
        if comments_num > 0:
            area_data = {
                'provinceCode': city_code[0:2] + '0000',
                'cityCode': city_code,
                'countyCode': k[1],
                'commentsQty': comments_num,  # 维修量
                'satisfiedcommentsQty': satisfied_num,  # 满意评价数
                'serviceScore': round(service_score / comments_num, 1),
                'priceScore': round(price_score / comments_num, 1),
                'qualityScore': round(quality_score / comments_num, 1),
                'envirScore': round(envir_score / comments_num, 1),
                'efficiencyScore': round(efficiency_score / comments_num, 1),
                'allComment': round(all_comment / comments_num, 1),
            }
        else:
            area_data = {
                'provinceCode': city_code[0:2] + '0000',
                'cityCode': city_code,
                'countyCode': k[1],
                'commentsQty': comments_num,
                'satisfiedcommentsQty': satisfied_num,
                'serviceScore': 0,
                'priceScore': 0,
                'qualityScore': 0,
                'envirScore': 0,
                'efficiencyScore': 0,
                'allComment': 0,
            }
        lastweek.append(area_data)
    # 上一月
    start_last_month, end_last_month = get_last_month_period(today)
    lastmonth = []
    for k, v in area_relatived_record.items():
        comments_num = 0  # 总数计数
        satisfied_num = 0  # 满意评论计数
        service_score = 0
        price_score = 0
        quality_score = 0
        envir_score = 0
        efficiency_score = 0
        all_comment = 0
        for eachday in v:
            if not in_month((start_last_month, end_last_month), eachday.get('date')):
                continue
            qty = eachday.get('commentsQty')
            comments_num += qty
            satisfied_num += eachday.get('satisfiedcommentsQty')
            service_score += eachday.get('serviceScore') * qty
            price_score += eachday.get('serviceScore') * qty
            quality_score += eachday.get('serviceScore') * qty
            envir_score += eachday.get('serviceScore') * qty
            efficiency_score += eachday.get('serviceScore') * qty
            all_comment += eachday.get('allComment') * qty
        if comments_num > 0:
            area_data = {
                'provinceCode': city_code[0:2] + '0000',
                'cityCode': city_code,
                'countyCode': k[1],
                'commentsQty': comments_num,
                'satisfiedcommentsQty': satisfied_num,
                'serviceScore': round(service_score / comments_num, 1),
                'priceScore': round(price_score / comments_num, 1),
                'qualityScore': round(quality_score / comments_num, 1),
                'envirScore': round(envir_score / comments_num, 1),
                'efficiencyScore': round(efficiency_score / comments_num, 1),
                'allComment': round(all_comment / comments_num, 1),
            }
        else:
            area_data = {
                'provinceCode': city_code[0:2] + '0000',
                'cityCode': city_code,
                'countyCode': k[1],
                'commentsQty': comments_num,
                'satisfiedcommentsQty': satisfied_num,
                'serviceScore': 0,
                'priceScore': 0,
                'qualityScore': 0,
                'envirScore': 0,
                'efficiencyScore': 0,
                'allComment': 0,
            }
        lastmonth.append(area_data)
    # 上一季度
    start_season_day, end_season_day = get_last_season_period(today)
    lastseason = []
    for k, v in area_relatived_record.items():
        comments_num = 0  # 总数计数
        satisfied_num = 0  # 满意评论计数
        service_score = 0
        price_score = 0
        quality_score = 0
        envir_score = 0
        efficiency_score = 0
        all_comment = 0
        for eachday in v:
            # 选择上周时间内的统计数据
            if not in_season((start_season_day, end_season_day), eachday.get('date')):
                continue
            qty = eachday.get('commentsQty')
            comments_num += qty
            satisfied_num += eachday.get('satisfiedcommentsQty')
            service_score += eachday.get('serviceScore') * qty
            price_score += eachday.get('serviceScore') * qty
            quality_score += eachday.get('serviceScore') * qty
            envir_score += eachday.get('serviceScore') * qty
            efficiency_score += eachday.get('serviceScore') * qty
            all_comment += eachday.get('allComment') * qty
        if comments_num > 0:
            area_data = {
                'provinceCode': city_code[0:2] + '0000',
                'cityCode': city_code,
                'countyCode': k[1],
                'commentsQty': comments_num,
                'satisfiedcommentsQty': satisfied_num,
                'serviceScore': round(service_score / comments_num, 1),
                'priceScore': round(price_score / comments_num, 1),
                'qualityScore': round(quality_score / comments_num, 1),
                'envirScore': round(envir_score / comments_num, 1),
                'efficiencyScore': round(efficiency_score / comments_num, 1),
                'allComment': round(all_comment / comments_num, 1),
            }
        else:
            area_data = {
                'provinceCode': city_code[0:2] + '0000',
                'cityCode': city_code,
                'countyCode': k[1],
                'commentsQty': comments_num,
                'satisfiedcommentsQty': satisfied_num,
                'serviceScore': 0,
                'priceScore': 0,
                'qualityScore': 0,
                'envirScore': 0,
                'efficiencyScore': 0,
                'allComment': 0,
            }
        lastseason.append(area_data)
    # 获取周趋势
    bias = calendar.weekday(today.year, today.month, today.day)
    start_trend_week_day = datetime(today.year, today.month, today.day, tzinfo=None) - timedelta(bias) - timedelta(
        6 * 7)
    end_trend_week_day = datetime(today.year, today.month, today.day, tzinfo=None) + timedelta(days=(6 - bias))
    weeks = create_week_list(start_trend_week_day.strftime('%Y-%m-%d'), end_trend_week_day.strftime('%Y-%m-%d'))
    weekly_trends = []
    for k, v in area_relatived_record.items():
        for week in weeks:
            comments_num = 0  # 总数计数
            satisfied_num = 0  # 满意评价计数
            service_score = 0
            price_score = 0
            quality_score = 0
            envir_score = 0
            efficiency_score = 0
            all_comment = 0
            for eachday in v:
                if not in_week(week, eachday.get('date')):
                    continue
                qty = eachday.get('commentsQty')
                comments_num += qty
                satisfied_num += eachday.get('satisfiedcommentsQty')
                service_score += eachday.get('serviceScore') * qty
                price_score += eachday.get('serviceScore') * qty
                quality_score += eachday.get('serviceScore') * qty
                envir_score += eachday.get('serviceScore') * qty
                efficiency_score += eachday.get('serviceScore') * qty
                all_comment += eachday.get('allComment') * qty
            if comments_num > 0:
                per_week = {
                    'provinceCode': city_code[0:2] + '0000',
                    'cityCode': city_code,
                    'countyCode': k[1],
                    'commentsQty': comments_num,
                    'satisfiedcommentsQty': satisfied_num,
                    'serviceScore': round(service_score / comments_num, 1),
                    'priceScore': round(price_score / comments_num, 1),
                    'qualityScore': round(quality_score / comments_num, 1),
                    'envirScore': round(envir_score / comments_num, 1),
                    'efficiencyScore': round(efficiency_score / comments_num, 1),
                    'allComment': round(all_comment / comments_num, 1),
                    'periodStart': week[0].isoformat(),
                    'periodEnd': week[1].isoformat(),
                }
            else:
                per_week = {
                    'provinceCode': city_code[0:2] + '0000',
                    'cityCode': city_code,
                    'countyCode': k[1],
                    'commentsQty': comments_num,
                    'satisfiedcommentsQty': satisfied_num,
                    'serviceScore': 0,
                    'priceScore': 0,
                    'qualityScore': 0,
                    'envirScore': 0,
                    'efficiencyScore': 0,
                    'allComment': 0,
                    'periodStart': week[0].isoformat(),
                    'periodEnd': week[1].isoformat(),
                }
            weekly_trends.append(per_week)
    # 获取月趋势
    start_trend_month_day, end_trend_month_day = get_last_n_month_period(today)
    months = create_month_list(start_trend_month_day.strftime('%Y-%m-%d'), end_trend_month_day.strftime('%Y-%m-%d'))
    monthly_trends = []
    for k, v in area_relatived_record.items():
        for month in months:
            comments_num = 0  # 总数计数
            satisfied_num = 0  # 满意评论计数
            service_score = 0
            price_score = 0
            quality_score = 0
            envir_score = 0
            efficiency_score = 0
            all_comment = 0
            for eachday in v:
                # 选择周时间内的统计数据
                if not in_month(month, eachday.get('date')):
                    continue
                qty = eachday.get('commentsQty')
                comments_num += qty
                satisfied_num += eachday.get('satisfiedcommentsQty')
                service_score += eachday.get('serviceScore') * qty
                price_score += eachday.get('serviceScore') * qty
                quality_score += eachday.get('serviceScore') * qty
                envir_score += eachday.get('serviceScore') * qty
                efficiency_score += eachday.get('serviceScore') * qty
                all_comment += eachday.get('allComment') * qty
            if comments_num > 0:

                per_month = {
                    'provinceCode': city_code[0:2] + '0000',
                    'cityCode': city_code,
                    'countyCode': k[1],
                    'commentsQty': comments_num,
                    'satisfiedcommentsQty': satisfied_num,
                    'serviceScore': round(service_score / comments_num, 1),
                    'priceScore': round(price_score / comments_num, 1),
                    'qualityScore': round(quality_score / comments_num, 1),
                    'envirScore': round(envir_score / comments_num, 1),
                    'efficiencyScore': round(efficiency_score / comments_num, 1),
                    'allComment': round(all_comment / comments_num, 1),
                    'periodStart': month[0].isoformat(),
                    'periodEnd': month[1].isoformat(),
                }
            else:
                per_month = {
                    'provinceCode': city_code[0:2] + '0000',
                    'cityCode': city_code,
                    'countyCode': k[1],
                    'commentsQty': comments_num,  # 维修量
                    'satisfiedcommentsQty': satisfied_num,  # 满意评价数
                    'serviceScore': 0,
                    'priceScore': 0,
                    'qualityScore': 0,
                    'envirScore': 0,
                    'efficiencyScore': 0,
                    'allComment': 0,
                    'periodStart': month[0].isoformat(),
                    'periodEnd': month[1].isoformat(),
                }
            monthly_trends.append(per_month)
    # 获取季度趋势
    start_trend_season_day, end_trend_season_day = get_last_n_season_period(today)
    seasons = create_season_list(start_trend_season_day.strftime('%Y-%m-%d'),
                                 end_trend_season_day.strftime('%Y-%m-%d'))
    seasonly_trends = []
    for k, v in area_relatived_record.items():
        for season in seasons:
            comments_num = 0
            satisfied_num = 0
            service_score = 0
            price_score = 0
            quality_score = 0
            envir_score = 0
            efficiency_score = 0
            all_comment = 0
            for eachday in v:
                if not in_season(season, eachday.get('date')):
                    continue
                qty = eachday.get('commentsQty')
                comments_num += qty
                satisfied_num += eachday.get('satisfiedcommentsQty')
                service_score += eachday.get('serviceScore') * qty
                price_score += eachday.get('serviceScore') * qty
                quality_score += eachday.get('serviceScore') * qty
                envir_score += eachday.get('serviceScore') * qty
                efficiency_score += eachday.get('serviceScore') * qty
                all_comment += eachday.get('allComment') * qty
            if comments_num > 0:
                per_season = {
                    'provinceCode': city_code[0:2] + '0000',
                    'cityCode': city_code,
                    'countyCode': k[1],
                    'commentsQty': comments_num,
                    'satisfiedcommentsQty': satisfied_num,
                    'serviceScore': round(service_score / comments_num, 1),
                    'priceScore': round(price_score / comments_num, 1),
                    'qualityScore': round(quality_score / comments_num, 1),
                    'envirScore': round(envir_score / comments_num, 1),
                    'efficiencyScore': round(efficiency_score / comments_num, 1),
                    'allComment': round(all_comment / comments_num, 1),
                    'periodStart': season[0].isoformat(),
                    'periodEnd': season[1].isoformat(),
                }
            else:
                per_season = {
                    'provinceCode': city_code[0:2] + '0000',
                    'cityCode': city_code,
                    'countyCode': k[1],
                    'commentsQty': comments_num,
                    'satisfiedcommentsQty': satisfied_num,
                    'serviceScore': 0,
                    'priceScore': 0,
                    'qualityScore': 0,
                    'envirScore': 0,
                    'efficiencyScore': 0,
                    'allComment': 0,
                    'periodStart': season[0].isoformat(),
                    'periodEnd': season[1].isoformat(),
                }
            seasonly_trends.append(per_season)
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


@admin_bp.route(r'/commonapi/admin/statistics/comments/repairtype', methods=['GET', 'POST'])
def repair_type():
    """统计一段时间内各车辆类型的评价量"""

    today = datetime.today()
    city_code = request.args.get('citycode')
    if not city_code:
        return jsonify({'code': '400'}), 400

    mongo_client = MongoClient(host='127.0.0.1', port=27017)
    comments_repairtype = mongo_client.statistics.repairtype.find({'cityCode': city_code})

    # 获取车辆类型列表
    repairtypelist = [
        ['日常维护', 10],
        ['一级维护', 20],
        ['二级维护', 30],
        ['汽车小修', 40],
        ['汽车大修', 50],
        ['总成修理', 60],
        ['零件修理', 70],
        ['其它', 90]
    ]
    # 按照维修类别进行划分
    repairtype_relatived_record = {}
    for repairtype in repairtypelist:
        statistics_list = []
        for tstats in comments_repairtype:
            if tstats.get('repairType') == repairtype[1]:
                statistics_list.append(tstats)
        repairtype_relatived_record[(repairtype[0], repairtype[1])] = statistics_list

    # 统计，全部历史数据
    totaldata = []
    for k, v in repairtype_relatived_record.items():
        comments_num = 0  # 总数计数
        satisfied_num = 0  # 满意评论计数
        service_score = 0
        price_score = 0
        quality_score = 0
        envir_score = 0
        efficiency_score = 0
        all_comment = 0
        for eachday in v:
            qty = eachday.get('commentsQty')
            comments_num += eachday.get('commentsQty')
            satisfied_num += eachday.get('satisfiedcommentsQty')
            service_score += eachday.get('serviceScore') * qty
            price_score += eachday.get('serviceScore') * qty
            quality_score += eachday.get('serviceScore') * qty
            envir_score += eachday.get('serviceScore') * qty
            efficiency_score += eachday.get('serviceScore') * qty
            all_comment += eachday.get('allComment') * qty
        if comments_num > 0:
            type_data = {
                'provinceCode': city_code[0:2] + '0000',
                'cityCode': city_code,
                'repairType': k[1],
                'commentsQty': comments_num,  # 维修量
                'satisfiedcommentsQty': satisfied_num,  # 满意评价数
                'serviceScore': round(service_score / comments_num, 1),
                'priceScore': round(price_score / comments_num, 1),
                'qualityScore': round(quality_score / comments_num, 1),
                'envirScore': round(envir_score / comments_num, 1),
                'efficiencyScore': round(efficiency_score / comments_num, 1),
                'allComment': round(all_comment / comments_num, 1),
            }
        else:
            type_data = {
                'provinceCode': city_code[0:2] + '0000',
                'cityCode': city_code,
                'repairType': k[1],
                'commentsQty': comments_num,  # 维修量
                'satisfiedcommentsQty': satisfied_num,  # 满意评价数
                'serviceScore': 0,
                'priceScore': 0,
                'qualityScore': 0,
                'envirScore': 0,
                'efficiencyScore': 0,
                'allComment': 0,
            }
        totaldata.append(type_data)
    # 上一周
    bias = calendar.weekday(today.year, today.month, today.day)
    start_week_day = datetime(today.year, today.month, today.day, tzinfo=None) - timedelta(bias + 7)
    end_week_day = start_week_day + timedelta(days=6)

    lastweek = []
    for k, v in repairtype_relatived_record.items():
        comments_num = 0  # 总数计数
        satisfied_num = 0  # 满意评论计数
        service_score = 0
        price_score = 0
        quality_score = 0
        envir_score = 0
        efficiency_score = 0
        all_comment = 0
        for eachday in v:
            if not in_week((start_week_day, end_week_day), eachday.get('date')):
                continue
            qty = eachday.get('commentsQty')
            comments_num += qty
            satisfied_num += eachday.get('satisfiedcommentsQty')
            service_score += eachday.get('serviceScore') * qty
            price_score += eachday.get('serviceScore') * qty
            quality_score += eachday.get('serviceScore') * qty
            envir_score += eachday.get('serviceScore') * qty
            efficiency_score += eachday.get('serviceScore') * qty
            all_comment += eachday.get('allComment') * qty
        if comments_num > 0:
            type_data = {
                'provinceCode': city_code[0:2] + '0000',
                'cityCode': city_code,
                'repairType': k[1],  # 品牌
                'commentsQty': comments_num,  # 维修量
                'satisfiedcommentsQty': satisfied_num,  # 满意评价数
                'serviceScore': round(service_score / comments_num, 1),
                'priceScore': round(price_score / comments_num, 1),
                'qualityScore': round(quality_score / comments_num, 1),
                'envirScore': round(envir_score / comments_num, 1),
                'efficiencyScore': round(efficiency_score / comments_num, 1),
                'allComment': round(all_comment / comments_num, 1),
            }
        else:
            type_data = {
                'provinceCode': city_code[0:2] + '0000',
                'cityCode': city_code,
                'repairType': k[1],
                'commentsQty': comments_num,
                'satisfiedcommentsQty': satisfied_num,
                'serviceScore': 0,
                'priceScore': 0,
                'qualityScore': 0,
                'envirScore': 0,
                'efficiencyScore': 0,
                'allComment': 0,
            }
        lastweek.append(type_data)
    # 上一月
    start_last_month, end_last_month = get_last_month_period(today)
    lastmonth = []
    for k, v in repairtype_relatived_record.items():
        comments_num = 0  # 总数计数
        satisfied_num = 0  # 满意评论计数
        service_score = 0
        price_score = 0
        quality_score = 0
        envir_score = 0
        efficiency_score = 0
        all_comment = 0
        for eachday in v:
            if not in_month((start_last_month, end_last_month), eachday.get('date')):
                continue
            qty = eachday.get('commentsQty')
            comments_num += qty
            satisfied_num += eachday.get('satisfiedcommentsQty')
            service_score += eachday.get('serviceScore') * qty
            price_score += eachday.get('serviceScore') * qty
            quality_score += eachday.get('serviceScore') * qty
            envir_score += eachday.get('serviceScore') * qty
            efficiency_score += eachday.get('serviceScore') * qty
            all_comment += eachday.get('allComment') * qty
        if comments_num > 0:
            type_data = {
                'provinceCode': city_code[0:2] + '0000',
                'cityCode': city_code,
                'repairType': k[1],
                'commentsQty': comments_num,
                'satisfiedcommentsQty': satisfied_num,
                'serviceScore': round(service_score / comments_num, 1),
                'priceScore': round(price_score / comments_num, 1),
                'qualityScore': round(quality_score / comments_num, 1),
                'envirScore': round(envir_score / comments_num, 1),
                'efficiencyScore': round(efficiency_score / comments_num, 1),
                'allComment': round(all_comment / comments_num, 1),
            }
        else:
            type_data = {
                'provinceCode': city_code[0:2] + '0000',
                'cityCode': city_code,
                'repairType': k[1],
                'commentsQty': comments_num,
                'satisfiedcommentsQty': satisfied_num,
                'serviceScore': 0,
                'priceScore': 0,
                'qualityScore': 0,
                'envirScore': 0,
                'efficiencyScore': 0,
                'allComment': 0,
            }
        lastmonth.append(type_data)
    # 上一季度
    start_season_day, end_season_day = get_last_season_period(today)
    lastseason = []
    for k, v in repairtype_relatived_record.items():
        comments_num = 0  # 总数计数
        satisfied_num = 0  # 满意评论计数
        service_score = 0
        price_score = 0
        quality_score = 0
        envir_score = 0
        efficiency_score = 0
        all_comment = 0
        for eachday in v:
            # 选择上周时间内的统计数据
            if not in_season((start_season_day, end_season_day), eachday.get('date')):
                continue
            qty = eachday.get('commentsQty')
            comments_num += qty
            satisfied_num += eachday.get('satisfiedcommentsQty')
            service_score += eachday.get('serviceScore') * qty
            price_score += eachday.get('serviceScore') * qty
            quality_score += eachday.get('serviceScore') * qty
            envir_score += eachday.get('serviceScore') * qty
            efficiency_score += eachday.get('serviceScore') * qty
            all_comment += eachday.get('allComment') * qty
        if comments_num > 0:
            type_data = {
                'provinceCode': city_code[0:2] + '0000',
                'cityCode': city_code,
                'repairType': k[1],
                'commentsQty': comments_num,
                'satisfiedcommentsQty': satisfied_num,
                'serviceScore': round(service_score / comments_num, 1),
                'priceScore': round(price_score / comments_num, 1),
                'qualityScore': round(quality_score / comments_num, 1),
                'envirScore': round(envir_score / comments_num, 1),
                'efficiencyScore': round(efficiency_score / comments_num, 1),
                'allComment': round(all_comment / comments_num, 1),
            }
        else:
            type_data = {
                'provinceCode': city_code[0:2] + '0000',
                'cityCode': city_code,
                'repairType': k[1],
                'commentsQty': comments_num,
                'satisfiedcommentsQty': satisfied_num,
                'serviceScore': 0,
                'priceScore': 0,
                'qualityScore': 0,
                'envirScore': 0,
                'efficiencyScore': 0,
                'allComment': 0,
            }
        lastseason.append(type_data)
    # 获取周趋势
    bias = calendar.weekday(today.year, today.month, today.day)
    start_trend_week_day = datetime(today.year, today.month, today.day, tzinfo=None) - timedelta(bias) - timedelta(
        6 * 7)
    end_trend_week_day = datetime(today.year, today.month, today.day, tzinfo=None) + timedelta(days=(6 - bias))
    weeks = create_week_list(start_trend_week_day.strftime('%Y-%m-%d'), end_trend_week_day.strftime('%Y-%m-%d'))
    weekly_trends = []
    for k, v in repairtype_relatived_record.items():
        for week in weeks:
            comments_num = 0  # 总数计数
            satisfied_num = 0  # 满意评价计数
            service_score = 0
            price_score = 0
            quality_score = 0
            envir_score = 0
            efficiency_score = 0
            all_comment = 0
            for eachday in v:
                if not in_week(week, eachday.get('date')):
                    continue
                qty = eachday.get('commentsQty')
                comments_num += qty
                satisfied_num += eachday.get('satisfiedcommentsQty')
                service_score += eachday.get('serviceScore') * qty
                price_score += eachday.get('serviceScore') * qty
                quality_score += eachday.get('serviceScore') * qty
                envir_score += eachday.get('serviceScore') * qty
                efficiency_score += eachday.get('serviceScore') * qty
                all_comment += eachday.get('allComment') * qty
            if comments_num > 0:
                type_per_week = {
                    'provinceCode': city_code[0:2] + '0000',
                    'cityCode': city_code,
                    'repairType': k[1],
                    'commentsQty': comments_num,
                    'satisfiedcommentsQty': satisfied_num,
                    'serviceScore': round(service_score / comments_num, 1),
                    'priceScore': round(price_score / comments_num, 1),
                    'qualityScore': round(quality_score / comments_num, 1),
                    'envirScore': round(envir_score / comments_num, 1),
                    'efficiencyScore': round(efficiency_score / comments_num, 1),
                    'allComment': round(all_comment / comments_num, 1),
                    'periodStart': week[0].isoformat(),
                    'periodEnd': week[1].isoformat(),
                }
            else:
                type_per_week = {
                    'provinceCode': city_code[0:2] + '0000',
                    'cityCode': city_code,
                    'repairType': k[1],
                    'commentsQty': comments_num,
                    'satisfiedcommentsQty': satisfied_num,
                    'serviceScore': 0,
                    'priceScore': 0,
                    'qualityScore': 0,
                    'envirScore': 0,
                    'efficiencyScore': 0,
                    'allComment': 0,
                    'periodStart': week[0].isoformat(),
                    'periodEnd': week[1].isoformat(),
                }
            weekly_trends.append(type_per_week)
    # 获取月趋势
    start_trend_month_day, end_trend_month_day = get_last_n_month_period(today)
    months = create_month_list(start_trend_month_day.strftime('%Y-%m-%d'), end_trend_month_day.strftime('%Y-%m-%d'))
    monthly_trends = []
    for k, v in repairtype_relatived_record.items():
        for month in months:
            comments_num = 0  # 总数计数
            satisfied_num = 0  # 满意评论计数
            service_score = 0
            price_score = 0
            quality_score = 0
            envir_score = 0
            efficiency_score = 0
            all_comment = 0
            for eachday in v:
                if not in_month(month, eachday.get('date')):
                    continue
                qty = eachday.get('commentsQty')
                comments_num += qty
                satisfied_num += eachday.get('satisfiedcommentsQty')
                service_score += eachday.get('serviceScore') * qty
                price_score += eachday.get('serviceScore') * qty
                quality_score += eachday.get('serviceScore') * qty
                envir_score += eachday.get('serviceScore') * qty
                efficiency_score += eachday.get('serviceScore') * qty
                all_comment += eachday.get('allComment') * qty
            if comments_num > 0:

                brand_per_month = {
                    'provinceCode': city_code[0:2] + '0000',
                    'cityCode': city_code,
                    'repairType': k[1],
                    'commentsQty': comments_num,
                    'satisfiedcommentsQty': satisfied_num,
                    'serviceScore': round(service_score / comments_num, 1),
                    'priceScore': round(price_score / comments_num, 1),
                    'qualityScore': round(quality_score / comments_num, 1),
                    'envirScore': round(envir_score / comments_num, 1),
                    'efficiencyScore': round(efficiency_score / comments_num, 1),
                    'allComment': round(all_comment / comments_num, 1),
                    'periodStart': month[0].isoformat(),
                    'periodEnd': month[1].isoformat(),
                }
            else:
                brand_per_month = {
                    'provinceCode': city_code[0:2] + '0000',
                    'cityCode': city_code,
                    'repairType': k[1],  # 品牌
                    'commentsQty': comments_num,  # 维修量
                    'satisfiedcommentsQty': satisfied_num,  # 满意评价数
                    'serviceScore': 0,
                    'priceScore': 0,
                    'qualityScore': 0,
                    'envirScore': 0,
                    'efficiencyScore': 0,
                    'allComment': 0,
                    'periodStart': month[0].isoformat(),
                    'periodEnd': month[1].isoformat(),
                }
            monthly_trends.append(brand_per_month)
    # 获取季度趋势
    start_trend_season_day, end_trend_season_day = get_last_n_season_period(today)
    seasons = create_season_list(start_trend_season_day.strftime('%Y-%m-%d'),
                                 end_trend_season_day.strftime('%Y-%m-%d'))
    seasonly_trends = []
    for k, v in repairtype_relatived_record.items():
        for season in seasons:
            comments_num = 0
            satisfied_num = 0
            service_score = 0
            price_score = 0
            quality_score = 0
            envir_score = 0
            efficiency_score = 0
            all_comment = 0
            for eachday in v:
                if not in_season(season, eachday.get('date')):
                    continue
                qty = eachday.get('commentsQty')
                comments_num += qty
                satisfied_num += eachday.get('satisfiedcommentsQty')
                service_score += eachday.get('serviceScore') * qty
                price_score += eachday.get('serviceScore') * qty
                quality_score += eachday.get('serviceScore') * qty
                envir_score += eachday.get('serviceScore') * qty
                efficiency_score += eachday.get('serviceScore') * qty
                all_comment += eachday.get('allComment') * qty
            if comments_num > 0:
                type_per_season = {
                    'provinceCode': city_code[0:2] + '0000',
                    'cityCode': city_code,
                    'repairType': k[1],
                    'commentsQty': comments_num,
                    'satisfiedcommentsQty': satisfied_num,
                    'serviceScore': round(service_score / comments_num, 1),
                    'priceScore': round(price_score / comments_num, 1),
                    'qualityScore': round(quality_score / comments_num, 1),
                    'envirScore': round(envir_score / comments_num, 1),
                    'efficiencyScore': round(efficiency_score / comments_num, 1),
                    'allComment': round(all_comment / comments_num, 1),
                    'periodStart': season[0].isoformat(),
                    'periodEnd': season[1].isoformat(),
                }
            else:
                type_per_season = {
                    'provinceCode': city_code[0:2] + '0000',
                    'cityCode': city_code,
                    'repairType': k[1],
                    'commentsQty': comments_num,
                    'satisfiedcommentsQty': satisfied_num,
                    'serviceScore': 0,
                    'priceScore': 0,
                    'qualityScore': 0,
                    'envirScore': 0,
                    'efficiencyScore': 0,
                    'allComment': 0,
                    'periodStart': season[0].isoformat(),
                    'periodEnd': season[1].isoformat(),
                }
            seasonly_trends.append(type_per_season)
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


@admin_bp.route(r'/commonapi/admin/statistics/comments/category', methods=['GET', 'POST'])
def category():
    """统计一段时间内各车辆类型的评价量"""

    today = datetime.today()
    city_code = request.args.get('citycode')
    if not city_code:
        return jsonify({'code': '400'}), 400

    mongo_client = MongoClient(host='127.0.0.1', port=27017)
    comments_category = mongo_client.statistics.category.find({'cityCode': city_code})

    # 获取企业经营类别列表
    categorylist = [
        ['一类', 1],
        ['二类', 2],
        ['三类', 3],
        ['其它', 99],
    ]
    # 按照维修类别进行划分
    category_relatived_record = {}
    for _category in categorylist:
        statistics_list = []
        for tstats in comments_category:
            if tstats.get('category') == _category[1]:
                statistics_list.append(tstats)
        category_relatived_record[(_category[0], _category[1])] = statistics_list

    # 统计，全部历史数据
    totaldata = []
    for k, v in category_relatived_record.items():
        comments_num = 0  # 总数计数
        satisfied_num = 0  # 满意评论计数
        service_score = 0
        price_score = 0
        quality_score = 0
        envir_score = 0
        efficiency_score = 0
        all_comment = 0
        for eachday in v:
            qty = eachday.get('commentsQty')
            comments_num += eachday.get('commentsQty')
            satisfied_num += eachday.get('satisfiedcommentsQty')
            service_score += eachday.get('serviceScore') * qty
            price_score += eachday.get('serviceScore') * qty
            quality_score += eachday.get('serviceScore') * qty
            envir_score += eachday.get('serviceScore') * qty
            efficiency_score += eachday.get('serviceScore') * qty
            all_comment += eachday.get('allComment') * qty
        if comments_num > 0:
            type_data = {
                'provinceCode': city_code[0:2] + '0000',
                'cityCode': city_code,
                'category': k[1],
                'commentsQty': comments_num,
                'satisfiedcommentsQty': satisfied_num,
                'serviceScore': round(service_score / comments_num, 1),
                'priceScore': round(price_score / comments_num, 1),
                'qualityScore': round(quality_score / comments_num, 1),
                'envirScore': round(envir_score / comments_num, 1),
                'efficiencyScore': round(efficiency_score / comments_num, 1),
                'allComment': round(all_comment / comments_num, 1),
            }
        else:
            type_data = {
                'provinceCode': city_code[0:2] + '0000',
                'cityCode': city_code,
                'category': k[1],
                'commentsQty': comments_num,
                'satisfiedcommentsQty': satisfied_num,
                'serviceScore': 0,
                'priceScore': 0,
                'qualityScore': 0,
                'envirScore': 0,
                'efficiencyScore': 0,
                'allComment': 0,
            }
        totaldata.append(type_data)
    # 上一周
    bias = calendar.weekday(today.year, today.month, today.day)
    start_week_day = datetime(today.year, today.month, today.day, tzinfo=None) - timedelta(bias + 7)
    end_week_day = start_week_day + timedelta(days=6)

    lastweek = []
    for k, v in category_relatived_record.items():
        comments_num = 0  # 总数计数
        satisfied_num = 0  # 满意评论计数
        service_score = 0
        price_score = 0
        quality_score = 0
        envir_score = 0
        efficiency_score = 0
        all_comment = 0
        for eachday in v:
            if not in_week((start_week_day, end_week_day), eachday.get('date')):
                continue
            qty = eachday.get('commentsQty')
            comments_num += qty
            satisfied_num += eachday.get('satisfiedcommentsQty')
            service_score += eachday.get('serviceScore') * qty
            price_score += eachday.get('serviceScore') * qty
            quality_score += eachday.get('serviceScore') * qty
            envir_score += eachday.get('serviceScore') * qty
            efficiency_score += eachday.get('serviceScore') * qty
            all_comment += eachday.get('allComment') * qty
        if comments_num > 0:
            type_data = {
                'provinceCode': city_code[0:2] + '0000',
                'cityCode': city_code,
                'category': k[1],
                'commentsQty': comments_num,
                'satisfiedcommentsQty': satisfied_num,
                'serviceScore': round(service_score / comments_num, 1),
                'priceScore': round(price_score / comments_num, 1),
                'qualityScore': round(quality_score / comments_num, 1),
                'envirScore': round(envir_score / comments_num, 1),
                'efficiencyScore': round(efficiency_score / comments_num, 1),
                'allComment': round(all_comment / comments_num, 1),
            }
        else:
            type_data = {
                'provinceCode': city_code[0:2] + '0000',
                'cityCode': city_code,
                'category': k[1],
                'commentsQty': comments_num,
                'satisfiedcommentsQty': satisfied_num,
                'serviceScore': 0,
                'priceScore': 0,
                'qualityScore': 0,
                'envirScore': 0,
                'efficiencyScore': 0,
                'allComment': 0,
            }
        lastweek.append(type_data)
    # 上一月
    start_last_month, end_last_month = get_last_month_period(today)
    lastmonth = []
    for k, v in category_relatived_record.items():
        comments_num = 0  # 总数计数
        satisfied_num = 0  # 满意评论计数
        service_score = 0
        price_score = 0
        quality_score = 0
        envir_score = 0
        efficiency_score = 0
        all_comment = 0
        for eachday in v:
            if not in_month((start_last_month, end_last_month), eachday.get('date')):
                continue
            qty = eachday.get('commentsQty')
            comments_num += qty
            satisfied_num += eachday.get('satisfiedcommentsQty')
            service_score += eachday.get('serviceScore') * qty
            price_score += eachday.get('serviceScore') * qty
            quality_score += eachday.get('serviceScore') * qty
            envir_score += eachday.get('serviceScore') * qty
            efficiency_score += eachday.get('serviceScore') * qty
            all_comment += eachday.get('allComment') * qty
        if comments_num > 0:
            type_data = {
                'provinceCode': city_code[0:2] + '0000',
                'cityCode': city_code,
                'category': k[1],
                'commentsQty': comments_num,
                'satisfiedcommentsQty': satisfied_num,
                'serviceScore': round(service_score / comments_num, 1),
                'priceScore': round(price_score / comments_num, 1),
                'qualityScore': round(quality_score / comments_num, 1),
                'envirScore': round(envir_score / comments_num, 1),
                'efficiencyScore': round(efficiency_score / comments_num, 1),
                'allComment': round(all_comment / comments_num, 1),
            }
        else:
            type_data = {
                'provinceCode': city_code[0:2] + '0000',
                'cityCode': city_code,
                'category': k[1],
                'commentsQty': comments_num,
                'satisfiedcommentsQty': satisfied_num,
                'serviceScore': 0,
                'priceScore': 0,
                'qualityScore': 0,
                'envirScore': 0,
                'efficiencyScore': 0,
                'allComment': 0,
            }
        lastmonth.append(type_data)
    # 上一季度
    start_season_day, end_season_day = get_last_season_period(today)
    lastseason = []
    for k, v in category_relatived_record.items():
        comments_num = 0  # 总数计数
        satisfied_num = 0  # 满意评论计数
        service_score = 0
        price_score = 0
        quality_score = 0
        envir_score = 0
        efficiency_score = 0
        all_comment = 0
        for eachday in v:
            # 选择上周时间内的统计数据
            if not in_season((start_season_day, end_season_day), eachday.get('date')):
                continue
            qty = eachday.get('commentsQty')
            comments_num += qty
            satisfied_num += eachday.get('satisfiedcommentsQty')
            service_score += eachday.get('serviceScore') * qty
            price_score += eachday.get('serviceScore') * qty
            quality_score += eachday.get('serviceScore') * qty
            envir_score += eachday.get('serviceScore') * qty
            efficiency_score += eachday.get('serviceScore') * qty
            all_comment += eachday.get('allComment') * qty
        if comments_num > 0:
            type_data = {
                'provinceCode': city_code[0:2] + '0000',
                'cityCode': city_code,
                'category': k[1],
                'commentsQty': comments_num,
                'satisfiedcommentsQty': satisfied_num,
                'serviceScore': round(service_score / comments_num, 1),
                'priceScore': round(price_score / comments_num, 1),
                'qualityScore': round(quality_score / comments_num, 1),
                'envirScore': round(envir_score / comments_num, 1),
                'efficiencyScore': round(efficiency_score / comments_num, 1),
                'allComment': round(all_comment / comments_num, 1),
            }
        else:
            type_data = {
                'provinceCode': city_code[0:2] + '0000',
                'cityCode': city_code,
                'category': k[1],
                'commentsQty': comments_num,
                'satisfiedcommentsQty': satisfied_num,
                'serviceScore': 0,
                'priceScore': 0,
                'qualityScore': 0,
                'envirScore': 0,
                'efficiencyScore': 0,
                'allComment': 0,
            }
        lastseason.append(type_data)
    # 获取周趋势
    bias = calendar.weekday(today.year, today.month, today.day)
    start_trend_week_day = datetime(today.year, today.month, today.day, tzinfo=None) - timedelta(bias) - timedelta(
        6 * 7)
    end_trend_week_day = datetime(today.year, today.month, today.day, tzinfo=None) + timedelta(days=(6 - bias))
    weeks = create_week_list(start_trend_week_day.strftime('%Y-%m-%d'), end_trend_week_day.strftime('%Y-%m-%d'))
    weekly_trends = []
    for k, v in category_relatived_record.items():
        for week in weeks:
            comments_num = 0  # 总数计数
            satisfied_num = 0  # 满意评价计数
            service_score = 0
            price_score = 0
            quality_score = 0
            envir_score = 0
            efficiency_score = 0
            all_comment = 0
            for eachday in v:
                if not in_week(week, eachday.get('date')):
                    continue
                qty = eachday.get('commentsQty')
                comments_num += qty
                satisfied_num += eachday.get('satisfiedcommentsQty')
                service_score += eachday.get('serviceScore') * qty
                price_score += eachday.get('serviceScore') * qty
                quality_score += eachday.get('serviceScore') * qty
                envir_score += eachday.get('serviceScore') * qty
                efficiency_score += eachday.get('serviceScore') * qty
                all_comment += eachday.get('allComment') * qty
            if comments_num > 0:
                type_per_week = {
                    'provinceCode': city_code[0:2] + '0000',
                    'cityCode': city_code,
                    'category': k[1],
                    'commentsQty': comments_num,
                    'satisfiedcommentsQty': satisfied_num,
                    'serviceScore': round(service_score / comments_num, 1),
                    'priceScore': round(price_score / comments_num, 1),
                    'qualityScore': round(quality_score / comments_num, 1),
                    'envirScore': round(envir_score / comments_num, 1),
                    'efficiencyScore': round(efficiency_score / comments_num, 1),
                    'allComment': round(all_comment / comments_num, 1),
                    'periodStart': week[0].isoformat(),
                    'periodEnd': week[1].isoformat(),
                }
            else:
                type_per_week = {
                    'provinceCode': city_code[0:2] + '0000',
                    'cityCode': city_code,
                    'category': k[1],
                    'commentsQty': comments_num,
                    'satisfiedcommentsQty': satisfied_num,
                    'serviceScore': 0,
                    'priceScore': 0,
                    'qualityScore': 0,
                    'envirScore': 0,
                    'efficiencyScore': 0,
                    'allComment': 0,
                    'periodStart': week[0].isoformat(),
                    'periodEnd': week[1].isoformat(),
                }
            weekly_trends.append(type_per_week)
    # 获取月趋势
    start_trend_month_day, end_trend_month_day = get_last_n_month_period(today)
    months = create_month_list(start_trend_month_day.strftime('%Y-%m-%d'), end_trend_month_day.strftime('%Y-%m-%d'))
    monthly_trends = []
    for k, v in category_relatived_record.items():
        for month in months:
            comments_num = 0  # 总数计数
            satisfied_num = 0  # 满意评论计数
            service_score = 0
            price_score = 0
            quality_score = 0
            envir_score = 0
            efficiency_score = 0
            all_comment = 0
            for eachday in v:
                if not in_month(month, eachday.get('date')):
                    continue
                qty = eachday.get('commentsQty')
                comments_num += qty
                satisfied_num += eachday.get('satisfiedcommentsQty')
                service_score += eachday.get('serviceScore') * qty
                price_score += eachday.get('serviceScore') * qty
                quality_score += eachday.get('serviceScore') * qty
                envir_score += eachday.get('serviceScore') * qty
                efficiency_score += eachday.get('serviceScore') * qty
                all_comment += eachday.get('allComment') * qty
            if comments_num > 0:

                brand_per_month = {
                    'provinceCode': city_code[0:2] + '0000',
                    'cityCode': city_code,
                    'category': k[1],
                    'commentsQty': comments_num,
                    'satisfiedcommentsQty': satisfied_num,
                    'serviceScore': round(service_score / comments_num, 1),
                    'priceScore': round(price_score / comments_num, 1),
                    'qualityScore': round(quality_score / comments_num, 1),
                    'envirScore': round(envir_score / comments_num, 1),
                    'efficiencyScore': round(efficiency_score / comments_num, 1),
                    'allComment': round(all_comment / comments_num, 1),
                    'periodStart': month[0].isoformat(),
                    'periodEnd': month[1].isoformat(),
                }
            else:
                brand_per_month = {
                    'provinceCode': city_code[0:2] + '0000',
                    'cityCode': city_code,
                    'category': k[1],
                    'commentsQty': comments_num,
                    'satisfiedcommentsQty': satisfied_num,
                    'serviceScore': 0,
                    'priceScore': 0,
                    'qualityScore': 0,
                    'envirScore': 0,
                    'efficiencyScore': 0,
                    'allComment': 0,
                    'periodStart': month[0].isoformat(),
                    'periodEnd': month[1].isoformat(),
                }
            monthly_trends.append(brand_per_month)
    # 获取季度趋势
    start_trend_season_day, end_trend_season_day = get_last_n_season_period(today)
    seasons = create_season_list(start_trend_season_day.strftime('%Y-%m-%d'),
                                 end_trend_season_day.strftime('%Y-%m-%d'))
    seasonly_trends = []
    for k, v in category_relatived_record.items():
        for season in seasons:
            comments_num = 0
            satisfied_num = 0
            service_score = 0
            price_score = 0
            quality_score = 0
            envir_score = 0
            efficiency_score = 0
            all_comment = 0
            for eachday in v:
                if not in_season(season, eachday.get('date')):
                    continue
                qty = eachday.get('commentsQty')
                comments_num += qty
                satisfied_num += eachday.get('satisfiedcommentsQty')
                service_score += eachday.get('serviceScore') * qty
                price_score += eachday.get('serviceScore') * qty
                quality_score += eachday.get('serviceScore') * qty
                envir_score += eachday.get('serviceScore') * qty
                efficiency_score += eachday.get('serviceScore') * qty
                all_comment += eachday.get('allComment') * qty
            if comments_num > 0:
                type_per_season = {
                    'provinceCode': city_code[0:2] + '0000',
                    'cityCode': city_code,
                    'category': k[1],
                    'commentsQty': comments_num,
                    'satisfiedcommentsQty': satisfied_num,
                    'serviceScore': round(service_score / comments_num, 1),
                    'priceScore': round(price_score / comments_num, 1),
                    'qualityScore': round(quality_score / comments_num, 1),
                    'envirScore': round(envir_score / comments_num, 1),
                    'efficiencyScore': round(efficiency_score / comments_num, 1),
                    'allComment': round(all_comment / comments_num, 1),
                    'periodStart': season[0].isoformat(),
                    'periodEnd': season[1].isoformat(),
                }
            else:
                type_per_season = {
                    'provinceCode': city_code[0:2] + '0000',
                    'cityCode': city_code,
                    'category': k[1],
                    'commentsQty': comments_num,
                    'satisfiedcommentsQty': satisfied_num,
                    'serviceScore': 0,
                    'priceScore': 0,
                    'qualityScore': 0,
                    'envirScore': 0,
                    'efficiencyScore': 0,
                    'allComment': 0,
                    'periodStart': season[0].isoformat(),
                    'periodEnd': season[1].isoformat(),
                }
            seasonly_trends.append(type_per_season)
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
