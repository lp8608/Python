#!/usr/bin/env python
#-*- coding: UTF-8 -*-
# @File    :   meizitu.py
# @Time    :   2019/3/18 0018 12:55
# @Author  :   LIPENGAK 
# @Version :   1.0
# @Contact :   lipengak@dcits.com
# @License :   Copyright © 2019 DCITS. All Rights Reserved
# @Desc    :   通过urllib2，bs4 单线程抓取图片

'''
❤️❤️ 背景简介 ❤️❤️

 🎈妹子图:🎈
    有两个:  图片都一样.
    www.meizitu.com 没广告, 一页多张照片. 不好爬
    www.mzitu.com   广告多, 一页一张照片. 有水印,容易爬
    先来简单的，于是爬了www.mzitu.com

 🎈网站分析🎈:
     妹子图几乎每天都更新，
     到现在为止有 140页
     每页24个主题写真，
     每个主题下有几十张照片，每张照片一个网页.
     网页结构简单.用 BeautifulSoup 就可以轻松爬取。

    📌 网站140+页.  每页的网址很有规律 1-140
        只要能获得一个页面里面的数据
        剩下页面的数据只要从1到140 循环.就可以了
        http://www.mzitu.com/page/1
        http://www.mzitu.com/page/2
        http://www.mzitu.com/page/3
        ......
        http://www.mzitu.com/page/140

    📌 每页24个主题. 每个主题一个链接.
        http://www.mzitu.com/87933
        http://www.mzitu.com/87825
        每个主题之间就没什么联系了.
        所有主题的网址就得手动爬下来.
        这里就不能用循环了...

    📌 每个主题诺干张图片. 每张图片一个网址
        http://www.mzitu.com/86819/1
        http://www.mzitu.com/86819/2
        http://www.mzitu.com/86819/3
        单个主题下的图片很有规律
        只要知道这个主题的图片数量就能循环出某主题下所有的网址.
        这个网址 不等于 图片的网址.
        图片网址 需要到每个网页下面匹配出来.



 🎈爬虫步骤：🎈
     整个妹子图所有主题的网址.            get_page1_urls
     某主题下第一张照片地址               get_img_url
     某主题的照片数                       get_page_num
     用循环获取某主题下所有照片地址       get_img_url
     获取各个主题的主题名字               get_img_title
     下载所有主题下的所有照片             download_imgs

'''


# ❤️❤️ ↓↓↓ 0: 依赖模块 ↓↓↓ ❤️❤️


import urllib2
import threadpool
from bs4 import BeautifulSoup  # 解析网页内容
import re                      # 正则式模块.
import os                      # 系统路径模块: 创建文件夹用
import socket                  # 下载用到?
import time                    # 下载用到?
import random

# 收集到的常用Header
my_headers = [
    "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/537.75.14",
    "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Win64; x64; Trident/6.0)",
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
    'Opera/9.25 (Windows NT 5.1; U; en)',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
    'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',
    'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12',
    'Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9',
    "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Ubuntu/11.04 Chromium/16.0.912.77 Chrome/16.0.912.77 Safari/535.7",
    "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:10.0) Gecko/20100101 Firefox/10.0 "
]


# ❤️❤️ ↓↓↓ 0基础入门例子 ↓↓↓ ❤️❤️


'''
resp = urllib2.urlopen('https://www.mzitu.com/page/2')
html = resp.read()
print(html)
'''
# 浏览器输入网址就下载网页并显示给你.
# 终端怎么下载网页呢.  用 urllib2 / urllib2 是最方便的.
# 首先python3 的话:  import urllib2 导入这个下载网页的库.
# 然后上面第一行只要改掉urlopen 双引号里面的网址就可以爬你想要的网址了.
# 就可以在终端显示出 某个网站的源代码了, 这样一个网页就算被你爬下来了!! 很简单吧.
# response = urllib2.urlopen("https://www.0214.live")
# 调用 urllib库 里面的 urlopen 这个方法,这个方法需要传入一个数据.一般都是网址.
# 把 整个网页数据保存到 response 这个变量中.
# 这行其实可以分成两行.
# request = urllib2.Request("https://www.0214.live")
# response = urllib2.urlopen(request)
# 推荐大家这么写. 最终会有很多代码. 这样写逻辑上更清晰.
# 先传入一个请求,  然后再打开网站
# print response.read()
# 读取变量的内容. 也就是整个网页的内容

