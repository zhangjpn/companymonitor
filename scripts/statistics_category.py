# -*-coding:utf-8 -*-
"""根据企业经营类别对评论进行分地区、分时期统计"""

from pymongo import MongoClient
from datetime import datetime, timedelta
from app.commontools import create_week_list, create_month_list, create_season_list


def statistics_category(citycode):
    """获取全部历史的、过去一周的，过去一个月的，过去一个季度的维修类型统计数据"""
    mongo_client = MongoClient(host='127.0.0.1', port=27017)
    default_time = datetime(2000, 1, 1)
    today = datetime.today().strftime('%Y-%m-%d')

    # 获取某个城市的评价
    comments = mongo_client.spv1.comments.find({'status': 1})
    target_comments = []
    comments_count = 0
    for comment in comments:  # 需要重写
        relatived_company = mongo_client.spv1.companies.find_one({'_id': comment.get('company')})
        _city_code = str(int(relatived_company.get('cityCode', 0)))
        _county_code = str(int(relatived_company.get('countyCode', 0)))
        _province_code = str(int(relatived_company.get('provinceCode', 0)))
        _category = int(relatived_company.get('category', 9))
        if _city_code == citycode:
            comment['provinceCode'] = _province_code
            comment['cityCode'] = _city_code
            comment['countyCode'] = _county_code
            comment['category'] = _category
            target_comments.append(comment)
            comments_count += 1

    # 获取企业经营类别列表
    categorylist = [
        ['一类', 1],
        ['二类', 2],
        ['三类', 3],
        ['其它', 99],
    ]
    # 按照企业经营类别分类评价数据
    category_relatived_comments = {}
    for category_info in categorylist:
        temp_comment_list = []
        for tcomment in target_comments:
            if int(tcomment.get('vehicleType')) == category_info[1]:
                temp_comment_list.append(tcomment)
        category_relatived_comments[(category_info[0], category_info[1])] = temp_comment_list
    # 全部数据，按照企业经营类别统计各项评价指标
    for k, v in category_relatived_comments.items():
        service_score = 0
        price_score = 0
        quality_score = 0
        envir_score = 0
        efficiency_score = 0
        c_count = len(v)
        if c_count > 0:
            temp_count = 0  # 好评计数
            for c in v:  # 对所有评价项求和
                if c.get('allComment') >= 2:
                    temp_count += 1
                service_score += c.get('serviceScore', 0)
                price_score += c.get('priceScore', 0)
                quality_score += c.get('qualityScore', 0)
                envir_score += c.get('envirScore', 0)
                efficiency_score += c.get('efficiencyScore', 0)
            total_data = {  # 全部数据
                'statsType': 4,  # 统计类型 1-满意度 2-维修类别 3-车辆类型 4-经营类别 5-车辆品牌
                'cityCode': citycode,
                'dataType': 1,  # 文档类型: 1-全部数据 2-周统计 3-月统计 4-季度统计
                'repairType': k[1],  # 企业经营类别代码 2位数字
                'serviceScore': round(service_score / c_count, 1),  # 服务态度
                'priceScore': round(price_score / c_count, 1),  # 维修价格
                'qualityScore': round(quality_score / c_count, 1),  # 服务质量
                'envirScore': round(envir_score / c_count, 1),  # 店面环境
                'efficiencyScore': round(efficiency_score / c_count, 1),  # 维修效率
                'allComment': round(temp_count / c_count, 3),  # 评价满意度
                'periodStart': default_time,
                'periodEnd': default_time

            }

        else:
            total_data = {
                'statsType': 4,  # 统计类型 1-满意度 2-维修类别 3-车辆类型 4-经营类别 5-车辆品牌
                'cityCode': citycode,
                'dataType': 1,  # 文档类型: 1-全部数据 2-周统计 3-月统计 4-季度统计
                'repairType': k[1],  # 企业经营类别代码 2位数字
                'serviceScore': 0,  # 服务态度
                'priceScore': 0,  # 维修价格
                'qualityScore': 0,  # 服务质量
                'envirScore': 0,  # 店面环境
                'efficiencyScore': 0,  # 维修效率
                'allComment': 0,  # 评价满意度
                'periodStart': default_time,
                'periodEnd': default_time
            }
        print('企业经营类别全部数据', total_data)
        mongo_client.statistics.commentsstatistics.replace_one(
            {'statsType': 4, 'dataType': 1, 'repairType': k[1], 'cityCode': citycode, 'periodStart': default_time,
             'periodEnd': default_time},
            total_data, upsert=True)

    # 按照周统计
    for k, v in category_relatived_comments.items():
        # 生成按照自然周的时间段
        def in_week(weekperiod, target_date):
            """根据日期判断一个日期是否在日期时间段内"""
            if weekperiod[0] - timedelta(hours=8) <= target_date < (
                            weekperiod[1] + timedelta(days=1) - timedelta(hours=8)):
                return True
            return False

        weeks = create_week_list('2015-12-01', today)

        if len(v) == 0:  # 如果某一企业经营类别的评价数为0,则全部时间段设置成默认值
            for week in weeks:
                weekly_data = {
                    'statsType': 4,  # 统计类型 1-满意度 2-维修类别 3-车辆类型 4-经营类别 5-车辆品牌
                    'cityCode': citycode,
                    'dataType': 2,  # 周期类型: 1-全部数据 2-周统计 3-月统计 4-季度统计
                    'repairType': k[1],  # 企业经营类别代码 2位数字
                    'serviceScore': 0,  # 服务态度
                    'priceScore': 0,  # 维修价格
                    'qualityScore': 0,  # 服务质量
                    'envirScore': 0,  # 店面环境
                    'efficiencyScore': 0,  # 维修效率
                    'allComment': 0,  # 评价满意度
                    'periodStart': week[0],  # 时期
                    'periodEnd': week[1],  # 时期
                }
                print('按照周统计：', weekly_data)
                mongo_client.statistics.commentsstatistics.replace_one(
                    {'cityCode': citycode, 'statsType': 4, 'periodStart': week[0], 'periodEnd': week[1], 'dataType': 2,
                     'repairType': k[1]},
                    weekly_data, upsert=True)
        else:
            for week in weeks:
                weekly_service_score = 0
                weekly_price_score = 0
                weekly_quality_score = 0
                weekly_envir_score = 0
                weekly_efficiency_score = 0
                count = 0  # 评论数记数
                satisfied_count = 0  # 满意度记数

                for comment in v:
                    if in_week(week, comment.get('created')):
                        count += 1
                        weekly_service_score += comment.get('serviceScore', 0)
                        weekly_price_score += comment.get('priceScore', 0)
                        weekly_quality_score += comment.get('qualityScore', 0)
                        weekly_envir_score += comment.get('envirScore', 0)
                        weekly_efficiency_score += comment.get('efficiencyScore', 0)
                        if comment.get('allComment', 0) >= 2:
                            satisfied_count += 1

                if count > 0:
                    weekly_data = {
                        'statsType': 4,  # 统计类型 1-满意度 2-维修类别 3-车辆类型 4-经营类别 5-车辆品牌
                        'dataType': 2,  # 周期类型:1-全部数据 2-周统计 3-月统计 4-季度统计
                        'repairType': k[1],  # 企业经营类别代码 2位数字
                        'cityCode': citycode,
                        'serviceScore': round(weekly_service_score / count, 1),  # 服务态度
                        'priceScore': round(weekly_price_score / count, 1),  # 维修价格
                        'qualityScore': round(weekly_quality_score / count, 1),  # 服务质量
                        'envirScore': round(weekly_envir_score / count, 1),  # 店面环境
                        'efficiencyScore': round(weekly_efficiency_score / count, 1),  # 维修效率
                        'allComment': round(satisfied_count / count, 3),  # 评价满意度
                        'periodStart': week[0],  # 时期
                        'periodEnd': week[1],  # 时期
                    }
                else:
                    weekly_data = {
                        'statsType': 4,  # 统计类型 1-满意度 2-维修类别 3-车辆类型 4-经营类别 5-车辆品牌
                        'dataType': 2,  # 周期类型:1-全部数据 2-周统计 3-月统计 4-季度统计
                        'repairType': k[1],  # 企业经营类别代码 2位数字
                        'cityCode': citycode,
                        'serviceScore': 0,  # 服务态度
                        'priceScore': 0,  # 维修价格
                        'qualityScore': 0,  # 服务质量
                        'envirScore': 0,  # 店面环境
                        'efficiencyScore': 0,  # 维修效率
                        'allComment': 0,  # 评价满意度
                        'periodStart': week[0],  # 时期
                        'periodEnd': week[1],  # 时期
                    }
                print('按照周统计：', weekly_data)
                mongo_client.statistics.commentsstatistics.replace_one(
                    {'periodStart': week[0], 'periodEnd': week[1], 'statsType': 4, 'dataType': 2, 'repairType': k[1],
                     'cityCode': citycode},
                    weekly_data, upsert=True)

    # 按照自然月统计
    for k, v in category_relatived_comments.items():
        def in_month(monthperiod, target_date):
            """根据日期判断一个日期是否在日期时间段内"""
            if monthperiod[0] - timedelta(hours=8) <= target_date < (
                            monthperiod[1] + timedelta(days=1) - timedelta(hours=8)):
                return True
            return False

        # 生成被统计的日期区间
        months = create_month_list('2015-12-01', today)
        if len(v) == 0:  # 如果某一企业经营类别的评价数为0,则全部时间段设置成默认值
            for month in months:
                monthly_data = {
                    'statsType': 4,  # 统计类型 1-满意度 2-维修类别 3-车辆类型 4-经营类别 5-车辆品牌
                    'dataType': 3,  # 周期类型:1-全部数据 2-周统计 3-月统计 4-季度统计
                    'repairType': k[1],  # 企业经营类别代码 2位数字
                    'cityCode': citycode,
                    'serviceScore': 0,  # 服务态度
                    'priceScore': 0,  # 维修价格
                    'qualityScore': 0,  # 服务质量
                    'envirScore': 0,  # 店面环境
                    'efficiencyScore': 0,  # 维修效率
                    'allComment': 0,  # 评价满意度
                    'periodStart': month[0],  # 时期 用每月第一天表示
                    'periodEnd': month[1],
                }
                print('按照月统计：', monthly_data)
                mongo_client.statistics.commentsstatistics.replace_one(
                    {'cityCode': citycode, 'statsType': 4, 'periodStart': month[0], 'periodEnd': month[1],
                     'dataType': 3, 'repairType': k[1]},
                    monthly_data, upsert=True)
        else:
            # 按照月统计
            for month in months:
                monthly_service_score = 0
                monthly_price_score = 0
                monthly_quality_score = 0
                monthly_envir_score = 0
                monthly_efficiency_score = 0
                count = 0  # 评论数记数
                satisfied_count = 0  # 满意度记数
                # 统计
                for comment in v:
                    if in_month(month, comment.get('created')):
                        count += 1
                        monthly_service_score += comment.get('serviceScore', 0)
                        monthly_price_score += comment.get('priceScore', 0)
                        monthly_quality_score += comment.get('qualityScore', 0)
                        monthly_envir_score += comment.get('envirScore', 0)
                        monthly_efficiency_score += comment.get('efficiencyScore', 0)
                        if comment.get('allComment', 0) >= 2:
                            satisfied_count += 1
                if count > 0:
                    monthly_data = {
                        'statsType': 4,  # 统计类型 1-满意度 2-维修类别 3-车辆类型 4-经营类别 5-车辆品牌
                        'dataType': 3,  # 周期类型:1-全部数据 2-周统计 3-月统计 4-季度统计
                        'repairType': k[1],  # 企业经营类别代码 2位数字
                        'cityCode': citycode,
                        'serviceScore': round(monthly_service_score / count, 1),  # 服务态度
                        'priceScore': round(monthly_price_score / count, 1),  # 维修价格
                        'qualityScore': round(monthly_quality_score / count, 1),  # 服务质量
                        'envirScore': round(monthly_envir_score / count, 1),  # 店面环境
                        'efficiencyScore': round(monthly_efficiency_score / count, 1),  # 维修效率
                        'allComment': round(satisfied_count / count, 3),  # 评价满意度
                        'periodStart': month[0],  # 时期 用每月第一天表示
                        'periodEnd': month[1],
                    }
                else:
                    monthly_data = {
                        'statsType': 4,  # 统计类型 1-满意度 2-维修类别 3-车辆类型 4-经营类别 5-车辆品牌
                        'dataType': 3,  # 周期类型:1-全部数据 2-周统计 3-月统计 4-季度统计
                        'repairType': k[1],  # 企业经营类别代码 2位数字
                        'cityCode': citycode,
                        'serviceScore': 0,  # 服务态度
                        'priceScore': 0,  # 维修价格
                        'qualityScore': 0,  # 服务质量
                        'envirScore': 0,  # 店面环境
                        'efficiencyScore': 0,  # 维修效率
                        'allComment': 0,  # 评价满意度
                        'periodStart': month[0],  # 时期 用每月第一天表示
                        'periodEnd': month[1],
                    }
                print('按照月统计：', monthly_data)
                mongo_client.statistics.commentsstatistics.replace_one(
                    {'statsType': 4, 'cityCode': citycode, 'periodStart': month[0], 'periodEnd': month[1],
                     'dataType': 3, 'repairType': k[1]},
                    monthly_data, upsert=True)

    # 按照季度统计
    for k, v in category_relatived_comments.items():
        def in_season(seasonperiod, target_date):
            """根据日期判断一个日期是否在日期时间段内"""
            if seasonperiod[0] - timedelta(hours=8) <= target_date < (
                            seasonperiod[1] + timedelta(days=1) - timedelta(hours=8)):
                return True
            return False

        # 生成被统计的日期区间
        seasons = create_season_list('2015-12-01', today)
        if len(v) == 0:  # 如果某一企业经营类别的评价数为0,则全部时间段设置成默认值
            for season in seasons:
                seasonly_data = {  # 全部数据
                    'statsType': 4,  # 统计类型 1-满意度 2-维修类别 3-车辆类型 4-经营类别 5-车辆品牌
                    'dataType': 4,  # 周期类型:1-全部数据 2-周统计 3-月统计 4-季度统计
                    'repairType': k[1],  # 企业经营类别代码 2位数字
                    'cityCode': citycode,
                    'serviceScore': 0,  # 服务态度
                    'priceScore': 0,  # 维修价格
                    'qualityScore': 0,  # 服务质量
                    'envirScore': 0,  # 店面环境
                    'efficiencyScore': 0,  # 维修效率
                    'allComment': 0,  # 评价满意度
                    'periodStart': season[0],  # 时期 用每月第一天表示
                    'periodEnd': season[1],
                }
                print('按照季度统计：', seasonly_data)
                mongo_client.statistics.commentsstatistics.replace_one(
                    {'statsType': 4, 'cityCode': citycode, 'periodStart': season[0], 'periodEnd': season[1],
                     'dataType': 4, 'repairType': k[1]},
                    seasonly_data, upsert=True)
        else:
            for season in seasons:  # 分季度
                seasonly_service_score = 0
                seasonly_price_score = 0
                seasonly_quality_score = 0
                seasonly_envir_score = 0
                seasonly_efficiency_score = 0
                count = 0
                satisfied_count = 0

                for comment in v:
                    if in_season(season, comment.get('created')):
                        count += 1
                        seasonly_service_score += comment.get('serviceScore', 0)
                        seasonly_price_score += comment.get('priceScore', 0)
                        seasonly_quality_score += comment.get('qualityScore', 0)
                        seasonly_envir_score += comment.get('envirScore', 0)
                        seasonly_efficiency_score += comment.get('efficiencyScore', 0)
                        if comment.get('allComment', 0) >= 2:
                            satisfied_count += 1

                if count > 0:
                    seasonly_data = {
                        'statsType': 4,  # 统计类型 1-满意度 2-维修类别 3-车辆类型 4-经营类别 5-车辆品牌
                        'dataType': 4,  # 周期类型:1-全部数据 2-周统计 3-月统计 4-季度统计
                        'repairType': k[1],  # 企业经营类别代码 2位数字
                        'cityCode': citycode,
                        'serviceScore': round(seasonly_service_score / count, 1),  # 服务态度
                        'priceScore': round(seasonly_price_score / count, 1),  # 维修价格
                        'qualityScore': round(seasonly_quality_score / count, 1),  # 服务质量
                        'envirScore': round(seasonly_envir_score / count, 1),  # 店面环境
                        'efficiencyScore': round(seasonly_efficiency_score / count, 1),  # 维修效率
                        'allComment': round(satisfied_count / count, 3),  # 评价满意度
                        'periodStart': season[0],  # 时期
                        'periodEnd': season[1],
                    }
                else:
                    seasonly_data = {
                        'statsType': 4,  # 统计类型 1-满意度 2-维修类别 3-车辆类型 4-经营类别 5-车辆品牌
                        'dataType': 4,  # 周期类型:1-全部数据 2-周统计 3-月统计 4-季度统计
                        'repairType': k[1],  # 企业经营类别代码 2位数字
                        'cityCode': citycode,
                        'serviceScore': 0,  # 服务态度
                        'priceScore': 0,  # 维修价格
                        'qualityScore': 0,  # 服务质量
                        'envirScore': 0,  # 店面环境
                        'efficiencyScore': 0,  # 维修效率
                        'allComment': 0,  # 评价满意度
                        'periodStart': season[0],  # 时期
                        'periodEnd': season[1],
                    }
                print('按照季度统计：', seasonly_data)
                mongo_client.statistics.commentsstatistics.replace_one(
                    {'statsType': 4, 'cityCode': citycode, 'periodStart': season[0], 'periodEnd': season[1],
                     'dataType': 4, 'repairType': k[1]},
                    seasonly_data, upsert=True)


if __name__ == '__main__':
    statistics_category('371100')
