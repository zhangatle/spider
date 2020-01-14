# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
import datetime
import re

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst, Join
from w3lib.html import remove_tags

from utils.common import extract_num
from settings import SQL_DATETIME_FORMAT, SQL_DATE_FORMAT

from elasticsearch_dsl.connections import connections

from models.es_types import Lagou, ZhihuQuestion, ZhihuAnswer
es = connections.create_connection(hosts=["localhost"])


# 获取搜索建议
def gen_suggests(index, info_tuple):
    used_words = set()
    suggests = []
    for text, weight in info_tuple:
        if text:
            words = es.indices.analyze(index=index, body={"analyzer": "ik_max_word", "text": "{0}".format(text)})
            analyzed_words = set([r["token"] for r in words["tokens"] if len(r["token"])>1])
            new_words = analyzed_words - used_words
        else:
            new_words = set()
        if new_words:
            suggests.append({'input': list(new_words), 'weight': weight})
    return suggests


class QuestionItem(scrapy.Item):
    title = scrapy.Field()
    content = scrapy.Field()
    topics = scrapy.Field(
        output_processor=Join(',')
    )
    read_num = scrapy.Field()
    avatar = scrapy.Field()
    avatar_path = scrapy.Field()
    url = scrapy.Field()
    url_object_id = scrapy.Field()


# 知乎提问的itemloader
class ZhihuQuestionItemLoader(ItemLoader):
    default_output_processor = TakeFirst()


# 知乎提问item
class ZhihuQuestionItem(scrapy.Item):
    id = scrapy.Field()
    topics = scrapy.Field(
        output_processor=Join(',')
    )
    url = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    answer_num = scrapy.Field(
        input_processor=MapCompose(extract_num)
    )
    comments_num = scrapy.Field(
        input_processor=MapCompose(extract_num)
    )
    follow_num = scrapy.Field(
        input_processor=MapCompose(extract_num)
    )
    view_num = scrapy.Field(
        input_processor=MapCompose(extract_num)
    )
    crawl_time = scrapy.Field()

    # 获取插入的sql
    def get_insert_sql(self):
        insert_sql = """
            insert into zhihu_question(id, topics, url, title, content, answer_num, comments_num, follow_num, view_num, crawl_time) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            on duplicate key update content=values(content), answer_num=values(answer_num), comments_num=values(comments_num), follow_num=values(follow_num), view_num=values(view_num)
        """
        params = (self['id'], self['topics'], self['url'], self['title'], self['content'], self['answer_num'], self['comments_num'], self['follow_num'], self['view_num'], self['crawl_time'])
        return insert_sql, params

    # 保存到elasticsearch
    def save_to_es(self):
        zhihu = ZhihuQuestion(meta={'id': self['id']})
        zhihu.topics = self['topics']
        zhihu.url = self['url']
        zhihu.title = self['title']
        zhihu.content = self['content']
        zhihu.answer_num = self['answer_num']
        zhihu.comments_num = self['comments_num']
        zhihu.follow_num = self['follow_num']
        zhihu.view_num = self['view_num']
        zhihu.crawl_time = self['crawl_time']
        zhihu.suggest = gen_suggests(ZhihuQuestion._index._name, ((zhihu.title, 10), (zhihu.content, 7)))
        zhihu.save()
        return


def format_datetime(value):
    return datetime.datetime.fromtimestamp(value).strftime(SQL_DATETIME_FORMAT)


