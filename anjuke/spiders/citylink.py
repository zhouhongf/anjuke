# -*- coding: utf-8 -*-
from scrapy.spiders import Spider
from scrapy_splash import SplashRequest
import json


class CitylinkSpider(Spider):
    name = 'citylink'
    allowed_domains = ['anjuke.com']
    start_urls = ['https://www.anjuke.com/sy-city.html']

    #def start_requests(self):
    #    for url in self.start_urls:
    #        yield SplashRequest(url, self.parse, args={'wait': '2'})

    #def parse(self, response):
    #    links = set()
    #    cities = response.css('.city_list a::attr(href)').extract()
    #    for city in cities:
    #        link = city + '/community/' + '\n'
    #        links.add(link)
    #    with open('citylinks.txt', 'w') as f:
    #        f.writelines(links)

    # 保存为json文件
    # def parse(self, response):
    #    cities = response.css('.city_list a')
    #    data = []
    #    for city in cities:
    #        name = city.css('a::text').extract_first()
    #        temp_link = city.css('a::attr(href)').extract_first()
    #        link = temp_link + '/community/'
    #        data.append({'name': name, 'link': link})
    #    with open('citylinks.json', 'a') as f:
    #        f.write(json.dumps(data, indent=2, ensure_ascii=False))

    # 保存为json文件 含首字母
    #def parse(self, response):
    #    theitems = response.css('.letter_city li')
    #    data = []
    #    for theitem in theitems:
    #        letter = theitem.css('label.label_letter::text').extract_first()
    #        cities = theitem.css('.city_list a')
    #        for city in cities:
    #            name = city.css('a::text').extract_first()
    #            temp_link = city.css('a::attr(href)').extract_first()
    #            link = temp_link + '/community/'
    #            data.append({'name': name, 'link': link, 'letter': letter})
    #    with open('citylinks.json', 'a') as f:
    #        f.write(json.dumps(data, indent=2, ensure_ascii=False))

    # 保存为json文件，仅含名称和首字母
    def parse(self, response):
        theitems = response.css('.letter_city li')
        data = []
        for theitem in theitems:
            letter = theitem.css('label.label_letter::text').extract_first()
            cities = theitem.css('.city_list a')
            for city in cities:
                name = city.css('a::text').extract_first()
                data.append({'name': name, 'letter': letter})
        with open('citylinks.json', 'a') as f:
            f.write(json.dumps(data, indent=2, ensure_ascii=False))