# 上面三行是获取网页源代码的方法.
# 取消注释. 就能在终端显示妹子图第一页的源代码了.
# 接下来需要从源代码里面. 找出第一页的24个 主题地址网址!
# 这里就要用 beautifulsoup 4 模块来提取网页中指定内容了. 简称 bs4
# 下面是 bs4 的基本用法.
'''
# soup = BeautifulSoup(html, "lxml")
# 把网页源代码 结构化成 DOM树.
# 之后就可以用 soup.title; soup.p; soup.a; 来输出网页里面的内容了.
# 你只要改 html 这个变量就可以了. 后面的解析器不要动.

# print(soup.title)
# → <title>妹子图_性感妹子图片_日本美女图片_清纯妹子写真 </title>
# 输出网页标题(带标签的!)

# print(soup.title.string)
# → 妹子图_性感妹子图片_日本美女图片_清纯妹子写真 
# 输出网页标题(不带标签的!,只输出标题内容)

# print("这个网页标题:" + soup.title.string)
# 如果要输出自定义内容 需要用双引号 加上+号

# print(soup.a)
# → <a href="http://www.mzitu.com/">妹子图</a>
# 这个是输出网页中遇到的第一个链接.

# find_all() 搜索元素,
# find_all('a')  → 搜索所有的a  链接 
# find_all('p')  → 搜索所有的p  段落
# find_all('li') → 搜索所有的li 列表项目
# find_all() 也能用正则式来匹配搜索,这里就不介绍了..

# for link in soup.find_all('a'):
# print(link.get('href'))
# 这是找出网页内所有的链接.
# link是个变量. 名字任取. 只要上下两行对应就可.
# for xxx in soup.find_all('a'):
#     print(xxx.get('href'))

# 搜索网页中所有的 id 是pins 的ul元素
# for link in soup.find_all('ul', id="pins"):
#     print(link)
# 搜索网页中所有的 class 是 的img元素
# for link2 in soup.find_all('img', "lazy"):
#     print(link2)
# ID 和 Class 稍微有点区别. 多参数情况下默认是搜索class的
'''
# 了解了bs4 的基本用法. 就可以 把网址中的特定的网址加到某个数组里了.
# 功能: 把 id 是 pins 的ul元素 下面的所有li里的链接 加到一个数组里面
# 每页的24个妹子主题. 都是在 <ul id="pins"> 下面的24个li中.
# li里包含很多无用的信息:比如标题,时间. 我们只要里面的网址.
# 用循环把每个主题的地址. 添加到page1_urls 这个数组里面.
'''
page1_urls = []
lis = soup.find('ul', {'id': 'pins'}).find_all('li')
print(lis)
for li in lis:
    page1_urls.append(li.find('a')['href'])
print(page1_urls)

# 下面是结果
# ✘✘∙𝒗 zz python3 mzitu00.py
# ['http://www.mzitu.com/88557', 'http://www.mzitu.com/88509', 'http://www.mzitu
# .com/88458', 'http://www.mzitu.com/88415', 'http://www.mzitu.com/88373', 'http
# ://www.mzitu.com/88317', 'http://www.mzitu.com/88250', 'http://www.mzitu.com/8
# 8209', 'http://www.mzitu.com/88162', 'http://www.mzitu.com/88116', 'http://www
# .mzitu.com/88065', 'http://www.mzitu.com/88014', 'http://www.mzitu.com/87933',
#  'http://www.mzitu.com/87973', 'http://www.mzitu.com/87825', 'http://www.mzitu
# .com/87813', 'http://www.mzitu.com/87762', 'http://www.mzitu.com/87693', 'http
# ://www.mzitu.com/87628', 'http://www.mzitu.com/87580', 'http://www.mzitu.com/8
# 7541', 'http://www.mzitu.com/87500', 'http://www.mzitu.com/87434', 'http://www
# .mzitu.com/87390']

# 看了上面的例子就会爬第一个页面上的24个主题的链接了,只要用循环就能爬所有页面了!!!
'''


# ❤️❤️ ↓↓↓ 获取整个妹子网所有的主题 ↓↓↓ ❤️❤️


