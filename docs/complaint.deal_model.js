/**
 * complaint model.
 *
 * @author
 * @copyright
 * @license
 */
'use strict';


var mongoose = require('mongoose');
var Complaint = require('./complaint.model');
var Company = require('../company/company.model');
var User   = require('../user/user.model');

var ComplaintDealSchema = new mongoose.Schema({
    complaint:{ //关联投诉维修单
        type: mongoose.Schema.Types.ObjectId,
        ref: Complaint
    },
    solveStatus: {//解决状态，1：不满意，2：满意，3：非常满意
        type:Number,
    },
    dealstatus: { //处理状态, 0:车主 未做任何反馈，1:首次投诉，企业未做处理，2：车主对企业反馈进行不满意操作，
        // 3：车主对企业反馈进行满意操作，4：车主撤销投诉
        type: Number,
        default: 0
    },
    imgId:{
        type: [{
            type: String, //图片ID
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
    companyName:{ //企业名称
        type: String,
        trim: true
    },
    company:{
        type: mongoose.Schema.Types.ObjectId,
        ref: Company
    },
    userName: {//投诉人名称
        type: String,
        trim: true
    },
    user: {//关联用户
        type: mongoose.Schema.Types.ObjectId,
        ref: User
    },
    btext:{ //企业内容
        type: String,
        trim: true
    },
    ctext:{ //车主内容
        type: String,
        trim: true
    },
    acceptance:{ //企业状态：0：企业未做任何解决方案，1：企业受理，2：企业不受理
        type: Number,
    },

    btime: { //企业时间
        type: Date,
    },
    ctime: { //车主时间
        type: Date,
    },
    count:{ //记录次数
        type: Number,
        default: 1
    },
    updated: { //更新日期
        type: Date
    },
    created: { //更新日期
        type: Date,
        default: Date.now
        // type: String,
        // trim: true
    }
});

module.exports = mongoose.model('complaintdealinfo', ComplaintDealSchema);