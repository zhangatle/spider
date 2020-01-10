# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
import datetime

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst
from w3lib.html import remove_tags

from utils.common import extract_num
from settings import SQL_DATETIME_FORMAT, SQL_DATE_FORMAT


class QuestionItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    tags = scrapy.Field()
    read_num = scrapy.Field()
    avatar = scrapy.Field()
    avatar_path = scrapy.Field()
    url = scrapy.Field()
    url_object_id = scrapy.Field()


class ZhihuQuestionItem(scrapy.Item):
    id = scrapy.Field()
    topics = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    answer_num = scrapy.Field()
    comments_num = scrapy.Field()
    follow_num = scrapy.Field()
    view_num = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
            insert into zhihu_question(id, topics, url, title, content, answer_num, comments_num, follow_num, view_num, crawl_time) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            on duplicate key update content=values(content), answer_num=values(answer_num), comments_num=values(comments_num), follow_num=values(follow_num), view_num=values(view_num)
        """
        id = self['id'][0]
        topics = ",".join(self['topics'])
        url = self['url'][0]
        title = "".join(self['title'])
        content = "".join(self['content'])
        answer_num = extract_num("".join(self["answer_num"]))
        comments_num = extract_num("".join(self["comments_num"]))
        if len(self['follow_num']) == 2:
            follow_num = int(self['follow_num'][0].replace(",", ""))
            view_num = int(self['follow_num'][1].replace(",", ""))
        else:
            follow_num = int(self['follow_num'][0].replace(",", ""))
            view_num = 0
        crawl_time = datetime.datetime.now().strftime(SQL_DATETIME_FORMAT)

        params = (id, topics, url, title, content, answer_num, comments_num, follow_num, view_num, crawl_time)
        return insert_sql, params


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

    def get_insert_sql(self):
        insert_sql = """
            insert into zhihu_answer(id, url, question_id, author_id, content, approve_num, comments_num, create_time, update_time, crawl_time)
            values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            on duplicate key update content=values(content), comments_num=values(comments_num), approve_num=values(approve_num), update_time=values(update_time)
        """
        create_time = datetime.datetime.fromtimestamp(self["create_time"]).strftime(SQL_DATETIME_FORMAT)
        update_time = datetime.datetime.fromtimestamp(self["update_time"]).strftime(SQL_DATETIME_FORMAT)

        params = (
            self['id'], self['url'], self['question_id'], self['author_id'], self['content'], self['approve_num'], self['comments_num'], create_time, update_time, self['crawl_time'].strftime(SQL_DATETIME_FORMAT)
        )

        return insert_sql, params


def replace_splash(value):
    return value.replace("/", "")


def handle_strip(value):
    return value.strip()


def handle_jobaddr(value):
    addr_list = value.split("\n")
    addr_list = [item.strip() for item in addr_list if item.strip() != "查看地图"]
    return "".join(addr_list)


class LagouJobItemLoader(ItemLoader):
    default_output_processor = TakeFirst()


class LagouJobItem(scrapy.Item):
    title = scrapy.Field()
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

    def get_insert_sql(self):
        insert_sql = """
            insert into lagou_jobs(title, url, url_object_id, salary, job_city, work_years, degree_need, job_type, publish_time, job_advantage, job_desc, job_address, company_url, company_name, id, crawl_time, crawl_update_time)
            values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            on duplicate key update job_desc=values(job_desc)
        """

        id = extract_num(self["url"])
        params = (self['title'], self['url'], self['url_object_id'], self['salary'], self['job_city'], self['work_years'], self['degree_need'],
                  self['job_type'], self['publish_time'], self['job_advantage'], self['job_desc'], self['job_address'], self['company_url'],
                  self['company_name'], id, self['crawl_time'], self['crawl_update_time'])

        return insert_sql, params



