# -*- coding: utf-8 -*-
import datetime

from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from items import LagouJobItemLoader, LagouJobItem
from utils.common import get_md5


class LagouSpider(CrawlSpider):
    name = 'lagou'
    allowed_domains = ['www.lagou.com']
    start_urls = ['https://www.lagou.com/']

    custom_settings = {
        "COOKIES_ENABLED": False,
        "DOWNLOAD_DELAY": 5,
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Connection': 'keep-alive',
            'Cookie': '_zap=06b43a3c-c746-4368-a222-ae5089c9c25b; d_c0="AJBldFHKnxCPTip9m6FbANB2XDHnKb8j97U=|1578381252"; capsion_ticket="2|1:0|10:1578388528|14:capsion_ticket|44:N2E2NzkyMzMwM2JkNGQ3MDlkY2ZjNTY1MTNiY2U0Mjk=|598db6ffd10f71709e577e8a0f54f28a1566f037c9f93b7ab9b34cb925615da8"; _xsrf=ffc6e768-92a0-44ed-b625-d1e4aafa4735; Hm_lvt_98beee57fd2ef70ccdd5ca52b9740c49=1578619947,1578620284,1578720575,1578721728; KLBRSID=ca494ee5d16b14b649673c122ff27291|1578721825|1578720575; Hm_lpvt_98beee57fd2ef70ccdd5ca52b9740c49=1578721826',
            'Host': 'www.lagou.com',
            'Origin': 'https://www.lagou.com',
            'Referer': 'https://www.lagou.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
        }
    }

    rules = (
        # Rule(LinkExtractor(allow=(r'zhaopin/.*',),)),
        # Rule(LinkExtractor(allow=(r'gongsi/.*',),)),
        Rule(LinkExtractor(allow=(r'jobs/\d+.html',),), callback='parse_job', follow=True),
    )

    def parse_job(self, response):
        item_loader = LagouJobItemLoader(item=LagouJobItem(), response=response)
        item_loader.add_css("title", ".job-name::attr(title)")
        item_loader.add_css("tags", ".job_request ul li::text")
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
