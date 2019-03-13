

import contextlib
import pymysql
import datetime


# 定义上下文管理器，负责数据库连接
@contextlib.contextmanager
def mysql():
    conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='1234', db="webspider", charset='utf8')
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
    try:
        yield cursor
    finally:
        conn.commit()
        cursor.close()
        conn.close()


# 新的爬虫任务 ，新建两个表
def create_table(key_word):
    # 获取任务时间，确定任务id，确定表名
    spider_time = datetime.datetime.now()
    spider_id = spider_time.strftime("%Y%m%d%H%M%S")
    comment_table_name = spider_id + "comment"
    item_table_name = spider_id + "item"
    # date_time要写入总表
    date_time = spider_time.strftime("%Y-%m-%d %H:%M:%S")

    with mysql() as cursor:
        # 创建商品表
        sql = "create table " + item_table_name + "(" \
              "id integer unsigned not null auto_increment primary key," \
              "item_id char(15) not null," \
              "item_name text not null," \
              "good_rate float not null," \
              "good_count integer not null," \
              "general_count integer not null," \
              "poor_count integer not null," \
              "hot_comment text not null)"
        try:
            cursor.execute(sql)  # 创建表
        except pymysql.Error as e:
            print(e)

        # 创建评价表
        sql = "create table " + comment_table_name + "(" \
              "id integer unsigned not null auto_increment primary key," \
              "date_time char(25) not null," \
              "comment text not null," \
              "item_id integer unsigned not null," \
              "INDEX item_id_index (item_id)," \
              "INDEX date_time_index (date_time)," \
              "foreign key(item_id) references " + spider_id + "item(id))"
        try:
            cursor.execute(sql)  # 创建表
        except pymysql.Error as e:
            print(e)

    with mysql() as cursor:
        # 如果总表不存在，就创建总表
        exit_table = False
        sql = "select * from information_schema.tables where table_name = 'webspider';"
        try:
            exit_table = cursor.execute(sql)  # 执行查询，判断webspider总表是否存在
        except pymysql.Error as e:
            print(e)
        if not exit_table:
            sql = "create table if not exists webspider (" \
                  "id integer unsigned not null auto_increment primary key," \
                  "spider_id char(15) not null," \
                  "chinese_name text not null," \
                  "date_time text not null)"
            try:
                cursor.execute(sql)  # 创建表
            except pymysql.Error as e:
                print(e)

        # 爬虫任务信息写入总表
        sql = "insert into webspider(spider_id,chinese_name,date_time) " \
              "values(%s, %s, %s) "
        try:
            cursor.execute(sql, (spider_id, key_word, date_time))
        except pymysql.Error as e:
            print(e)

    return spider_id


# 存入具体数据
# spider_id：爬虫编号，base_info：基本信息，comment：具体评价
def save_item(spider_id, base_info, comments):
    if (base_info is None) or (comments is None):
        return
    with mysql() as cursor:
        # 商品基本信息写入到item表
        sql = "insert into " + spider_id + \
              "item(item_id,item_name,good_rate,good_count,general_count," \
              "poor_count,hot_comment) values(%s, %s, %s, %s, %s, %s, %s) "
        try:
            cursor.execute(sql, (base_info[0], base_info[1], base_info[2], base_info[3],
                                 base_info[4], base_info[5], base_info[6]))
        except pymysql.Error as e:
            print(e)

    with mysql() as cursor:
        # 从item表中获取商品id
        sql = "select id from " + spider_id + \
              "item where item_id = " + base_info[0]
        try:
            cursor.execute(sql)
            results = cursor.fetchall()
            item_id = results[0]['id']
        except pymysql.Error as e:
            print(e)
        # 把刚才获取到的id作为外键，和评价内容一起写入到comment表
        for com in comments:
            sql = "insert into " + spider_id + \
                  "comment(date_time,comment,item_id) values(%s, %s, %s) "
            try:
                cursor.execute(sql, (com[0], com[1], item_id))
            except pymysql.Error as e:
                print(e)
        # 打印一个日志，表示本商品相关操作至此执行完毕
        print(base_info[1])


def get_table():
    with mysql() as cursor:
        sql = "select * from webspider"
        try:
            cursor.execute(sql)
            return cursor.fetchall()
        except pymysql.Error as e:
            print(e)


def get_item(spider_id):
    with mysql() as cursor:
        sql = "select * from " + spider_id + "item"
        try:
            cursor.execute(sql)
            return cursor.fetchall()
        except pymysql.Error as e:
            print(e)


def get_comments(spider_id,item_id):
    with mysql() as cursor:
        try:
            sql = "select * from " + spider_id + "comment where item_id = %s"
            cursor.execute(sql, item_id)
            return cursor.fetchall()
        except pymysql.Error as e:
            print(e)


def count(spider_id):
    # 通过爬虫任务id提取时间戳
    length=len(spider_id)
    count0 = spider_id[:length - 19] + ","
    spider_id = spider_id.replace("-", "").replace(" ", "").replace(":", "")[length-19:length]
    date = datetime.datetime.strptime(spider_id[:8], "%Y%m%d")

    with mysql() as cursor:
        for i in range(-7, 0):
            day = (date + datetime.timedelta(days=i)).strftime("%Y-%m-%d")
            try:
                # 统计时间为day的这一天中商品的销量
                sql = "select count(1) from " + spider_id + \
                      "comment where date_time LIKE %s"
                cursor.execute(sql, day + '%')
            except pymysql.Error as e:
                print(e)
            count0 += day[5:] + ","
            count0 += str(cursor.fetchall()[0]['count(1)']) + ","
    return count0


