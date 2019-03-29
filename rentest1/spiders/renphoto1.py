#-*- coding: utf-8 -*-
import scrapy
import json
#from scrapy.spiders import CrawlSpider,Rule
#from scrapy.linkextractors import LinkExtractor
from scrapy.http import Request, FormRequest
from rentest1.items import Rentest1Item
import requests
import re
import math


class RenrenSpider(scrapy.Spider):

    name = 'renphoto001'
    allowed_domains = ['renren.com']

    # start_urls = ['http://follow.renren.com/list/965740621/pub/v7']
    # todo_urls =
    # seen_urls =
    # rules = (
    # Rule(LinkExtractor(allow = ('http://follow.renren.com/list/\d{9}/pub/v7')),callback='parse_urls',follow=True))

    def start_requests(self):
        """发送请求，回调登录"""
        return [Request('http://www.renren.com/SysHome.do', callback=self.post_login, dont_filter=True)]

    def post_login(self, response):
        """提交登录表单"""
        print('OK1')
        return [FormRequest.from_response(
            response, formdata={
                'email': 'XX',
                # 'icode':'',
                # 'origURL':'http://www.renren.com/home',
                # 'domain':'renren.com',
                # 'key_id':'1',
                # 'captcha_type':'web_login',
                'password': 'XX',
                # 'rkey':'XX',
                # 'f':'http%3A%2F%2Fzhibo.renren.com%2Ftop',
            },
            # meta = {'cookiejar':1},
            callback=self.parse_user_id,
            dont_filter=True
        )
        ]

    def parse_user_id(self, response):
        """从 id.txt 中读取id, 发送相册请求页面"""

        user_id = self.read_id()

        # 暂时以 此错误作为终止条件
        if not user_id:
            raise ZeroDivisionError

        # 总共 3W 个ID
        for i in range(5000):
            user_id = user_id + 1
            url = 'http://photo.renren.com/photo/' + '%s' % str(user_id) + '/albumlist/v7'
            yield Request(url,
                          meta={
                              # 'cookiejar':response.meta['cookiejar'],
                              'user_id': user_id
                          },
                          callback=self.parse_album_urls,
                          # dont_filter=True
                          )

    '''
    def parse_user_ids(self,response):
      
        yield Request("http://photo.renren.com/photo/500999244/albumlist/v7?offset=0&limit=40#",
            meta = {'cookiejar':response.meta['cookiejar'],'user_id':'500999244'},
            callback=self.parse_album_urls,
            dont_filter=True)
    '''

    def parse_album_urls(self, response):
        """解析相册"""
        album_pages = response.xpath('/*').re(r'"albumId":"\d{9}"')
        album_numbers = response.xpath('/*').re(r'"photoCount":\d+')
        if not album_pages:
            return

        album_ids = []
        for album_page in album_pages:
            album_id = album_page[11:20]
            album_ids.append(album_id)

        album_counts = []
        for album_number in album_numbers:
            album_count = album_number[13:]
            album_counts.append(album_count)

        album_urls=[]
        json_urls=[]
        for i in range(0, len(album_ids)):
            # math.ceil() 返回 向上取整的 int
            # x 是页码
            for x in range(1, math.ceil(int(album_counts[i])/20)+1):
                # http://photo.renren.com/photo/500999244/album-848184418/bypage/ajax/v7?page=3&pageSize=20
                url = 'http://photo.renren.com/photo/' + str(response.meta['user_id']) + '/album-' + str(album_ids[i])\
                      + '/bypage/ajax/v7?page=%d&pageSize=20' % x

                yield Request(url,
                              meta={
                                  # 'cookiejar':response.meta['cookiejar'],
                                  'user_id': response.meta['user_id'],
                                  'album_id':album_ids[i]
                              },
                              callback=self.save_item,
                              # dont_filter = True
                              )

    def save_item(self, response):
        print(response.status)

        # 如果 重定向 回调登录
        if response.status == 302:
            yield Request('http://www.renren.com/SysHome.do', callback=self.post_login, dont_filter=True)
        js = json.loads(response.body_as_unicode())
        for j in js['photoList']:
            item = Rentest1Item()
            item['user_id'] = response.meta['user_id']
            item['album_id'] = response.meta['album_id']
            item['url'] = j['url']
            name = j['url'].replace('/', '_')
            item['name'] = name

            # ImagesPiplines
            item['image_urls'] = [item['url']]

            print(item)
            yield item

    @staticmethod
    def read_id():

        file_name = 'id.txt'

        # 读取 ID
        with open(file_name, 'r', encoding='utf-8') as f:
            id_list = f.readlines()
            user_id = int(id_list[0])

        # 前移，相当于删除了第一个 ID
        with open(file_name, 'w', encoding='utf-8') as f:
            for temp in id_list[1:]:
                f.write(temp)

        return user_id
