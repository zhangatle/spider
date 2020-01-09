# -*- coding: utf-8 -*-
import base64
import datetime
import hashlib
import hmac
import json
import os
import re
import time
from urllib import parse
from urllib.parse import urlencode
from scrapy.loader import ItemLoader
from Spider.items import ZhihuQuestionItem, ZhihuAnswerItem

import execjs
import scrapy
from scrapy.http.cookies import CookieJar

from Spider.utils.utils import saveImage, showImage, removeImage


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['zhihu.com']
    start_urls = ['http://zhihu.com/']

    _xsrf = ''
    captcha = ''
    cur_path = os.getcwd()
    cookie_jar = CookieJar()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
        'Referer': 'https://www.zhihu.com/',
        'Host': 'www.zhihu.com',
    }
    start_answer_url = "https://www.zhihu.com/api/v4/questions/{0}/answers?include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cis_labeled%2Cis_recognized%2Cpaid_info%2Cpaid_info_content%3Bdata%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cbadge%5B%2A%5D.topics&limit={1}&offset={2}&platform=desktop&sort_by=default"
    captcha_url = 'https://www.zhihu.com/api/v3/oauth/captcha?lang=en'
    homepage_url = 'https://www.zhihu.com/'
    login_url = 'https://www.zhihu.com/api/v3/oauth/sign_in'

    '''js code'''
    encrypt_js_code = '''
    // I borrowed the codes from https://github.com/zkqiang/zhihu-login/blob/master/encrypt.js
    function s(e) {
      return (s = "function" == typeof Symbol && "symbol" == typeof Symbol.t ? function(e) {
          return typeof e
      }
      : function(e) {
          return e && "function" == typeof Symbol && e.constructor === Symbol && e !== Symbol.prototype ? "symbol" : typeof e
      }
      )(e)
    }
    function i() {}
    function h(e) {
      this.s = (2048 & e) >> 11,
      this.i = (1536 & e) >> 9,
      this.h = 511 & e,
      this.A = 511 & e
    }
    function A(e) {
      this.i = (3072 & e) >> 10,
      this.A = 1023 & e
    }
    function n(e) {
      this.n = (3072 & e) >> 10,
      this.e = (768 & e) >> 8,
      this.a = (192 & e) >> 6,
      this.s = 63 & e
    }
    function e(e) {
      this.i = e >> 10 & 3,
      this.h = 1023 & e
    }
    function a() {}
    function c(e) {
      this.n = (3072 & e) >> 10,
      this.e = (768 & e) >> 8,
      this.a = (192 & e) >> 6,
      this.s = 63 & e
    }
    function o(e) {
      this.A = (4095 & e) >> 2,
      this.s = 3 & e
    }
    function r(e) {
      this.i = e >> 10 & 3,
      this.h = e >> 2 & 255,
      this.s = 3 & e
    }
    function k(e) {
      this.s = (4095 & e) >> 10,
      this.i = (1023 & e) >> 8,
      this.h = 1023 & e,
      this.A = 63 & e
    }
    function B(e) {
      this.s = (4095 & e) >> 10,
      this.n = (1023 & e) >> 8,
      this.e = (255 & e) >> 6
    }
    function f(e) {
      this.i = (3072 & e) >> 10,
      this.A = 1023 & e
    }
    function u(e) {
      this.A = 4095 & e
    }
    function C(e) {
      this.i = (3072 & e) >> 10
    }
    function b(e) {
      this.A = 4095 & e
    }
    function g(e) {
      this.s = (3840 & e) >> 8,
      this.i = (192 & e) >> 6,
      this.h = 63 & e
    }
    function G() {
      this.c = [0, 0, 0, 0],
      this.o = 0,
      this.r = [],
      this.k = [],
      this.B = [],
      this.f = [],
      this.u = [],
      this.C = !1,
      this.b = [],
      this.g = [],
      this.G = !1,
      this.Q = null,
      this.R = null,
      this.w = [],
      this.x = 0,
      this.D = {
          0: i,
          1: h,
          2: A,
          3: n,
          4: e,
          5: a,
          6: c,
          7: o,
          8: r,
          9: k,
          10: B,
          11: f,
          12: u,
          13: C,
          14: b,
          15: g
      }
    }
    Object.defineProperty(exports, "__esModule", {
      value: !0
    });
    var t = "1.1"
    , __g = {};
    i.prototype.M = function(e) {
      e.G = !1
    }
    ,
    h.prototype.M = function(e) {
      switch (this.s) {
      case 0:
          e.c[this.i] = this.h;
          break;
      case 1:
          e.c[this.i] = e.k[this.A]
      }
    }
    ,
    A.prototype.M = function(e) {
      e.k[this.A] = e.c[this.i]
    }
    ,
    n.prototype.M = function(e) {
      switch (this.s) {
      case 0:
          e.c[this.n] = e.c[this.e] + e.c[this.a];
          break;
      case 1:
          e.c[this.n] = e.c[this.e] - e.c[this.a];
          break;
      case 2:
          e.c[this.n] = e.c[this.e] * e.c[this.a];
          break;
      case 3:
          e.c[this.n] = e.c[this.e] / e.c[this.a];
          break;
      case 4:
          e.c[this.n] = e.c[this.e] % e.c[this.a];
          break;
      case 5:
          e.c[this.n] = e.c[this.e] == e.c[this.a];
          break;
      case 6:
          e.c[this.n] = e.c[this.e] >= e.c[this.a];
          break;
      case 7:
          e.c[this.n] = e.c[this.e] || e.c[this.a];
          break;
      case 8:
          e.c[this.n] = e.c[this.e] && e.c[this.a];
          break;
      case 9:
          e.c[this.n] = e.c[this.e] !== e.c[this.a];
          break;
      case 10:
          e.c[this.n] = s(e.c[this.e]);
          break;
      case 11:
          e.c[this.n] = e.c[this.e]in e.c[this.a];
          break;
      case 12:
          e.c[this.n] = e.c[this.e] > e.c[this.a];
          break;
      case 13:
          e.c[this.n] = -e.c[this.e];
          break;
      case 14:
          e.c[this.n] = e.c[this.e] < e.c[this.a];
          break;
      case 15:
          e.c[this.n] = e.c[this.e] & e.c[this.a];
          break;
      case 16:
          e.c[this.n] = e.c[this.e] ^ e.c[this.a];
          break;
      case 17:
          e.c[this.n] = e.c[this.e] << e.c[this.a];
          break;
      case 18:
          e.c[this.n] = e.c[this.e] >>> e.c[this.a];
          break;
      case 19:
          e.c[this.n] = e.c[this.e] | e.c[this.a]
      }
    }
    ,
    e.prototype.M = function(e) {
      e.r.push(e.o),
      e.B.push(e.k),
      e.o = e.c[this.i],
      e.k = [];
      for (var t = 0; t < this.h; t++)
          e.k.unshift(e.f.pop());
      e.u.push(e.f),
      e.f = []
    }
    ,
    a.prototype.M = function(e) {
      e.o = e.r.pop(),
      e.k = e.B.pop(),
      e.f = e.u.pop()
    }
    ,
    c.prototype.M = function(e) {
      switch (this.s) {
      case 0:
          e.C = e.c[this.n] >= e.c[this.e];
          break;
      case 1:
          e.C = e.c[this.n] <= e.c[this.e];
          break;
      case 2:
          e.C = e.c[this.n] > e.c[this.e];
          break;
      case 3:
          e.C = e.c[this.n] < e.c[this.e];
          break;
      case 4:
          e.C = e.c[this.n] == e.c[this.e];
          break;
      case 5:
          e.C = e.c[this.n] != e.c[this.e];
          break;
      case 6:
          e.C = e.c[this.n];
          break;
      case 7:
          e.C = !e.c[this.n]
      }
    }
    ,
    o.prototype.M = function(e) {
      switch (this.s) {
      case 0:
          e.o = this.A;
          break;
      case 1:
          e.C && (e.o = this.A);
          break;
      case 2:
          e.C || (e.o = this.A);
          break;
      case 3:
          e.o = this.A,
          e.Q = null
      }
      e.C = !1
    }
    ,
    r.prototype.M = function(e) {
      switch (this.s) {
      case 0:
          for (var t = [], n = 0; n < this.h; n++)
              t.unshift(e.f.pop());
          e.c[3] = e.c[this.i](t[0], t[1]);
          break;
      case 1:
          for (var r = e.f.pop(), o = [], i = 0; i < this.h; i++)
              o.unshift(e.f.pop());
          e.c[3] = e.c[this.i][r](o[0], o[1]);
          break;
      case 2:
          for (var a = [], c = 0; c < this.h; c++)
              a.unshift(e.f.pop());
          e.c[3] = new e.c[this.i](a[0],a[1])
      }
    }
    ,
    k.prototype.M = function(e) {
      switch (this.s) {
      case 0:
          e.f.push(e.c[this.i]);
          break;
      case 1:
          e.f.push(this.h);
          break;
      case 2:
          e.f.push(e.k[this.A]);
          break;
      case 3:
          e.f.push(e.g[this.A])
      }
    }
    ,
    B.prototype.M = function(t) {
      switch (this.s) {
      case 0:
          var s = t.f.pop();
          t.c[this.n] = t.c[this.e][s];
          break;
      case 1:
          var i = t.f.pop()
            , h = t.f.pop();
          t.c[this.e][i] = h;
          break;
      case 2:
          var A = t.f.pop();
          if(A === 'window') {
              A = {
                  encodeURIComponent: function (url) {
                      return encodeURIComponent(url)
                  }
              }
          } else if (A === 'navigator') {
              A = {
                  'userAgent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ' +
                      '(KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'
              }
          }
          t.c[this.n] = eval(A)
      }
    }
    ,
    f.prototype.M = function(e) {
      e.c[this.i] = e.g[this.A]
    }
    ,
    u.prototype.M = function(e) {
      e.Q = this.A
    }
    ,
    C.prototype.M = function(e) {
      throw e.c[this.i]
    }
    ,
    b.prototype.M = function(e) {
      var t = this
        , n = [0];
      e.k.forEach(function(e) {
          n.push(e)
      });
      var r = function(r) {
          var o = new G;
          return o.k = n,
          o.k[0] = r,
          o.J(e.b, t.A, e.g, e.w),
          o.c[3]
      };
      r.toString = function() {
          return "() { [native code] }"
      }
      ,
      e.c[3] = r
    }
    ,
    g.prototype.M = function(e) {
      switch (this.s) {
      case 0:
          for (var t = {}, n = 0; n < this.h; n++) {
              var r = e.f.pop();
              t[e.f.pop()] = r
          }
          e.c[this.i] = t;
          break;
      case 1:
          for (var o = [], i = 0; i < this.h; i++)
              o.unshift(e.f.pop());
          e.c[this.i] = o
      }
    }
    ,
    G.prototype.v = function(e) {
      for (var t = Buffer.from(e, 'base64').toString('binary'), n = [], r = 0; r < t.length - 1; r += 2)
          n.push(t.charCodeAt(r) << 8 | t.charCodeAt(r + 1));
      this.b = n
    }
    ,
    G.prototype.y = function(e) {
      for (var t = Buffer.from(e, 'base64').toString('binary'), n = 66, r = [], o = 0; o < t.length; o++) {
          var i = 24 ^ t.charCodeAt(o) ^ n;
          r.push(String.fromCharCode(i)),
          n = i
      }
      return r.join("")
    }
    ,
    G.prototype.F = function(e) {
      var t = this;
      this.g = e.map(function(e) {
          return "string" == typeof e ? t.y(e) : e
      })
    }
    ,
    G.prototype.J = function(e, t, n) {
      for (t = t || 0,
      n = n || [],
      this.o = t,
      "string" == typeof e ? (this.F(n),
      this.v(e)) : (this.b = e,
      this.g = n),
      this.G = !0,
      this.x = Date.now(); this.G; ) {
          var r = this.b[this.o++];
          if ("number" != typeof r)
              break;
          var o = Date.now();
          if (500 < o - this.x)
              return;
          this.x = o;
          try {
              this.M(r)
          } catch (e) {
              if (this.R = e,
              !this.Q)
                  throw "execption at " + this.o + ": " + e;
              this.o = this.Q
          }
      }
    }
    ,
    G.prototype.M = function(e) {
      var t = (61440 & e) >> 12;
      new this.D[t](e).M(this)
    }
    ,
    (new G).J("4AeTAJwAqACcAaQAAAAYAJAAnAKoAJwDgAWTACwAnAKoACACGAESOTRHkQAkAbAEIAMYAJwFoAASAzREJAQYBBIBNEVkBnCiGAC0BjRAJAAYBBICNEVkBnDGGAC0BzRAJACwCJAAnAmoAJwKoACcC4ABnAyMBRAAMwZgBnESsA0aADRAkQAkABgCnA6gABoCnA+hQDRHGAKcEKAAMQdgBnFasBEaADRAkQAkABgCnBKgABoCnBOhQDRHZAZxkrAUGgA0QJEAJAAYApwVoABgBnG6sBYaADRAkQAkABgCnBegAGAGceKwGBoANECRACQAnAmoAJwZoABgBnIOsBoaADRAkQAkABgCnBugABoCnByhQDRHZAZyRrAdGgA0QJEAJAAQACAFsB4gBhgAnAWgABIBNEEkBxgHEgA0RmQGdJoQCBoFFAE5gCgFFAQ5hDSCJAgYB5AAGACcH4AFGAEaCDRSEP8xDzMQIAkQCBoFFAE5gCgFFAQ5hDSCkQAkCBgBGgg0UhD/MQ+QACAIGAkaBxQBOYGSABoAnB+EBRoIN1AUCDmRNJMkCRAIGgUUATmAKAUUBDmENIKRACQIGAEaCDRSEP8xD5AAIAgYCRoHFAI5gZIAGgCcH4QFGgg3UBQQOZE0kyQJGAMaCRQ/OY+SABoGnCCEBTTAJAMYAxoJFAY5khI/Nk+RABoGnCCEBTTAJAMYAxoJFAw5khI/Nk+RABoGnCCEBTTAJAMYAxoJFBI5khI/Nk+RABoGnCCEBTTAJAMYBxIDNEEkB3JsHgNQAA==", 0, ["BRgg", "BSITFQkTERw=", "LQYfEhMA", "PxMVFBMZKB8DEjQaBQcZExMC", "", "NhETEQsE", "Whg=", "Wg==", "MhUcHRARDhg=", "NBcPBxYeDQMF", "Lx4ODys+GhMC", "LgM7OwAKDyk6Cg4=", "Mx8SGQUvMQ==", "SA==", "ORoVGCQgERcCAxo=", "BTcAERcCAxo=", "BRg3ABEXAgMaFAo=", "SQ==", "OA8LGBsP", "GC8LGBsP", "Tg==", "PxAcBQ==", "Tw==", "KRsJDgE=", "TA==", "LQofHg4DBwsP", "TQ==", "PhMaNCwZAxoUDQUeGQ==", "PhMaNCwZAxoUDQUeGTU0GQIeBRsYEQ8=", "Qg==", "BWpUGxkfGRsZFxkbGR8ZGxkHGRsZHxkbGRcZG1MbGR8ZGxkXGRFpGxkfGRsZFxkbGR8ZGxkHGRsZHxkbGRcZGw==", "ORMRCyk0Exk8LQ==", "ORMRCyst"]);
    var Q = function(e) {
      return __g._encrypt(e)
    };
    '''

    # 解析主页
    def parse(self, response):
        all_urls = response.css("a::attr(href)").extract()
        all_urls = [parse.urljoin(response.url, url) for url in all_urls]
        all_urls = filter(lambda x: True if x.startswith('https') else False, all_urls)
        for url in all_urls:
            match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$).*", url)
            if match_obj:
                request_url = match_obj.group(1)
                yield scrapy.Request(request_url, headers=self.headers, meta={'cookiejar': response.meta['cookiejar']}, callback=self.parse_question)
            else:
                yield scrapy.Request(url, headers=self.headers, meta={'cookiejar': response.meta['cookiejar']}, callback=self.parse)

    def parse_question(self, response):
        match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$).*", response.url)
        if match_obj:
            question_id = int(match_obj.group(2))
            item_loader = ItemLoader(item=ZhihuQuestionItem(), response=response)
            item_loader.add_css("title", "h1.QuestionHeader-title::text")
            item_loader.add_css("content", ".QuestionHeader-detail")
            item_loader.add_value('url', response.url)
            item_loader.add_value("id", question_id)
            item_loader.add_css('answer_num', ".List-headerText span::text")
            item_loader.add_css('comments_num', ".QuestionHeader-Comment button::text")
            item_loader.add_css('follow_num', ".NumberBoard-itemValue::text")
            item_loader.add_css('topics', ".QuestionHeader-topics .Popover div::text")
            question_item = item_loader.load_item()
            yield scrapy.Request(self.start_answer_url.format(question_id, 20, 0), meta={'cookiejar': response.meta['cookiejar']}, headers=self.headers, callback=self.parse_answer)
            yield question_item

    def parse_answer(self, response):
        answer_json = json.loads(response.text)
        is_end = answer_json['paging']['is_end']
        next_url = answer_json['paging']['next']

        for answer in answer_json['data']:
            answer_item = ZhihuAnswerItem()
            answer_item['id'] = answer['id']
            answer_item['url'] = answer['url']
            answer_item['question_id'] = answer['question']['id']
            answer_item['author_id'] = answer['author']['id'] if 'id' in answer['author'] else None
            answer_item['content'] = answer['content'] if 'content' in answer else None
            answer_item['approve_num'] = answer['voteup_count']
            answer_item['comments_num'] = answer['comment_count']
            answer_item['create_time'] = answer['created_time']
            answer_item['update_time'] = answer['updated_time']
            answer_item['crawl_time'] = datetime.datetime.now()
            yield answer_item

        if not is_end:
            yield scrapy.Request(next_url, meta={'cookiejar': response.meta['cookiejar']}, headers=self.headers, callback=self.parse_answer)

    # 首先获取验证码
    def start_requests(self):
        return [scrapy.Request(self.captcha_url, meta={'cookiejar': self.cookie_jar}, headers=self.headers, callback=self.is_captcha)]

    # 检查是否需要验证码
    def is_captcha(self, response):
        cookies = response.headers.getlist('Set-Cookie')
        for cookie in cookies:
            cookie = cookie.decode("utf-8")
            m = re.match(r"^_xsrf=(.*?);", cookie)
            if m is not None:
                self._xsrf = m.group(1)
        if 'true' in response.text:
            return scrapy.Request(self.captcha_url, meta={'cookiejar': response.meta['cookiejar']}, headers=self.headers, callback=self.get_captcha, method='PUT')

    # 获取验证码
    def get_captcha(self, response):
        img_base64 = json.loads(response.text)['img_base64'].replace('\\n', '')
        saveImage(base64.b64decode(img_base64), os.path.join(self.cur_path, 'captcha.jpg'))
        showImage(os.path.join(self.cur_path, 'captcha.jpg'))
        self.captcha = input('请输入图形验证码:')
        return [scrapy.FormRequest(self.captcha_url, meta={'cookiejar': response.meta['cookiejar']}, headers=self.headers, formdata={'input_text': self.captcha},
                               callback=self.check_captcha)]

    def check_captcha(self, response):
        # 获取signature
        signature = hmac.new(b'd1b964811afb40118a12068ff74a12f4', digestmod=hashlib.sha1)
        grant_type = 'password'
        client_id = 'c3cef7c66a1843f8b3a9e6a1e3160e20'
        source = 'com.zhihu.web'
        timestamp = str(int(time.time() * 1000))
        signature.update(bytes((grant_type + client_id + source + timestamp), 'utf-8'))
        signature = signature.hexdigest()
        data = {
            'client_id': client_id,
            'grant_type': grant_type,
            'source': source,
            'username': '',
            'password': '',
            'lang': 'en',
            'ref_source': 'homepage',
            'utm_source': '',
            'captcha': self.captcha,
            'timestamp': timestamp,
            'signature': signature
        }
        js = execjs.compile(self.encrypt_js_code)
        data = js.call('Q', urlencode(data))
        self.headers.update(
            {'x-zse-83': '3_1.1', 'x-xsrftoken': self._xsrf, 'content-type': 'application/x-www-form-urlencoded'})
        return [scrapy.Request(self.login_url, meta={'cookiejar': response.meta['cookiejar']},  headers=self.headers,
                                   method='POST', body=data,
                                   callback=self.check_login)]

    def check_login(self, response):
        res = response.body.decode("utf-8")
        if 'user_id' in res:
            print('登录成功')
            removeImage(os.path.join(self.cur_path, 'captcha.jpg'))
            for url in self.start_urls:
                yield scrapy.Request(url, dont_filter=True, headers=self.headers, meta={'cookiejar': response.meta['cookiejar']})
        else:
            raise RuntimeError('登录出错')