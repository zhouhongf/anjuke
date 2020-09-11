# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class CommunityPriceItem(Item):
    table = 'house_anjuke'
    name = Field()
    city = Field()
    county = Field()
    area = Field()
    address = Field()
    build_time = Field()
    price = Field()
    data_time = Field()
    name_location = Field()
    source = Field()
    month = Field()
    year = Field()


class NameLinkItem(Item):
    name = Field()
    link = Field()

