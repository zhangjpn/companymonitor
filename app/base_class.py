# -*-coding:utf-8 -*-

import json
import csv


class CodeTable(object):
    """全国区域代码表"""

    def __init__(self):
        self.codetable = []
        with open(file='codetable.csv', mode='r') as f:
            r = csv.reader(f)
            for li in r:
                self.codetable.append(li)

    def getProvinceCode(self, province_name):
        pass

    def getProvinceName(self, province_code):
        pass
    def getCityCode(self, city_name):
        pass

    def getCityName(self, city_code):
        pass
    def getCountyCode(self, county_name):
        pass

    def getCountyName(self, county_code):
        pass

    def get_belong_county_info(self, province_code, city_code):
        """通过省代码和城市代码获取区县代码和名字
        :param province_code str 两位数字
        :param city_code str 两位数字
        :return county_list list
        """
        countylist = []
        for li in self.codetable:
            if province_code == li[1] and city_code == li[3]:
                countylist.append([li[4], li[1] + li[3] + li[5], 0])

        return countylist



        pass

if __name__ == '__main__':
    with open(file='codetable.csv',mode='r') as f:
        reader = csv.reader(f)
        for i in reader:
            print(i)