

import re
import requests
import time
from bs4 import BeautifulSoup
import mysql

# 根据url获取网页html
def get_html_text(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                                 'AppleWebKit/537.36 (KHTML, like Gecko) '
                                 'Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299',
                   'Accept-Language': 'zh-CN',
                   'Referer': 'https://www.jd.com/'}
        # timeout为最长等待时间
        r = requests.get(url, headers=headers, timeout=5)
        # 参数不是200则代表访问出错
        if r.status_code == 200:
            return r.text
        return None
    except requests.RequestException:
        print("获取网址" + url + "失败")
        return None


# 根据关键字和数量获取url集合
def get_url(key, item_num):
    list_url = []
    page = 1
    while page+1:
        url = "https://search.jd.com/Search?keyword=" +\
              key+"&enc=utf-8&page="+str(page)
        text = get_html_text(url)
        # 这个if是为了避免搜索结果过少导致死循环
        if text is None:
            if page > 100:
                break
            continue
        # BeautifulSoup模块实现html提取
        soup = BeautifulSoup(text, "html.parser")
        urls = soup.findAll("a", href=re.compile(
            "//item.jd.com/[^\D]*.html#comment"))
        # 把提取到的url存入数组
        for item_url in urls:
            s = item_url["href"]
            list_url.append("https:" + s)
        page += 2
        # 判断获取到的url个数是否足够
        if len(list_url) >= item_num:
            break
    while len(list_url) > item_num:
        list_url.pop()
    return list_url


# 根据url获取基本信息（产品名，好评率，基本评价）
def get_base_info(url):
    if url is "https:":
        return None
    text = get_html_text(url)
    if text is None:
        return None
    # 获取商品编号item_id和中文名name
    id_group = re.search('item\.jd\.com/(\d*)\.html', text).group()
    item_id = id_group[len('item.jd.com/'):-len('.html')]
    name_group = re.search('<title>(.*)</title>', text).group()
    name = name_group[len('<title>'):-len('</title>')]
    comments_text = get_html_text("https://sclub.jd.com/comment/productPageComments.action?productId=" +
                                  item_id + "&score=0&sortType=5&pageSize=10&page=0")
    if comments_text is None:
        return None
    # 获取好评率，好评数，中评数和差评数
    good_rate_show = re.search('(goodRate\":)((0\.(\d*))|(1\.0))', comments_text).group()
    good_rate = good_rate_show[len('goodRate":'):]
    good_count_show = re.search('goodCount\":(\d*)', comments_text).group()
    good_count = good_count_show[len('goodCount":'):]
    general_count_show = re.search('generalCount\":(\d*)', comments_text).group()
    general_count = general_count_show[len('generalCount":'):]
    poor_count_show = re.search('poorCount\":(\d*)', comments_text).group()
    poor_count = poor_count_show[len('poorCount":'):]
    # 获取热门评价并拼接成字符串
    hot_comment = ""
    hot_comment_tag = re.findall('name\":\"(.*?)\",\"rid(.*?)\",\"count\":(.*?),\"type', comments_text)
    for i in hot_comment_tag:
        hot_comment += i[0] + '(' + i[2] + ')' + '  '
    return [item_id, name, good_rate, good_count, general_count, poor_count,hot_comment]


# 根据url和评论数，获取具体评论
def get_comments(url, comment_num):
    text = get_html_text(url)
    if text is None:
        return None
    # 获取商品编号
    id_group = re.search('item\.jd\.com/(\d*)\.html', text).group()
    item_id = id_group[len('item.jd.com/'):-len('.html')]
    comment_url = "https://sclub.jd.com/comment/productPageComments.action?productId=" + item_id + \
                  "&score=0&sortType=5&pageSize=10&page="
    # 二维数组，存放待返回的数据
    comment = [[]]
    page= 0
    n = comment_num
    comment.pop()
    while n > 0:
        # 根据商品编号和当前页数，并构造商品对应的url
        comment_url_page = comment_url + str(page)
        comment_html_text = get_html_text(comment_url_page)
        if comment_html_text is None:
            return None
        # 通过findall函数获取多个符合正则表达式的字段
        comment_set = re.findall('topped\":0,\"guid\":(.*?)\",\"content\":\"(.*?)\",'
                                 '\"creationTime\":\"(.*?)\"', comment_html_text)
        if len(comment_set) is 0:
            break
        page += 1
        # 保存获取到的字段
        for i in comment_set:
            comment.append([i[2], i[1]])
            n -= 1
    while len(comment) > comment_num:
        comment.pop()
    return comment


def spider(key, item_num, comment_num):
    try:
        list_url = get_url(key, int(item_num))
        spider_id = mysql.create_table(key)
        for url in list_url:
            base_info = get_base_info(url)
            comments = get_comments(url, int(comment_num))
            mysql.save_item(spider_id, base_info, comments)
            time.sleep(2)
    except Exception as e:
        return 1
    return 0

