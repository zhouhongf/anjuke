import pymysql
import json
import re
import time

db_name = 'houseprice'
table_name = 'house_anjuke'

db = pymysql.connect(host='localhost', user='root', password='@20110919Zyy==20170215Zyy@', port=3306, db=db_name)
cursor = db.cursor()

sql_create_city = 'CREATE TABLE IF NOT EXISTS house_price_city (' \
                  'id BIGINT(20) NOT NULL AUTO_INCREMENT, ' \
                  'city VARCHAR(255) NOT NULL, ' \
                  'year INT(11) NOT NULL, ' \
                  'jan_avg_price DOUBLE DEFAULT NULL, ' \
                  'feb_avg_price DOUBLE DEFAULT NULL, ' \
                  'mar_avg_price DOUBLE DEFAULT NULL, ' \
                  'apr_avg_price DOUBLE DEFAULT NULL, ' \
                  'may_avg_price DOUBLE DEFAULT NULL, ' \
                  'jun_avg_price DOUBLE DEFAULT NULL, ' \
                  'jul_avg_price DOUBLE DEFAULT NULL, ' \
                  'aug_avg_price DOUBLE DEFAULT NULL, ' \
                  'sep_avg_price DOUBLE DEFAULT NULL, ' \
                  'oct_avg_price DOUBLE DEFAULT NULL, ' \
                  'nov_avg_price DOUBLE DEFAULT NULL, ' \
                  'dec_avg_price DOUBLE DEFAULT NULL, ' \
                  'data_time DATETIME DEFAULT NULL,' \
                  'PRIMARY KEY(id)' \
                  ')'
cursor.execute(sql_create_city)

sql_create_county = 'CREATE TABLE IF NOT EXISTS house_price_county (' \
                    'id BIGINT(20) NOT NULL AUTO_INCREMENT, ' \
                    'county VARCHAR(255) NOT NULL, ' \
                    'city VARCHAR(255) NOT NULL, ' \
                    'year INT(11) NOT NULL, ' \
                    'jan_avg_price DOUBLE DEFAULT NULL, ' \
                    'feb_avg_price DOUBLE DEFAULT NULL, ' \
                    'mar_avg_price DOUBLE DEFAULT NULL, ' \
                    'apr_avg_price DOUBLE DEFAULT NULL, ' \
                    'may_avg_price DOUBLE DEFAULT NULL, ' \
                    'jun_avg_price DOUBLE DEFAULT NULL, ' \
                    'jul_avg_price DOUBLE DEFAULT NULL, ' \
                    'aug_avg_price DOUBLE DEFAULT NULL, ' \
                    'sep_avg_price DOUBLE DEFAULT NULL, ' \
                    'oct_avg_price DOUBLE DEFAULT NULL, ' \
                    'nov_avg_price DOUBLE DEFAULT NULL, ' \
                    'dec_avg_price DOUBLE DEFAULT NULL, ' \
                    'data_time DATETIME DEFAULT NULL,' \
                    'PRIMARY KEY(id)' \
                    ')'
cursor.execute(sql_create_county)

sql_create_area = 'CREATE TABLE IF NOT EXISTS house_price_area (' \
                  'id BIGINT(20) NOT NULL AUTO_INCREMENT, ' \
                  'area VARCHAR(255) NOT NULL, ' \
                  'county VARCHAR(255) NOT NULL, ' \
                  'city VARCHAR(255) NOT NULL, ' \
                  'year INT(11) NOT NULL, ' \
                  'jan_avg_price DOUBLE DEFAULT NULL, ' \
                  'feb_avg_price DOUBLE DEFAULT NULL, ' \
                  'mar_avg_price DOUBLE DEFAULT NULL, ' \
                  'apr_avg_price DOUBLE DEFAULT NULL, ' \
                  'may_avg_price DOUBLE DEFAULT NULL, ' \
                  'jun_avg_price DOUBLE DEFAULT NULL, ' \
                  'jul_avg_price DOUBLE DEFAULT NULL, ' \
                  'aug_avg_price DOUBLE DEFAULT NULL, ' \
                  'sep_avg_price DOUBLE DEFAULT NULL, ' \
                  'oct_avg_price DOUBLE DEFAULT NULL, ' \
                  'nov_avg_price DOUBLE DEFAULT NULL, ' \
                  'dec_avg_price DOUBLE DEFAULT NULL, ' \
                  'data_time DATETIME DEFAULT NULL,' \
                  'PRIMARY KEY(id)' \
                  ')'
cursor.execute(sql_create_area)

