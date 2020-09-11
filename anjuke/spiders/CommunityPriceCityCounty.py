# -*- coding: utf-8 -*-
from scrapy.spiders import Spider
from scrapy_splash import SplashRequest
from anjuke.items import CommunityPriceItem, NameLinkItem
import re
import time
import json
import codecs
import random


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
    the_num = math.random(1, 10)
    assert(splash:wait(the_num))

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


class CommunitypricecitycountySpider(Spider):
    name = 'CommunityPriceCityCounty'
    allowed_domains = ['anjuke.com']
    start_urls = []
    file = open('citylinks1.txt')
    links = file.readlines()
    for link in links:
        link_need = link[:-1]
        start_urls.append(link_need)
    file.close()


    def start_requests(self):
        for url in self.start_urls:
            wait_time = random.randint(0, 10)
            time.sleep(wait_time)
            yield SplashRequest(url, self.parse_county, endpoint='execute', cache_args=['lua_source'], args={'lua_source': lua_script})

    def parse_county(self, response):
        city = response.css('.list-content em:first-child::text').extract_first()
        # city = response.xpath('//div[@class="li-info"]/div[@class="sortby"]/span/em/text()').extract_first()
        # counties = response.css('.elems-l' and '.pp-mod')[0] 该表达式不太准确，因为有的项目只有elems-l, 没有pp-mod
        counties = response.xpath('//span[contains(@class, "elems-l")]')[0]
        a_object = counties.css('a')
        for a in a_object:
            county_link = a.css('a::attr(href)').extract_first()
            result = re.match('.*community/.+', county_link)
            if result is not None:
                url = result.group(0)
                yield SplashRequest(url, self.parse_area, endpoint='execute', cache_args=['lua_source'], args={'lua_source': lua_script}, meta={'city': city})

    def parse_area(self, response):
        city = response.meta['city']
        areas = response.xpath('//span[contains(@class, "elems-l")]')[0]
        a_object = areas.css('div.sub-items a')
        for a in a_object:
            area_link = a.css('a::attr(href)').extract_first()
            result = re.match('.*community/.+', area_link)
            if result is not None:
                url = result.group(0)
                yield SplashRequest(url, self.parse, endpoint='execute', cache_args=['lua_source'], args={'lua_source': lua_script}, meta={'city': city})

    def parse(self, response):
        city = response.meta['city']
        communities = response.css('.li-itemmod')
        if len(communities) > 0:
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

            next_page = response.css('.multi-page a:last-child::attr(href)').extract_first()
            if next_page is not None:
                # yield response.follow(next_page, callback=self.parse)
                the_page = response.urljoin(next_page)
                yield SplashRequest(the_page, self.parse, endpoint='execute', cache_args=['lua_source'], args={'lua_source': lua_script}, meta={'city': city})

            else:
                # last_page_num = response.css('.multi-page i.curr::text').extract_first()
                # last_page = response.url + '\n'
                # with open('citylinks_last_page.txt', 'a') as f:
                #    f.writelines(last_page)

                # 直接储存在json文件中
                # last_page = response.url
                # data = {'city': city, 'link': last_page}
                # with codecs.open('citylinks_last_page.json', 'a', encoding='utf-8') as f:
                #     f.write(json.dumps(data, indent=2, ensure_ascii=False) + "\n")

                # 通过NamePriceItem使用UniversalPipeline储存在json文件中
                last_page = response.url
                item = NameLinkItem()
                item['name'] = city
                item['link'] = last_page
                yield item
