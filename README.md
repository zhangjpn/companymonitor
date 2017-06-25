


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