def get_page1_urls():          # 定义一个函数
    page1_urls = []            # 定义一个数组,来储存所有主题的URL
    for page in range(1, 2):
        # 1-140. 整个妹子图只有140页,注意下面缩进内容都在循环内的!
        url = 'http://www.mzitu.com/page/' + str(page)
        request = urllib2.Request(url)
        # 制作请求头了. 140页 每页都请求一遍. 自然就能获取到每页下的24个主题了
        html = urllib2.urlopen(request, timeout=20).read()
        # read 就是读取网页内容并储存到 html变量中.
        soup = BeautifulSoup(html, 'lxml')
        # 把下载的网页.结构化成DOM, 方便下面用 find 取出数据
        lis = soup.find('ul', {'id': 'pins'}).find_all('li')
        # 找到 id 为pins 这个列表下面的 每个列 就找到每个页面下的 24个主题了
        for li in lis:
            # 遍历每页下面的24个主题 (也就是24个li)
            # page1_urls.append(li.find('a')['href'])
            if len(li.select('span > a')) > 0 :
                page1_urls.append(li.select('span > a')[0]['href'])
            # 把每个主题的地址. 添加到page1_urls 这个数组里面.
        # print(page1_urls)
        # # 显示网址. 测试用. 循环140次. 这样就获得了所有主题的网址了
    return page1_urls


# ❤️❤️ ↓↓↓ 自动获取某主题的照片数量 ↓↓↓ ❤️❤️
# 进入某个主题, 然后分析底部的 导航条.
# 导航条格式: 上一组 1 2 3 4 ... 64 下一组
# 很多按钮.每个按钮都是一个<a>元素.
# 倒数第二个<a>元素 这里也就是64 就是照片数量!


def get_page_num(page1_url):        # 参数 page1_url 不一定要外界传入的. 可以给函数里面用的.
    request = urllib2.Request(page1_url)
    try:
        html = urllib2.urlopen(request, timeout=20).read()
    except:
        try:
            html = urllib2.urlopen(request, timeout=20).read()
        except:
            return None
            # 这个函数会重复请求两次. 如果两次都超时就放弃.
    soup = BeautifulSoup(html, 'lxml')
    try:
        page_num = soup.find('div', {'class': 'pagenavi'}).find_all('a')[-2].find('span').get_text()
    except:
        return None
    return int(page_num)
# aa = get_page_num("http://www.mzitu.com/858")
# print(aa)
# 这两行是测试 某主题下的图片数量的. 你随便填个妹子图的主题地址进去.看看对不对.


# ❤️❤️ 三: 获取某主题下第一张照片的URL. ❤️❤️
# 结合上面的照片数量. 就能获取到某主题下的所有照片链接了.


def get_img_url(url):
    request = urllib2.Request(url)
    try:
        html = urllib2.urlopen(request, timeout=20).read()
    except:
        try:
            html = urllib2.urlopen(request, timeout=20).read()
        except:
            return None
    soup = BeautifulSoup(html, 'lxml')
    try:
        img_url = soup.find(
            'div', {'class':
                    'main-image'}).find('p').find('a').find('img')['src']
    except:
        return None
    return img_url
# bb = get_img_url("http://www.mzitu.com/858")
# print(bb)
# 这两行是测试 某主题下第一张图片的真实url的.  亲测通过.


# ❤️❤️ 四: 获取某主题下所有照片的URL. ❤️❤️


# 然后就要获取某主题下所有照片的URL的函数
# 这时候就用到了 上面两个函数了.
# 这个函数 要传入一个参数.也就是主题的URL地址.
# 每个主题都循环一遍 就能获取所有主题的所有照片了.
# 任务也就只差下载了.


def get_img_urls(page1_url):
    page_num = get_page_num(page1_url)
    # 这里就用到了 上面的 get_page_num 这个函数了.
    if page_num is None:
        return None
    img_urls = {}
    # 定义一个数组 来储存该主题下的 所有照片的 URL
    for page in range(1, page_num + 1):
        url = page1_url + '/' + str(page)
        # 实际照片的链接地址 就是主题的链接 + / + 数量
        img_url = get_img_url(url)
        # 这里用到了 get_img_url 这个函数. 可以获取该主题下的第一张照片.
        # 现在是在循环里面. 循环次数就是 该主题的照片数量+1
        if img_url is None:
            return None
        else:
            img_urls[url] = img_url
        # 把获取到的 url 添加到 img_urls 这个数组里.
        # 这样循环下来 img_urls 数组里面就有该主题下的所有照片地址了
    return img_urls

# cc = get_img_urls("http://www.mzitu.com/858")
# print(cc)
# 这两行是测试 某主题下所有图片的真实url的.  亲测通过.


# ❤️❤️ 五: 获取某主题名称,创建本地文件夹用 ❤️❤️


