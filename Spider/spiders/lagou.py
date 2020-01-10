# -*- coding: utf-8 -*-
import datetime
import time

import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from items import LagouJobItemLoader, LagouJobItem
from utils.common import get_md5


class LagouSpider(CrawlSpider):
    name = 'lagou'
    allowed_domains = ['www.lagou.com']
    start_urls = ['https://www.lagou.com/']

    rules = (
        Rule(LinkExtractor(allow=(r'zhaopin/.*',),)),
        Rule(LinkExtractor(allow=(r'gongsi/.*',),)),
        Rule(LinkExtractor(allow=(r'jobs/\d+.html',),), callback='parse_job', follow=True),
    )

    def parse_job(self, response):
        item_loader = LagouJobItemLoader(item=LagouJobItem(), response=response)
        item_loader.add_css("title", ".job-name::attr(title)")
        item_loader.add_value("url", response.url)
        item_loader.add_value("url_object_id", get_md5(response.url))
        item_loader.add_css("salary", ".salary::text")
        item_loader.add_xpath("job_city", "//*[@class='job_request']/h3/span[2]/text()")
        item_loader.add_xpath("work_years", "//*[@class='job_request']/h3/span[3]/text()")
        item_loader.add_xpath("degree_need", "//*[@class='job_request']/h3/span[4]/text()")
        item_loader.add_xpath("job_type", "//*[@class='job_request']/h3/span[5]/text()")

        item_loader.add_css("publish_time", ".publish_time::text")
        item_loader.add_css("job_advantage", ".job-advantage p::text")
        item_loader.add_css("job_desc", ".job_bt div")
        item_loader.add_css("job_address", ".work_addr")
        item_loader.add_css("company_url", "#job_company dt a::attr(href)")
        item_loader.add_css("company_name", ".job_company_content em::text")

        item_loader.add_value("crawl_time", datetime.datetime.now())
        item_loader.add_value("crawl_update_time", datetime.datetime.now())
        job_item = item_loader.load_item()
        return job_item