# -*-codint:utf-8 -*-

import requests

# url = 'http://0.0.0.0:5000/commonapi/admin/statistics/comments/satisfaction'
# params = {
#     'citycode':'371100'
#
# }
# res = requests.get(url=url,params=params)
#
# print(res.json().get('trends').get('monthly')[0].get('periodEnd'))

url = 'http://0.0.0.0:5000/commonapi/admin/statistics/comments/repairtype'
params = {
    'citycode': '371100'

}
res = requests.get(url=url, params=params)
if res.status_code == 200:
    print('*' * 30, 'trends.weekly', '*' * 30)
    print('count', len((res.json().get('trends')).get('weekly')))
    for i in (res.json().get('trends')).get('weekly'):
        print(i)

    print('*' * 30, 'trends.monthly', '*' * 30)
    print('count', len((res.json().get('trends')).get('monthly')))
    for i in (res.json().get('trends')).get('monthly'):
        print(i)
    print('*' * 30, 'trends.seasonly', '*' * 30)
    print('count', len((res.json().get('trends')).get('seasonly')))
    for i in (res.json().get('trends')).get('seasonly'):
        print(i)
else:
    print(res.status_code)
