/**
 * Company model.
 *
 * @author
 * @copyright
 * @license
 */
'use strict';

/**
 * Module dependencies.
 */
var crypto   = require('crypto');
var mongoose = require('mongoose');
var Mobile   = require('../mobile/mobile.model.js');
//var User = require('../user/user.model.js');

/**
 * Company Schema
 */
var CompanySchema = new mongoose.Schema({
    name: { //企业名称
        type: String,
        trim: true,
        required: true
    },
    ID: { //企业系统ID
        type: String,
        trim: true,
        required: true
    },
    businessLicense: { //经营许可证
        type: String,
        trim: true
    },
    socialCode: { //统一社会信用代码
        type: String,
        trim: true,
        index:{
            unique: true
        },
        required: true
    },
    address: { //详细地址
        type: String,
        trim: true,
        required: true
    },
    scope: { //经营范围
        type: String,
        trim: true,
        required: true
    },
    businessPhoto: { //营业执照照片
        type: String, //url
        trim: true,
        required: true
    },
    licenseNo: { //道路运输经营许可证号
        type: String,
        trim: true
    },
    licensePublish: { //发证日期
        // type: Date
        type: String,
        trim: true
    },
    licenseBegin: { //开始日期
        // type: Date
        type: String,
        trim: true
    },
    licenseEnd: { //结束日期
        // type: Date
        type: String,
        trim: true
    },
    roadPhoto: { //道理运输许可照片
        type: String, //url
        trim: true
    },
    contactName: { //企业联系人姓名
        type: String,
        trim: true
    },
    category: { //企业经营业务类别
        type: Number
    },
    legalPerson: { //法人负责人姓名
        type: String,
        trim: true,
        required: true
    },
    IDNumber: { //身份证件号
        type: String,
        trim: true,
        required: true
    },
    idfront: { //身份证照片正面
        type: String,
        trim: true,
        required: true
    },
    idback: { //身份证照片反面
        type: String,
        trim: true,
        required: true
    },
    legalMobile: { //法人联系方式
        type: String,
        trim: true,
        required: true
    },
    mobile: { //企业联系人联系方式
        type: String,
        trim: true
    },
    accountId: {//维修企业
        type: mongoose.Schema.Types.ObjectId,
        ref: Mobile
    },
    status: { //公司状态,1:审核中，2:审核失败, 3:审核成功
        type: Number,
        default: 1
    },
    provinceCode: { //公司省份代码
        type: Number,
        required: true
    },
    cityCode: { //公司市级代码
        type: Number,
        required: true
    },
    countyCode:{ //区域编码
        type: Number
    },
    businessType: { //维修企业经营类型
        type: Number
    },
    operator:{ //操作人
        type: String,
        trim: true
    },
    remarks:{ //审核备注信息
        type: String,
        trim: true
    },
    score:{ //企业评分
        type: Number
    },
    level:{ //企业等级
        type: Number
    },
    serviceScore:{ //服务评分,1：差， 2：一般，3：好，4：很好，5：满意
        type:Number,
        default: 0
    },
    priceScore:{ //价格评分
        type:Number,
        default: 0
    },
    qualityScore:{ //质量评分
        type:Number,
        default: 0
    },
    envirScore:{ //环境评分
        type:Number,
        default: 0
    },
    efficiencyScore:{ //效率评分
        type:Number,
        default: 0
    },
    businessStatus:{ //企业经营状况
        type: Number
    },
    // longitude:{ //经度
    //     type: String,
    //     trim: true
    // },
    // latitude:{ //纬度
    //     type: String,
    //     trim: true
    // },
    dstCoordinates : {
        type:{
            latitude: Number, //纬度,
            longitude: Number  //经度
        }
    },
    updated: { //创建日期
        type: Date
    },
    created: { //更新日期
        type: Date,
        default: Date.now
    }
});


module.exports = mongoose.model('Company', CompanySchema);
