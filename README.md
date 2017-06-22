


### 接口说明

[GET] /monitor/active/companies
参数：
    from='2017.01.04'
    to='2017.02.03'
    citycode='371100'
返回值：
    {
        'code':'200',
        '':[{'countycode':'东港区','data':{'日期1':4,'日期2'：5,...},},
            {'countycode':'东港区','data':{'日期1':3,'日期2'：2,...},},
            {'countycode':'东港区','data':{'日期1':7,'日期2'：10,...},},
            ]
    }

## 数据库说明
统计量储存位置spv1.activecompanies