# 知乎回答的Item
class ZhihuAnswerItem(scrapy.Item):
    id = scrapy.Field()
    url = scrapy.Field()
    question_id = scrapy.Field()
    author_id = scrapy.Field()
    content = scrapy.Field()
    approve_num = scrapy.Field()
    comments_num = scrapy.Field()
    create_time = scrapy.Field()
    update_time = scrapy.Field()
    crawl_time = scrapy.Field()

    # 获取插入sql
    def get_insert_sql(self):
        insert_sql = """
            insert into zhihu_answer(id, url, question_id, author_id, content, approve_num, comments_num, create_time, update_time, crawl_time)
            values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            on duplicate key update content=values(content), comments_num=values(comments_num), approve_num=values(approve_num), update_time=values(update_time)
        """

        params = (
            self['id'], self['url'], self['question_id'], self['author_id'], self['content'], self['approve_num'], self['comments_num'], format_datetime(self['create_time']), format_datetime(self['update_time']), format_datetime(self['crawl_time'])
        )
        return insert_sql, params

    # 保存数据到elasticsearch
    def save_to_es(self):
        zhihu = ZhihuAnswer(meta={'id': self['id']})
        zhihu.url = self['url']
        zhihu.question_id = self['question_id']
        zhihu.author_id = self['author_id']
        zhihu.content = self['content']
        zhihu.approve_num = self['approve_num']
        zhihu.comments_num = self['comments_num']
        zhihu.create_time = format_datetime(self['create_time'])
        zhihu.update_time = format_datetime(self['update_time'])
        zhihu.crawl_time = format_datetime(self['crawl_time'])
        zhihu.suggest = gen_suggests(ZhihuAnswer._index._name, ((zhihu.content, 7),))
        zhihu.save()
        return


# 替换"/"
def replace_splash(value):
    return value.replace("/", "")


def handle_strip(value):
    return value.strip()

# 处理地址信息
def handle_jobaddr(value):
    addr_list = value.split("\n")
    addr_list = [item.strip() for item in addr_list if item.strip() != "查看地图"]
    return "".join(addr_list)


# 拉勾职位信息的itemloader
class LagouJobItemLoader(ItemLoader):
    default_output_processor = TakeFirst()


# 拉勾item
class LagouJobItem(scrapy.Item):
    title = scrapy.Field()
    tags = scrapy.Field(
        output_processor=Join(',')
    )
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    salary = scrapy.Field()
    job_city = scrapy.Field(
        input_processor=MapCompose(replace_splash)
    )
    work_years = scrapy.Field(
        input_processor=MapCompose(replace_splash)
    )
    degree_need = scrapy.Field(
        input_processor=MapCompose(replace_splash)
    )
    job_type = scrapy.Field()
    publish_time = scrapy.Field()
    job_advantage = scrapy.Field()
    job_desc = scrapy.Field(
        input_processor=MapCompose(handle_strip)
    )
    job_address = scrapy.Field(
        input_processor=MapCompose(remove_tags, handle_jobaddr)
    )
    company_name = scrapy.Field(
        input_processor=MapCompose(handle_strip)
    )
    company_url = scrapy.Field()
    crawl_time = scrapy.Field()
    crawl_update_time = scrapy.Field()

    # 获取插入sql
    def get_insert_sql(self):
        insert_sql = """
            insert into lagou_jobs(title, url, url_object_id, salary, job_city, work_years, degree_need, job_type, publish_time, job_advantage, job_desc, job_address, company_url, company_name, id, crawl_time, crawl_update_time, tags)
            values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            on duplicate key update job_desc=values(job_desc)
        """

        id = extract_num(self["url"])
        params = (self['title'], self['url'], self['url_object_id'], self['salary'], self['job_city'], self['work_years'], self['degree_need'],
                  self['job_type'], self['publish_time'], self['job_advantage'], self['job_desc'], self['job_address'], self['company_url'],
                  self['company_name'], id, self['crawl_time'], self['crawl_update_time'], self['tags'])

        return insert_sql, params

    # 保存到elasticsearch
    def save_to_es(self):
        lagou = Lagou(meta={'id': extract_num(self["url"])})
        lagou.title = self['title']
        lagou.url = self['url']
        lagou.url_object_id = self['url_object_id']
        lagou.salary = self['salary']
        lagou.job_city = self['job_city']
        lagou.work_years = self['work_years']
        lagou.degree_need = self['degree_need']
        lagou.job_type = self['job_type']
        lagou.publish_time = self['publish_time']
        lagou.job_advantage = self['job_advantage']
        lagou.job_desc = self['job_desc']
        lagou.job_address = self['job_address']
        lagou.company_url = self['company_url']
        lagou.company_name = self['company_name']
        lagou.crawl_time = self['crawl_time']
        lagou.crawl_update_time = self['crawl_update_time']
        lagou.tags = self['tags']
        lagou.suggest = gen_suggests(Lagou._index._name, ((lagou.title, 10), (lagou.job_desc, 7)))
        lagou.save()
        return





