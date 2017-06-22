# -*-coding:utf-8 -*-

from datetime import tzinfo, timedelta, datetime
from pymongo import MongoClient

class UTC(tzinfo):
    """UTC"""

    def __init__(self, offset=0):
        self._offset = offset

    def utcoffset(self, dt):
        return timedelta(hours=self._offset)

    def tzname(self, dt):
        return "UTC +%s" % self._offset

    def dst(self, dt):
        return timedelta(hours=self._offset)


if __name__ == '__main__':
    localnow = datetime.now(tz=UTC(8))
    utcnow = localnow.utcnow()

    client = MongoClient()
    client.test.test.insert({'localnow':localnow,'utcnow':utcnow})
