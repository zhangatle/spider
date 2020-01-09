# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request


class IthomeSpider(scrapy.Spider):
    name = 'ithome'
    allowed_domains = ['ithome.com']
    start_urls = ['https://www.ithome.com/blog/']

    def parse_article(self, response):
        article = response.xpath('//div[@class="content fl"]')
        title = article.xpath('./div[@class="post_title"]/h1/text()').extract_first("")
        pubtime = article.xpath('.//span[@id="pubtime_baidu"]/text()').extract_first("")
        source = article.xpath('.//span[@id="source_baidu"]/a/text()').extract_first("")
        source_url = article.xpath('.//span[@id="source_baidu"]/a/@href').extract_first("")
        author = article.xpath('.//span[@id="author_baidu"]/strong/text()').extract_first("")
        editor = article.xpath('.//span[@id="editor_baidu"]/strong/text()').extract_first("")
        #commentcount = contents.xpath('.//span[@id="commentcount"]')
        content = article.xpath('.//div[@id="paragraph"]').extract_first("")
        print(title)

    def parse(self, response):
        article_list = response.xpath('//div[@class="cate_list"]//li')
        for article in article_list:
            article_url = article.xpath('./a/@href').extract_first()
            yield Request(article_url, self.parse_article)
        # 请求下一页


