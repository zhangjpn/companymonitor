


### 接口说明

[GET] /monitor/admin/statistics/total
参数：
    from='2017.01.04'  字符串类型
    to='2017.02.03'  字符串类型
    citycode='371100'  长度为6的字符串类型
返回值：
    {
        'code':'200',
        'companies':[
                {'date':'2016-06-01','东港区':4,'市辖区':7,'岚山区':2,...},
                {'date':'2016-06-02','东港区':4,'市辖区':7,'岚山区':2,...},
                {'date':'2016-06-03','东港区':4,'市辖区':7,'岚山区':2,...},
                ],
        'cars':[],维修车辆数
        'carfixrecords':[],维修记录数
        'rates':[],评价量
        'averagescores':[], 平均评价得分
        'complaints':[],投诉量
    }

## 数据库说明
统计量储存位置spv1.companiesstatistics


评论统计：
        spv1.commentsstatistics

投诉统计：
        spv1.complaintsstatistics


维修企业数统计[GET] http://192.168.0.151:5000/commonapi/admin/statistics/companies
评论数统计[GET] http://192.168.0.151:5000/commonapi/admin/statistics/comments
投诉量统计[GET] http://192.168.0.151:5000/commonapi/admin/statistics/complaints
参数：
    from='2017.01.04'或'2017-01-04' 字符串类型
    to='2017.02.03' 或'2017-02-03' 字符串类型
    citycode='371100'  长度为6的字符串类型
    from和to两个只传一个时取有值的一个
    from和to都缺失时默认为今天
    citycode缺失时时默认为日照市'371100'
返回值：
    {'code':'200',
     rows:[
        {'date':ISO(...),'东港区':1,'市辖区':5...}
        {'date':ISO(...),'东港区':1,'市辖区':5...}
     ]}
     
     
     
投诉处理：
投诉量：complaintsNum/maintenacesNum
申诉量：complaintsNum/maintenacsNum


