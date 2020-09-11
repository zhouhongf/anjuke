# -*- coding: utf-8 -*-
from scrapy.spiders import Spider
from scrapy_splash import SplashRequest
from anjuke.items import CommunityPriceItem
import re
import time
import codecs
import json


lua_script = '''
function IsEvenNumber(num)
    local num1, num2 = math.modf(num/2)
    if(num2==0)then
        return true
    else
        return false
    end
end

function main(splash, args)
    assert(splash:go(args.url))
    the_num = math.random(1, 10)
    assert(splash:wait(the_num))

    local num_result = IsEvenNumber(the_num)
    if(num_result)then
        splash.scroll_position = {x=0, y=the_num*100}
    end

    return {
        html = splash:html(),
        png = splash:png(),
        har = splash:har(),
    }
end'''


class CommunitypricemoreSpider(Spider):
    name = 'CommunityPriceMore'
    allowed_domains = ['anjuke.com']

    # 从txt文件中读取链接
    # start_urls = set()
    # file = open('citylinks_last_page.txt')
    # links = file.readlines()
    # for link in links:
    #    temp_link = link[:-1]
    #    result = re.match('(.*)p50/', temp_link)
    #    if result is not None:
    #        start_urls.add(result.group(1))
    # file.close()

    # def start_requests(self):
    #    for url in self.start_urls:
    #        for num in range(51, 101):
    #            link = url + 'p' + str(num) + '/'
    #            yield SplashRequest(link, self.parse, endpoint='execute', cache_args=['lua_source'], args={'lua_source': lua_script})

    # 从json文件中读取链接
    def start_requests(self):
        with codecs.open('citylinks_last_page.json', encoding='utf-8') as file:
            strings = file.read()
            data = json.loads(strings)
            for d in data:
                city = d.get('city')
                url = d.get('link')
                if city and url is not None:
                    for num in range(51, 101):
                        link = url + 'p' + str(num) + '/'
                        yield SplashRequest(link, self.parse, endpoint='execute', cache_args=['lua_source'], args={'lua_source': lua_script}, meta={'city': city})

    def parse(self, response):
        city = response.meta['city']
        communities = response.css('.li-itemmod')
        if len(communities) > 0:
            # city = response.xpath('.list-content em:first-child::text').extract_first()
            # city = response.xpath('//div[@class="list-content"]/div[@class="sortby"]/span/em/text()').extract_first()
            for comm in communities:
                item = CommunityPriceItem()
                item['name'] = comm.css('.li-info a:first-child::text').extract_first()
                item['city'] = city

                full_address = comm.css('.li-info address::text').extract_first().strip()
                the_area_first = re.findall(r'［\w*-\w*］', full_address)
                the_area_second = re.findall(r'［\w*］', full_address)
                if len(the_area_first) > 0:
                    thelist = the_area_first[0][1:-1].split('-')
                    item['county'] = thelist[0]
                    item['area'] = thelist[1]
                    thelength = len(the_area_first[0])
                    item['address'] = full_address[thelength:]
                    item['name_location'] = item['name'] + '+' + item['city'] + '+' + item['county'] + '+' + item[ 'area']
                elif len(the_area_second) > 0:
                    item['county'] = the_area_second[0][1:-1]
                    item['area'] = ' '
                    thelength = len(the_area_second[0])
                    item['address'] = full_address[thelength:]
                    item['name_location'] = item['name'] + '+' + item['city'] + '+' + item['county']
                else:
                    item['county'] = ' '
                    item['area'] = ' '
                    item['address'] = full_address
                    item['name_location'] = item['name'] + '+' + item['city']

                item['build_time'] = comm.css('.li-info p.date::text').extract_first().strip()
                item['data_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                item['source'] = '安居客'
                item['month'] = 10
                item['year'] = time.strftime('%Y')

                # item['price'] = comm.xpath('.//div[@class="li-side"]/p/strong/text()').extract_first()
                temp_price_one = comm.css('.li-side p strong::text').extract_first()
                temp_price_two = comm.css('.li-side p::text').extract_first()
                if temp_price_one is not None:
                    item['price'] = temp_price_one.strip()
                elif temp_price_two is not None:
                    item['price'] = temp_price_two.strip()
                else:
                    item['price'] = '暂无数据'

                item['name_location'] = item['name'] + '+' + item['city'] + '+' + item['county'] + '+' + item['area']
                yield item