def get_img_title(page1_url):
    request = urllib2.Request(page1_url)
    try:
        html = urllib2.urlopen(request, timeout=20).read()
    except:
        try:
            html = urllib2.urlopen(request, timeout=20).read()
        except:
            return None
    soup = BeautifulSoup(html, 'lxml')
    # <h2 class="main-title">古典气质型美女施诗 顶级美腿加酥胸圆臀火辣身材性感十足</h2>
    title = soup.find('h2', {'class': 'main-title'}).get_text()
    # 下面两行是异常分析..
    removeSign = re.compile(r'[\/:*?"<>|]')
    # re 就是正则表达式模块
    # re.compile 把正则表达式封装起来. 可以给别的函数用. ()里面的才是真的 表达式.
    # r'[\/:*?"<>|]'
    # [] 表示一个字符集;  \对后面的进行转义 英文/是特殊符号; 其他的是正常符号.
    title = re.sub(removeSign, '', title)
    # re.sub 在字符串中 找到匹配表达式的所有子串. 用另一个进行替换.这里用'' 就是删除的意思.
    # 就是说 删除标题里面的 /:*?"<>| 这些符号.
    # 英文创建文件夹时候 不能有特殊符号的!!!
    return title
# dd = get_img_title("http://www.mzitu.com/858")
# print(dd)
# 这两行是测试 某主题的主题名.  亲测通过.


# ❤️❤️ 六: 定义下载某主题所有图片的函数 ❤️❤️
# 下载肯定要创建文件夹.要用到路径.这就需要 os 模块了.
# 我们把照片 建立个文件夹 下载到 脚本运行的目录下
# os.path模块主要用于文件的属性获取，经常用到，以下是该模块的几种常用方法
# print(os.getcwd())                 # 获取并输出当前脚本所在的目录.
# os.mkdir('./妹子图')               # 在当前文件夹下 建立 妹子图 文件夹.
# os.rmdir('./妹子图')               # 在当前文件夹下 删除 妹子图 文件夹.
# if os.path.exists('./妹子图'):     # 判断当前文件夹 是否存在   妹子图这个文件夹
# if not os.path.exists('./妹子图'): # 判断当前文件夹 是否不存在 妹子图这个文件夹
# 本项目我们先判断当前脚本文件夹 是否已经有妹子图这个文件夹存在.
# 如果不存在那就新建一个妹子图文件夹.
# 再判断妹子图文件夹下 有没有对应的子文件夹存在.


def download_imgs(page1_url,fileNameEncode):
    img_urls = get_img_urls(page1_url)
    pic_path = './妹子图'
    if img_urls is None:
        return None
    title = get_img_title(page1_url)
    if title is None:
        return
    print os.path
    local_path = pic_path + "/" + title.replace(' ','')
    if not os.path.exists(local_path):
        try:
            os.makedirs(local_path.encode(fileNameEncode))
        except:
            pass
    if img_urls is None or len(img_urls) == 0:
        return
    else:
        print('--开始下载' + title + '--')
        for link in img_urls:
            img_url = img_urls[link]
            img_name = local_path + '/' + os.path.basename(img_url)
            req = urllib2.Request(img_url)
            req.add_header('User-Agent',random.choice(my_headers))
            req.add_header("Referer", link)
            fp = urllib2.urlopen(req)
            f = open(img_name.encode(fileNameEncode), 'wb')
            f.write(fp.read())
            f.close()
            print('--' + img_name + '下载完成--')


# ee = download_imgs("http://www.mzitu.com/858")
# print(ee)
# 成功下载一套主题!!!!
# ❤️❤️ 七: 下载所有主题的图片 ❤️❤️


def craw_meizitu(fileNameEncode):
    page1_urls = get_page1_urls()
    # 这里用到了 第一个函数. 也就是获取所有主题的 URL.
    if page1_urls is None or len(page1_urls) == 0:
        return
    else:
        # 利用线程池多线程下载图片
        args = [((item, fileNameEncode), None) for item in page1_urls]
        pool = threadpool.ThreadPool(10)
        requests = threadpool.makeRequests(download_imgs, args)
        [pool.putRequest(req) for req in requests]
        pool.wait()
        # for page1_url in page1_urls:
        #     # 循环第六步 来下载所有主题的URL
        #     download_imgs(page1_url,fileNameEncode)
    print "下载完成! 共下载" + len(page1_urls) + "张图片！"

def main():
    import sys
    reload(sys)
    sys.setdefaultencoding('utf-8')
    craw_meizitu("gbk")
if __name__ == '__main__':
    main()
