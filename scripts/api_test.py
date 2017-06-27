# -*-codint:utf-8 -*-

import requests

url = 'http://0.0.0.0:5000/commonapi/admin/statistics/comments/satisfaction'
params = {
    'citycode':'371100'

}
res = requests.get(url=url,params=params)

print(res.json().get('trends').get('monthly')[0].get('periodEnd'))