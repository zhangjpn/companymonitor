# -*-coding:utf-8 -*-

import csv
import os.path as path

base_path = path.dirname(__file__)
codetable = path.join(base_path, 'codetable.csv')


class CodeTable(object):
    """全国区域代码表"""

    def __init__(self):
        self.codetable = []
        with open(file=codetable, mode='r') as codetablefile:
            r = csv.reader(codetablefile)
            for li in r:
                self.codetable.append(li)

    def get_province_code(self, province_name):
        pass

    def get_province_name(self, province_code):
        pass

    def get_city_code(self, city_name):
        pass

    def get_city_name(self, city_code):
        pass
    def get_city_codes(self):
        """返回所有的城市代码"""
        city_codes = []
        for li in self.codetable:
            city_codes.append(li[1] + li[3] + '00')
        return city_codes
    def get_county_code(self, county_name):
        pass

    def get_county_name(self, county_code):
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
                countylist.append([li[4], li[1] + li[3] + li[5]])

        return countylist


if __name__ == '__main__':
    with open(file='codetable.csv', mode='r') as f:
        reader = csv.reader(f)
        for i in reader:
            print(i)
