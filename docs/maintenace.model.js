/**
 * Maintenace model.
 *
 * @author
 * @copyright
 * @license
 */
'use strict';

/**
 * Module dependencies.
 */
var mongoose = require('mongoose');
var Company = require('../company/company.model.js');
var Store = require('../store/store.model')
/**
 * Maintenace Schema
 */
var MaintenaceSchema = new mongoose.Schema({
    plateNo: { //车牌号码
        type: String,
        trim: true,
        required: true
    },
    engineNo: { //发动机号码
        type: String,
        trim: true
    },
    statementNo: { //结算清单编号
        type: String,
        trim: true,
        index: {
            unique: true
        },
        required: true
    },
    settlementDate: { //结算日期
        type: Date
    },
    deliveryDate: { //送修日期
        type: Date
    },
    deliveryMileage: { //送修里程
        type: Number
    },
    description: { //故障信息
        type: String,
        trim: true
    },
    repairItems: { //维修项目列表
        type: [{
            name: String, //维修项目名称
            hours: Number, //维修工时
            price: Number, //维修工时单价
            cost: Number //金额
        }]
    },
    repairParts: { //维修配件列表
        type: [{
            name: String, //配件名称
            partNo: String, //配件编码
            brand: String, //品牌
            quantity: Number, //配件数量
            attribute: String, //配件属性
            self: Boolean, //是否为自备配件
            price: Number, //单价
            cost: Number //金额
        }]
    },
    others: { //其他费用列表
        type: [{
            name: String, //其他费用项目名称
            cost: Number //金额
        }]
    },
    sum: { //总费用
        type: {
            cost: Number, //"总费用":"3600",
		    realCost: Number  //"实收总费用":"2700"
        }
    },
    QAInfo: { //质保信息
        type: {
            qaMileage: Number, //"质量保证里程":"100000",
		    qaDate: Date  //"质量保证时间":"2019-03-06"
        }
    },
    VINCode:{ //VIN码
        type: String,
        trim: true
    },
    vehicleOwner: { //车辆所有者
        type: String,
        trim: true
    },
    vehicleBrand: { //车辆品牌
        type: String,
        trim: true
    },
    vehicleType: { //车辆类型
        type: Number
    },
    repairType: { //维修类型
        type: Number
    },
    repairName: { // 送修人名称
        type: String,
        trim: true
    },
    repairMobile: { // 送修人联系方式
        type: String,
        trim: true
    },
    source: { // 维修表单来源：1:新增，2：上传，3：接口
        type: Number
    },
    status: { // 维修表单是否同步，0:未同步，1：同步
        type: Number,
        default: 1
    },
    integratedRate: { // 表单完整率 0:不合格，1:高，2:中，3:低，
        type: Number
    },
    companyId: {//维修企业
        type: mongoose.Schema.Types.ObjectId,
        ref: Company
    },
    xlsxPath:{ //XLSX文件下载
        type: String,
        trim: true
    },
    originalXLSXName: { //原xlsx名称
        type: String,
        trim: true
    },
    xlsxStatus: {//数据标准化,0: 标准中，1:已标准, 2:标准失败
        type: Number,
        default: 1
    },
     factoryDate: { //出厂日期
        type: Date
     },
     factoryMileage: { //出厂里程
        type: Number
     },
    updated: { //更新日期
        type: Date,
        default: Date.now
    },
    created: { //创建日期
        type: Date,
        default: Date.now
    },
    is_status_fix:{ //非标准数据,0: 未确认，1:已确认， 2:已核对确认
        type: Number,
        default: 0
    },
    store: { //关联对应门店
        type: mongoose.Schema.Types.ObjectId,
        ref: Store
    },
    commentStatus:{ //评论状态，0：未评价，1：已评价
        type: Number,
        default: 0
    },
    complaint_status:{ //投诉状态，0：没有进行投诉，1：投诉处理中，2：投诉处理完成
        type: Number,
        default: 0
    }
});

module.exports = mongoose.model('Maintenace', MaintenaceSchema);
