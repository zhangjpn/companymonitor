# -*-coding:utf-8 -*-

from mongoengine import Document
from mongoengine.fields import *
from datetime import datetime

class CommentsStatistics(Document):
    """评价统计"""
    meta = {
        'db_alias': 'statistics',
        'collection': 'commentsstatistics',
        'strict': False,
    }
    statsType = IntField(required=True)  # 统计类型 1-满意度 2-维修类别 3-车辆类型 4-经营类别 5-车辆品牌
    provinceCode = StringField(default=None)  # 省编号
    cityCode = StringField(required=True)  # 城市编号
    countyCode = StringField(default=None)  # 辖区编号
    dataType = IntField(required=True)  # 周期类型: 1-全部数据 2-周统计 3-月统计 4-季度统计
    repairType = IntField(default=None)  # 维修类别
    vehicleType = IntField(default=None)  # 车辆类型
    category = IntField(default=None)  # 企业经营类别
    serviceScore = FloatField(default=0)  # 服务态度
    priceScore = FloatField(default=0)  # 维修价格
    qualityScore = FloatField(default=0)  # 服务质量
    envirScore = FloatField(default=0)  # 店面环境
    efficiencyScore = FloatField(default=0)  # 维修效率
    allComment = FloatField(default=0)  # 评价满意度
    periodStart = DateTimeField(required=True, default=datetime(2000, 1, 1))  # 周期起始日
    periodEnd = DateTimeField(required=True, default=datetime(2000, 1, 1))  # 周期终止日
    commentsNum = IntField(default=None)  # 总评论
    satisfiedComments = IntField(default=None),  # 满意数
    satisfiactionRate = FloatField(default=None)  # 历史满意度

class ComplaintsStatistics(Document):
    """评价统计"""
    meta = {
        'db_alias': 'statistics',
        'collection': 'complaintsstatistics',
        'strict': False,
    }
    statsType = IntField(required=True)  # 统计类型 1-按照辖区分类
    provinceCode = StringField(default=None)  # 省编号
    cityCode = StringField(required=True)  # 城市编号
    countyCode = StringField(default=None)  # 辖区编号
    dataType = IntField(required=True)  # 周期类型: 1-全部数据 2-周统计 3-月统计 4-季度统计
    repairType = IntField(default=None)  # 维修类别
    vehicleType = IntField(default=None)  # 车辆类型
    category = IntField(default=None)  # 企业经营类别
    serviceScore = FloatField(default=0)  # 服务态度
    priceScore = FloatField(default=0)  # 维修价格
    qualityScore = FloatField(default=0)  # 服务质量
    envirScore = FloatField(default=0)  # 店面环境
    efficiencyScore = FloatField(default=0)  # 维修效率
    allComment = FloatField(default=0)  # 评价满意度
    periodStart = DateTimeField(required=True, default=datetime(2000, 1, 1))  # 周期起始日
    periodEnd = DateTimeField(required=True, default=datetime(2000, 1, 1))  # 周期终止日
    commentsNum = IntField(default=None)  # 总评论
    satisfiedComments = IntField(default=None),  # 满意数
    satisfiactionRate = FloatField(default=None)  # 历史满意度
