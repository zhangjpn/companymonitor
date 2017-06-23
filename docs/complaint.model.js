/**
 * complaint model.
 *
 * @author
 * @copyright
 * @license
 */
'use strict';


var mongoose = require('mongoose');
var Maintenace   = require('../maintenace/maintenace.model');
var User   = require('../user/user.model');
var Store   = require('../store/store.model');
var Company = require('../company/company.model');

var ComplaintSchema = new mongoose.Schema({
    statementNo: { //结算清单编号
        type: String,
        trim: true,
        index: {
            unique: true
        },
        required: true
    },
    plateNo: { //车牌号码
        type: String,
        trim: true,
    },
    VINCode:{ //VIN码
        type: String,
        trim: true
    },
    companyName:{ //维修企业名称
        type: String,
        trim: true
    },
    storeName:{ //维修门店名称
        type: String,
        trim: true
    },
    repairType: { //维修类型
        type: Number
    },
    description: { //故障信息
        type: String,
        trim: true
    },
    factoryDate: { //出厂日期
        type: Date
    },
    factoryMileage: { //出厂里程
        type: Number
    },
    QAInfo: { //质保信息
        type: {
            qaMileage: Number, //"质量保证里程":"100000",
            qaDate: Date  //"质量保证时间":"2019-03-06"
        }
    },
    deliveryMileage: { //送修里程
        type: Number
    },
    settlementDate: { //结算日期
        type: Date
    },
    vehicleType: { //车辆类型
        type: Number
    },
    vehicleBrand: { //车辆品牌
        type: String,
        trim: true
    },
    repairName: { // 送修人名称
        type: String,
        trim: true
    },
    repairMobile: { // 送修人联系方式
        type: String,
        trim: true
    },
    complaintUser: { //投诉人
        type: String,
        trim: true
    },
    phone: { //投诉人联系电话
        type: String,
        trim: true
    },
    content: { //投诉原因
        type: String,
        trim: true
    },
    scope: { //投诉原因的描述
        type: String,
        trim: true
    },
    imgId:{
        type: [{
            id: String, //图片ID
        }]
    },
    imgsArr:{
        type: [{
            imgUrl:String
        }]
    },
    imgs:{
        type: String,
        trim: true
    },
    status: { //投诉状态,1:新增投诉，2:投诉处理中, 3:投诉处理完成, 4:企业不受理
        type: Number,
        default: 1
    },
    provinceCode: { //省份代码
        type: Number,
    },
    cityCode: { //市级代码
        type: Number,
    },
    countyCode:{ //区域编码
        type: Number
    },
    company: {//维修企业
        type: mongoose.Schema.Types.ObjectId,
        ref: Company
    },
    maintenace:{ //关联维修单
        type: mongoose.Schema.Types.ObjectId,
        ref: Maintenace
    },
    user: {//关联用户
        type: mongoose.Schema.Types.ObjectId,
        ref: User
    },
    store: {//关联门店
        type: mongoose.Schema.Types.ObjectId,
        ref: Store
    },
    updated: { //更新日期
        type: Date
    },
    created: { //创建日期
        type: Date,
        default: Date.now
    }
});

module.exports = mongoose.model('complaint', ComplaintSchema);