# -*- coding: utf-8 -*-
import re
from urllib import parse

import scrapy
from Spider.items import QuestionItem
from Spider.pipelines import QuestionPipeline
from Spider.utils.common import get_md5
import datetime


class SegmentfaultSpider(scrapy.Spider):
    name = 'segmentfault'
    allowed_domains = ['segmentfault.com', 'cdn.segmentfault.com']
    start_urls = ['https://segmentfault.com/questions/']

    def parse(self, response):
        question_list = response.xpath('//div[@class="stream-list question-stream"]/section')
        for question in question_list:
            question_url = question.xpath('./div[@class="summary"]/h2/a/@href').extract_first("")
            if question_url:
                yield scrapy.Request(url=parse.urljoin("https://segmentfault.com", question_url), callback=self.parse_question)
        next_link = response.xpath("//li[@class='next']//a/@href").extract_first()
        if(next_link):
            # yield scrapy.Request(url=parse.urljoin("https://segmentfault.com", next_link), callback=self.parse)
            pass

    def parse_question(self, response):
        question_item = QuestionItem()
        question_item['title'] = response.xpath("//a[@class='text-body']/text()").extract_first()
        question_item['content'] = response.xpath("//article[@class='article fmt article-content']/p/text()").extract_first()
        tags = response.xpath("//div[@class='m-n1']/a/text()").extract()
        new_tags = []
        for tag in tags:
            tag = re.sub('[(\n)+ +]', '', tag)
            if tag:
                new_tags.append(tag)
        question_item['tags'] = new_tags
        read_num = response.xpath("//div[@class='text-secondary font-size-14 mb-3 d-flex justify-content-between']/text()").extract_first()
        question_item['read_num'] = re.sub('[^0-9]', '', read_num)
        question_item['avatar'] = response.xpath("//picture[@class='mr-2']//img[contains(@class,'d-inline-block rounded-circle')]/@src").extract()
        question_item['url'] = response.url
        question_item['url_object_id'] = get_md5(response.url)
        yield question_item

