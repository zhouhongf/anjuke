# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import codecs
import json
import pymysql
import csv
from anjuke.items import CommunityPriceItem, NameLinkItem


class JsonPipeline(object):
    def __init__(self):
        self.file = codecs.open('communityprice.json', 'w', encoding='utf-8')

    def process_item(self, item, spider):
        line = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(line)
        return item

    def spider_closed(self, spider):
        self.file.close()


class CSVPipeline(object):
    def __init__(self):
        self.file = open('data.csv', 'a', newline='')
        fieldnames = ['name', 'city', 'county', 'area', 'address', 'build_time', 'price', 'data_time', 'name_location']
        self.writer = csv.DictWriter(self.file, fieldnames=fieldnames)
        self.writer.writeheader()

    def process_item(self, item, spider):
        self.writer.writerow(dict(item))
        return item

    def spider_closed(self, spider):
        self.file.close()


class MySQLPipeline(object):
    def __init__(self, host, database, user, password, port):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            host=crawler.settings.get('MYSQL_HOST'),
            database=crawler.settings.get('MYSQL_DATABASE'),
            user=crawler.settings.get('MYSQL_USER'),
            password=crawler.settings.get('MYSQL_PASSWORD'),
            port=crawler.settings.get('MYSQL_PORT')
        )

    def open_spider(self, spider):
        self.database = pymysql.connect(self.host, self.user, self.password, self.database, charset='utf8', port=self.port)
        self.cursor = self.database.cursor()
        sql = 'CREATE TABLE IF NOT EXISTS house_anjuke (' \
              'id BIGINT(20) NOT NULL AUTO_INCREMENT, ' \
              'name VARCHAR(255) NOT NULL, ' \
              'city VARCHAR(255) NOT NULL, ' \
              'county VARCHAR(255) NOT NULL, ' \
              'area VARCHAR(255) NOT NULL, ' \
              'address VARCHAR(255) NOT NULL, ' \
              'build_time VARCHAR(255) DEFAULT NULL, ' \
              'price VARCHAR(255) DEFAULT NULL, ' \
              'data_time DATETIME DEFAULT NULL,' \
              'name_location VARCHAR(255) NOT NULL,' \
              'source VARCHAR(255) DEFAULT NULL,' \
              'month INT(11) DEFAULT NULL,' \
              'year INT(11) DEFAULT NULL,' \
              'PRIMARY KEY(id),' \
              'UNIQUE KEY uidx_name_location (name_location)' \
              ')'
        self.cursor.execute(sql)

    def close_spider(self, spider):
        self.database.close()

    def process_item(self, item, spider):
        data = dict(item)
        keys = ', '.join(data.keys())
        values = ', '.join(['%s'] * len(data))
        sql = 'INSERT IGNORE INTO %s (%s) VALUES (%s)' % (item.table, keys, values)
        self.cursor.execute(sql, tuple(data.values()))
        self.database.commit()
        return item


class UniversalPipeline(object):
    def __init__(self, host, database, user, password, port):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port
        # self.file = codecs.open('citylinks_last_page.json', 'a', encoding='utf-8')

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            host=crawler.settings.get('MYSQL_HOST'),
            database=crawler.settings.get('MYSQL_DATABASE'),
            user=crawler.settings.get('MYSQL_USER'),
            password=crawler.settings.get('MYSQL_PASSWORD'),
            port=crawler.settings.get('MYSQL_PORT')
        )

    def open_spider(self, spider):
        self.database = pymysql.connect(self.host, self.user, self.password, self.database, charset='utf8', port=self.port)
        self.cursor = self.database.cursor()
        sql = 'CREATE TABLE IF NOT EXISTS house_anjuke (' \
              'id BIGINT(20) NOT NULL AUTO_INCREMENT, ' \
              'name VARCHAR(255) NOT NULL, ' \
              'city VARCHAR(255) NOT NULL, ' \
              'county VARCHAR(255) NOT NULL, ' \
              'area VARCHAR(255) NOT NULL, ' \
              'address VARCHAR(255) NOT NULL, ' \
              'build_time VARCHAR(255) DEFAULT NULL, ' \
              'price VARCHAR(255) DEFAULT NULL, ' \
              'data_time DATETIME DEFAULT NULL,' \
              'name_location VARCHAR(255) NOT NULL,' \
              'source VARCHAR(255) DEFAULT NULL,' \
              'month INT(11) DEFAULT NULL,' \
              'year INT(11) DEFAULT NULL,' \
              'PRIMARY KEY(id),' \
              'UNIQUE KEY uidx_name_location (name_location)' \
              ')'
        self.cursor.execute(sql)

    def close_spider(self, spider):
        self.database.close()
        # self.file.close()

    def process_item(self, item, spider):
        if isinstance(item, CommunityPriceItem):
            data = dict(item)
            keys = ', '.join(data.keys())
            values = ', '.join(['%s'] * len(data))
            sql = 'INSERT IGNORE INTO %s (%s) VALUES (%s)' % (item.table, keys, values)
            self.cursor.execute(sql, tuple(data.values()))
            self.database.commit()
            return item
        elif isinstance(item, NameLinkItem):
            one = json.dumps(dict(item), indent=2, ensure_ascii=False) + ",\n"
            with codecs.open('citylinks_last_page.json', 'a', encoding='utf-8') as file:
                file.write(one)
            return item
