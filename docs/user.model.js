/**
 * User model.
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
var Roles = require('../permissions/permissions.roles_model');



/**
 * User Schema
 */
var UserSchema = new mongoose.Schema({
    name: {
        type: String,
        trim: true,
        //validate: [validateLocalStrategyProperty, 'Please fill in your name']
    },
    mobile: {
        type: String,
        trim: true,
        unique: true,
        required: true
        //validate: [validateLocalStrategyProperty, 'Please fill in your mobile'],
        // match: [/.+\@.+\..+/, 'Please fill a valid mobile number']
    },
    password: {
        type: String,
        required: true
    },
    roles :{ // 普通用户:0, 监管:1, 维修企业:2, 营运企业:3,车主:4, 系统管理人员:6
        type: Number,
        default: 0
    },
    is_admin:{//是否超级管理员
        type: Boolean,
        default: false
    },
    is_active:{//是否启用
        type: Boolean,
        default: true
    },
    parentId:{ //用户的父级
        type: String,
        trim: true
    },
    is_role_admin:{//是否角色管理员
        type: Boolean,
        default: false
    },
    regulator: {// 监管角色，1:区级监管，2:市级监管，3:省级监管
        type: Number
    },
    provinceCode: { //省份代码
        type: Number
    },
    cityCode: { //市级代码
        type: Number
    },
    countyCode:{ //区域编码
        type: Number
    },
    roleId: {//角色的ID
        type:mongoose.Schema.Types.ObjectId,
        ref: Roles
    },
    sub_region:{ //所属区域
        type: String,
        trim: true
    },
    wx_token:{ //获取微信openid
        type: String,
        trim: true
    },
    al_token:{ //获取支付宝token
        type: String,
        trim: true
    },
    avatar: { //用户头像
        type: String,
        trim: true
    },
    department:{ //用户所属部门 0：运维，1：开发，2：产品
        type: Number
    },
    mobileBindStatus:{ //绑定状态：0：未绑定，1：已绑定
        type:Number,
        default: 0
    },
    updated: {
        type: Date
    },
    created: {
        type: Date,
        default: Date.now
    },
    sex: { //性别 1为男性 2为女性
        type: String,
        trim: true
    },
    city:{
        type: String,
        trim: true
    },
    province: {
        type: String,
        trim: true
    }
});


/**
 * Pre-save hook (execute before each user.save() call)
 */
UserSchema.pre('save', function(next) {
    var mobile = this;
    const hash = crypto.createHash('sha256');
    hash.update(mobile.password);
    mobile.password = hash.digest('hex');
    next();

});

UserSchema.methods.comparePassword = function(password, cb) {
    const hash = crypto.createHash('sha256');
    hash.update(password);
    var pwdHash = hash.digest('hex');
    if (pwdHash === this.password) {
        cb(null, true);
    } else {
        cb(null, false);
    }
};

UserSchema.virtual('is_valid').get(function(){
  if(this.mobileBindStatus==1){
    return true;
  }
  return false;
});

UserSchema.statics.find_by_openid = function(openid, cb) {
  return this.findOne({
    wx_token: openid
  }, cb);
};
module.exports = mongoose.model('User', UserSchema);