month_list = ['jan_avg_price', 'feb_avg_price', 'mar_avg_price', 'apr_avg_price', 'may_avg_price', 'jun_avg_price',
              'jul_avg_price', 'aug_avg_price', 'sep_avg_price', 'oct_avg_price', 'nov_avg_price', 'dec_avg_price']
data_time = time.strftime('%Y-%m-%d %H:%M:%S')
data_year = int(time.strftime('%Y'))
data_month = int(time.strftime('%m'))
sql_month = month_list[data_month - 1]


# 从json文件中读取出城市名称，并去掉重复的
cityNames = set()
with open('citylinks.json', 'r') as file:
    str = file.read()
    datas = json.loads(str)
    for data in datas:
        name = data.get('name')
        cityNames.add(name)

# 根据城市名称从数据库中找出该城市的数据
for cityname in cityNames:
    sql_city = 'SELECT * FROM {table} WHERE city="{cityname}"'.format(table=table_name, cityname=cityname)
    cursor.execute(sql_city)
    results_city = cursor.fetchall()
    columns_name = [col[0] for col in cursor.description]

    cityData = []
    city_sum = 0
    city_avg = 0
    for result in results_city:
        # 把城市数据做成一个字典类型的项目
        city = dict(zip(columns_name, result))
        # 筛选掉房价为 暂无数据 的项目
        theNum = re.match('\d+', city['price'])
        if theNum is not None:
            cityData.append(city)
            price = float(city['price'])
            city_sum += price
    if len(cityData) > 0:
        # 求整 房价平均值
        city_avg = city_sum // len(cityData)
        # 插入数据库
        data = {'city': cityname, 'year': data_year, sql_month: city_avg, 'data_time': data_time}
        table = 'house_price_city'
        keys = ', '.join(data.keys())
        values = ', '.join(['%s'] * len(data))
        sql = 'INSERT INTO {table}({keys}) VALUES ({values})'.format(table=table, keys=keys, values=values)
        try:
            if cursor.execute(sql, tuple(data.values())):
                print('成功插入一个城市的平均房价')
                db.commit()
        except:
            print('未能插入一个城市的平均房价')
            db.rollback()

    # 找出该城市中所有的 县 的名字
    countyNames = set()
    for city in cityData:
        # 去掉 县 名为空的记录
        county_name = re.match('\S+', city['county'])
        if county_name is not None:
            countyNames.add(county_name.group(0))

    # 遍历 县 名字， 获取各县的数据集合
    for county_name in countyNames:
        countyData = []
        county_sum = 0
        county_avg = 0
        for city in cityData:
            if city['county'] == county_name:
                countyData.append(city)
                price = float(city['price'])
                county_sum += price
        if len(countyData) > 0:
            # 求整 县 房价平均值
            county_avg = county_sum // len(countyData)
            data = {'county': county_name, 'city': cityname, 'year': data_year, sql_month: county_avg, 'data_time': data_time}
            table = 'house_price_county'
            keys = ', '.join(data.keys())
            values = ', '.join(['%s'] * len(data))
            sql = 'INSERT INTO {table}({keys}) VALUES ({values})'.format(table=table, keys=keys, values=values)
            try:
                if cursor.execute(sql, tuple(data.values())):
                    print('成功插入一个城市——县的平均房价')
                    db.commit()
            except:
                print('未能插入一个城市——县的平均房价')
                db.rollback()


        # 在该区县中，找出所有 区 的名字
        areaNames = set()
        for county in countyData:
            # 去掉 区 名为空的记录
            area_name = re.match('\S+', county['area'])
            if area_name is not None:
                areaNames.add(area_name.group(0))

        # 遍历 区 名字， 获取各区的数据集合
        for area_name in areaNames:
            areaData = []
            area_sum = 0
            area_avg = 0
            for county in countyData:
                if county['area'] == area_name:
                    areaData.append(county)
                    price = float(county['price'])
                    area_sum += price
            if len(areaData) > 0:
                area_avg = area_sum // len(areaData)
                data = {'area': area_name, 'county': county_name, 'city': cityname, 'year': data_year, sql_month: area_avg,'data_time': data_time}
                table = 'house_price_area'
                keys = ', '.join(data.keys())
                values = ', '.join(['%s'] * len(data))
                sql = 'INSERT INTO {table}({keys}) VALUES ({values})'.format(table=table, keys=keys, values=values)
                try:
                    if cursor.execute(sql, tuple(data.values())):
                        print('成功插入一个城市——县——区的平均房价')
                        db.commit()
                except:
                    print('未能插入一个城市——县——区的平均房价')
                    db.rollback()

db.close()

