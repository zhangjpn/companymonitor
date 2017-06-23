/**
 * comments
 * user authentication
 */
'use strict';
var mongoose = require('mongoose');
var Store = require('../store/store.model');
var ObjectId = mongoose.Schema.Types.ObjectId;
var Maintenace = require('../maintenace/maintenace.model');
var User = require('../user/user.model');
var Company = require('../company/company.model');



var CommentsSchema = new mongoose.Schema({
    content:{ //评论内容
        type:String,
        trim: true
    },
    allComment:{ //总体评价，1：不满意，2：满意，3：非常满意
        type:Number,
        default: 2
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
    company: {//维修企业
        type: ObjectId,
        ref: Company
    },
    store:{ //关联的维修门店
        type: ObjectId,
        ref: Store
    },
    maintenace:{ //关联的维修订单
        type: ObjectId,
        ref: Maintenace
    },
    user:{ //关联用户
        type: ObjectId,
        ref: User
    },
    status:{ //评论状态, 0：待审核评论，1：已通过的评论，2：未通过的评论
        type:Number,
        default: 1
    },
    statementNo: { //结算清单编号
        type: String,
        trim: true,
    },
    plateNo: { //车牌号码
        type: String,
        trim: true,
    },
    VINCode:{ //VIN码
        type: String,
        trim: true
    },
    repairType:{ //维修类别
        type:Number,
        trim: true
    },
    commentUser:{ //关联评论用户名称
        type: String,
        trim: true
    },
    is_recommend:{ //是否为推荐评价 1：是，2：不是
        type:Number,
        default: 1
    },
    remarks:{ //评论审核备注信息
        type: String,
        trim: true
    },
    operator:{ //操作人
        type: String,
        trim: true
    },
    is_checked:{//企业是否查看, 0：未查看，1：已查看
        type:Number,
        default: 0
    },
    updated: { //创建日期
        type: Date,
    },
    created: { //更新日期
        type: Date,
        default: Date.now
    }
});

module.exports = mongoose.model('Comments', CommentsSchema);