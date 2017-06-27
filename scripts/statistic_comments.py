# -*-codint:utf-8 -*-

from pymongo import MongoClient
from datetime import datetime, timedelta, tzinfo
from app.base_class import CodeTable
from app.commontools import create_week_list, create_month_list, create_season_list


class UTC(tzinfo):
    """UTC时区"""

    def __init__(self, offset=0):
        self._offset = offset

    def utcoffset(self, dt):
        return timedelta(hours=self._offset)

    def tzname(self, dt):
        return "UTC +%s" % self._offset

    def dst(self, dt):
        return timedelta(hours=self._offset)


def collect_comments(citycode):
    """获取城市的满意度数据，全部历史数据，过去一周的，过去一个月的，过去一个季度的满意度数据"""
    mongo_client = MongoClient(host='127.0.0.1', port=27017)

    # 获取某个城市的评价数
    comments = mongo_client.spv1.comments.find({'status': 1})
    target_comments = []
    comments_count = 0
    for comment in comments:  # 需要重写
        relatived_company = mongo_client.spv1.companies.find_one(comment.get('company'))
        _city_code = str(int(relatived_company.get('cityCode', 0)))
        _county_code = str(int(relatived_company.get('countyCode', 0)))
        _province_code = str(int(relatived_company.get('provinceCode', 0)))
        if _city_code == citycode:
            comment['provinceCode'] = _province_code
            comment['cityCode'] = _city_code
            comment['countyCode'] = _county_code
            target_comments.append(comment)
            comments_count += 1

    # 获取某个城市的所有好评数
    satisfied_count = 0
    for tcomment in target_comments:
        if tcomment.get('allComment') >= 2:
            satisfied_count += 1
    # 总体满意度
    if comments_count > 0:
        total_satisfied_rate = round(satisfied_count / comments_count, 3)  # 小数
    else:
        total_satisfied_rate = 1
    general_data = {
        'datatype': 0,  # 全局数据
        'cityCode': citycode,
        'commentsNum': comments_count,
        'satisfiedComments': satisfied_count,
        'satisfiedRate': total_satisfied_rate,
        'periodStart': 'untilnow',
        'periodEnd': 'untilnow',
    }
    print('全局数据:', general_data)
    # 单个城市满意度评价的总体数据
    mongo_client.statistics.commentsstatistics.replace_one(
        {'datatype': 0, 'cityCode': citycode, 'periodStart': 'untilnow'},
        general_data, upsert=True)
    # 按照分区统计满意度数据
    province_code_abbr = citycode[0:2]
    city_code_abbr = citycode[2:4]
    codetable = CodeTable()
    countylist = codetable.get_belong_county_info(province_code_abbr, city_code_abbr)  # 获取市内区域代码列表

    area_relatived_comments = {}  # 按照分区储存评论数据
    for county_info in countylist:
        temp_comment_list = []
        for tcomment in target_comments:
            if tcomment.get('countyCode') == county_info[1]:
                temp_comment_list.append(tcomment)
        area_relatived_comments[(county_info[0], county_info[1])] = temp_comment_list  # [comment1, comment2, ]

    # 全部数据，按照分区统计分区内各项评价指标
    for k, v in area_relatived_comments.items():
        service_score = 0
        price_score = 0
        quality_score = 0
        envir_score = 0
        efficiency_score = 0
        c_count = len(v)
        if c_count > 0:
            temp_count = 0
            for c in v:
                if c.get('allComment') >= 2:
                    temp_count += 1
                service_score += c.get('serviceScore', 0)
                price_score += c.get('priceScore', 0)
                quality_score += c.get('qualityScore', 0)
                envir_score += c.get('envirScore', 0)
                efficiency_score += c.get('efficiencyScore', 0)
            area_data = {  # 全部数据
                'datatype': 1,  # 文档类型:0-全局数据 1-全部数据 2-周统计 3-月统计 4-季度统计
                'county': k[0],  # 辖区名称
                'countyCode': k[1],  # 辖区代码 6位字符
                'cityCode': citycode,  # 城市代码 6位字符串
                'serviceScore': round(service_score / c_count, 1),  # 服务态度
                'priceScore': round(price_score / c_count, 1),  # 维修价格
                'qualityScore': round(quality_score / c_count, 1),  # 服务质量
                'envirScore': round(envir_score / c_count, 1),  # 店面环境
                'efficiencyScore': round(efficiency_score / c_count, 1),  # 维修效率
                'allComment': round(temp_count / c_count, 3),  # 评价满意度
                'periodStart': 'untilnow',  # 时期
                'periodEnd': 'untilnow',  # 时期
            }
        else:
            area_data = {  # 全部数据
                'datatype': 1,  # 文档类型:0-全局数据 1-全部数据 2-周统计 3-月统计 4-季度统计
                'county': k[0],  # 辖区名称
                'countyCode': k[1],  # 辖区代码 6位字符
                'cityCode': citycode,  # 城市代码 6位字符串
                'serviceScore': 0,  # 服务态度
                'priceScore': 0,  # 维修价格
                'qualityScore': 0,  # 服务质量
                'envirScore': 0,  # 店面环境
                'efficiencyScore': 0,  # 维修效率
                'allComment': 0,  # 评价满意度
                'periodStart': 'untilnow',  # 时期
                'periodEnd': 'untilnow',  # 时期
            }
        # 按照辖区写入数据库
        print('辖区全部数据', area_data)
        mongo_client.statistics.commentsstatistics.replace_one({'datatype': 1, 'county': [0], 'countyCode': k[1]},
                                                               area_data, upsert=True)

    # 按照自然周统计
    for k, v in area_relatived_comments.items():
        # 生成按照自然周的时间段
        def in_week(weekperiod, target_date):
            """根据日期判断一个日期是否在日期时间段内"""
            if weekperiod[0] <= target_date < (weekperiod[1] + timedelta(days=1)):
                return True
            return False

        today = datetime.today().strftime('%Y-%m-%d')
        weeks = create_week_list('2016-07-01', today)

        for week in weeks:
            # 按照周统计
            weekly_service_score = 0
            weekly_price_score = 0
            weekly_quality_score = 0
            weekly_envir_score = 0
            weekly_efficiency_score = 0
            count = 0
            satisfied_count = 0
            if v:
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
                    weekly_data = {  # 全部数据
                        'datatype': 2,  # 文档类型:0-全局数据 1-全部数据 2-周统计 3-月统计 4-季度统计
                        'county': k[0],  # 辖区名称
                        'countyCode': k[1],  # 辖区代码 6位字符
                        'cityCode': citycode,  # 城市代码 6位字符串
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
                    weekly_data = {  # 全部数据
                        'datatype': 2,  # 文档类型:0-全局数据 1-全部数据 2-周统计 3-月统计 4-季度统计
                        'county': k[0],  # 辖区名称
                        'countyCode': k[1],  # 辖区代码 6位字符
                        'cityCode': citycode,  # 城市代码 6位字符串
                        'serviceScore': 0,  # 服务态度
                        'priceScore': 0,  # 维修价格
                        'qualityScore': 0,  # 服务质量
                        'envirScore': 0,  # 店面环境
                        'efficiencyScore': 0,  # 维修效率
                        'allComment': 0,  # 评价满意度
                        'periodStart': week[0],  # 时期
                        'periodEnd': week[1],  # 时期
                    }
            else:
                weekly_data = {  # 全部数据
                    'datatype': 2,  # 文档类型:0-全局数据 1-全部数据 2-周统计 3-月统计 4-季度统计
                    'county': k[0],  # 辖区名称
                    'countyCode': k[1],  # 辖区代码 6位字符
                    'cityCode': citycode,  # 城市代码 6位字符串
                    'serviceScore': 0,  # 服务态度
                    'priceScore': 0,  # 维修价格
                    'qualityScore': 0,  # 服务质量
                    'envirScore': 0,  # 店面环境
                    'efficiencyScore': 0,  # 维修效率
                    'allComment': 0,  # 评价满意度
                    'periodStart': week[0],  # 时期
                    'periodEnd': week[1],  # 时期
                }
            print('按照自然周统计：', weekly_data)
            mongo_client.statistics.commentsstatistics.replace_one(
                {'periodStart': week[0], 'periodEnd': week[1], 'datatype': 2, 'county': k[0], 'countyCode': k[1]},
                weekly_data, upsert=True)

    # 按照自然月统计
    for k, v in area_relatived_comments.items():
        def in_month(monthperiod, target_date):
            """根据日期判断一个日期是否在日期时间段内"""
            if monthperiod[0] <= target_date < (monthperiod[1] + timedelta(days=1)):
                return True
            return False

        # 生成被统计的日期区间
        today = datetime.today().strftime('%Y-%m-%d')
        months = create_month_list('2016-07-01', today)

        for month in months:
            # 按照月统计
            monthly_service_score = 0
            monthly_price_score = 0
            monthly_quality_score = 0
            monthly_envir_score = 0
            monthly_efficiency_score = 0
            count = 0
            satisfied_count = 0
            if v:
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
                    monthly_data = {  # 全部数据
                        'datatype': 3,  # 文档类型:0-全局数据 1-全部数据 2-周统计 3-月统计 4-季度统计
                        'county': k[0],  # 辖区名称
                        'countyCode': k[1],  # 辖区代码 6位字符
                        'cityCode': citycode,  # 城市代码 6位字符串
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
                    monthly_data = {  # 全部数据
                        'datatype': 3,  # 文档类型:0-全局数据 1-全部数据 2-周统计 3-月统计 4-季度统计
                        'county': k[0],  # 辖区名称
                        'countyCode': k[1],  # 辖区代码 6位字符
                        'cityCode': citycode,  # 城市代码 6位字符串
                        'serviceScore': 0,  # 服务态度
                        'priceScore': 0,  # 维修价格
                        'qualityScore': 0,  # 服务质量
                        'envirScore': 0,  # 店面环境
                        'efficiencyScore': 0,  # 维修效率
                        'allComment': 0,  # 评价满意度
                        'periodStart': month[0],  # 时期 用每月第一天表示
                        'periodEnd': month[1],
                    }
            else:
                monthly_data = {  # 全部数据
                    'datatype': 3,  # 文档类型:0-全局数据 1-全部数据 2-周统计 3-月统计 4-季度统计
                    'county': k[0],  # 辖区名称
                    'countyCode': k[1],  # 辖区代码 6位字符
                    'cityCode': citycode,  # 城市代码 6位字符串
                    'serviceScore': 0,  # 服务态度
                    'priceScore': 0,  # 维修价格
                    'qualityScore': 0,  # 服务质量
                    'envirScore': 0,  # 店面环境
                    'efficiencyScore': 0,  # 维修效率
                    'allComment': 0,  # 评价满意度
                    'periodStart': month[0],  # 时期 用每月第一天表示
                    'periodEnd': month[1],
                }
            print('按照自然月统计：', monthly_data)
            mongo_client.statistics.commentsstatistics.replace_one(
                {'periodStart': month[0], 'periodEnd': month[1], 'datatype': 3, 'county': k[0], 'countyCode': k[1]},
                monthly_data,
                upsert=True)

    # 按照季度统计
    for k, v in area_relatived_comments.items():
        # v辖区内评论列表
        def in_season(seasonperiod, target_date):
            """根据日期判断一个日期是否在日期时间段内"""
            if seasonperiod[0] <= target_date < (seasonperiod[1] + timedelta(days=1)):
                return True
            return False

        today = datetime.today().strftime('%Y-%m-%d')
        seasons = create_season_list('2016-07-01', today)
        # 根据每个季度统计
        for season in seasons:  # 分季度
            seasonly_service_score = 0
            seasonly_price_score = 0
            seasonly_quality_score = 0
            seasonly_envir_score = 0
            seasonly_efficiency_score = 0
            count = 0
            satisfied_count = 0
            if v:
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
                    seasonly_data = {  # 全部数据
                        'datatype': 4,  # 文档类型:0-全局数据 1-全部数据 2-周统计 3-月统计 4-季度统计
                        'county': k[0],  # 辖区名称
                        'countyCode': k[1],  # 辖区代码 6位字符
                        'cityCode': citycode,  # 城市代码 6位字符串
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
                    seasonly_data = {  # 全部数据
                        'datatype': 4,  # 文档类型:0-全局数据 1-全部数据 2-周统计 3-月统计 4-季度统计
                        'county': k[0],  # 辖区名称
                        'countyCode': k[1],  # 辖区代码 6位字符
                        'cityCode': citycode,  # 城市代码 6位字符串
                        'serviceScore': 0,  # 服务态度
                        'priceScore': 0,  # 维修价格
                        'qualityScore': 0,  # 服务质量
                        'envirScore': 0,  # 店面环境
                        'efficiencyScore': 0,  # 维修效率
                        'allComment': 0,  # 评价满意度
                        'periodStart': season[0],  # 时期
                        'periodEnd': season[1],
                    }
            else:
                seasonly_data = {  # 全部数据
                    'datatype': 4,  # 文档类型:0-全局数据 1-全部数据 2-周统计 3-月统计 4-季度统计
                    'county': k[0],  # 辖区名称
                    'countyCode': k[1],  # 辖区代码 6位字符
                    'cityCode': citycode,  # 城市代码 6位字符串
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
                {'periodStart': season[0], 'periodEnd': season[1], 'datatype': 4, 'county': k[0], 'countyCode': k[1]},
                seasonly_data, upsert=True)


if __name__ == '__main__':
    city_codes = CodeTable().get_city_codes()
    for citycode in city_codes:
        collect_comments(citycode)
