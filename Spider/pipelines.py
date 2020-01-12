# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import codecs
import hashlib
import json
import os

from scrapy.pipelines.images import ImagesPipeline
from twisted.enterprise import adbapi
from pymysql import cursors


class QuestionPipeline(object):
    def process_item(self, item, spider):
        print(item)
        return item


class QuestionImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        for ok, value in results:
            avatar_path = value["path"]
            item["avatar_path"] = avatar_path
        return item


class JsonWithEncodingPipeline(object):
    def __init__(self):
        self.file = codecs.open("article.json", 'w', encoding="utf-8")

    def process_item(self, item ,spider):
        lines = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(lines)
        return item

    def spider_close(self, spider):
        self.file.close()


class MysqlTwistedPipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        params = dict(
            host=settings['MYSQL_HOST'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWORD'],
            charset='utf8',
            cursorclass=cursors.DictCursor,
            use_unicode=True,
        )
        dbpool = adbapi.ConnectionPool("pymysql", **params)
        return cls(dbpool)

    def process_item(self, item, spider):
        # 使用twisted将mysql异步插入
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error, item)
        return item

    def do_insert(self, cursor, item):
        insert_sql, params = item.get_insert_sql()
        cursor.execute(insert_sql, params)
        return item

    def handle_error(self, failure, item):
        print("=====", failure, item)

    def open_spider(self, spider):
        pass

    def close_spider(self, spider):
        pass


# 将数据保存在es中
class ElasticsearchPipeline(object):
    def process_item(self, item, spider):
        item.save_to_es()
        return item
