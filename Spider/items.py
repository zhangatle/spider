# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
import datetime

import scrapy
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