#!/usr/bin/python
# coding=utf-8

import urllib2
import re
import xlwt
import threading

# URL
url = "https://www.amazon.co.uk/gp/bestsellers/luggage/1769584031/ref=pd_zg_hrsr_luggage_2_3_last"
url_uk = "https://www.amazon.co.uk"
asin_link_list = []
asin_list = []
best_List = []

# 正则表达式
href = r'.*a-link-normal.*href=\"(.*?)\"'
link = r'.*/dp/.*'
asin_1 = r'<li><b>ASIN:</b> (B0.*?)</li>'
asin_2 = r'<td class=\"value\">(B0.*?)</td>'
asin_3 = r'.*name=\"ASIN\" value=\"(B0.*?)\">'
asin_4 = r'B0[\w]*'
flow_word = r'.*k=(.*?)\".*container=\"body\">(.*?)<'

# 请求头
headers = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}


def getURL(url):
    # 获取网址  # 打开网址
    try:
        req = urllib2.Request(url, headers=headers)

        html = urllib2.urlopen(req)

        if html.getcode() == 200:
            print ("已捕获"), url, "目标站数据..."
            return html
        else:
            print ("访问出现错误...错误代码："), html.getcode()
            return None
    except Exception, e:
        print 'connection failed'


# 按特定要求查询获取网页内的链接
def sreaching(getmatch, data):
    try:
        data = re.findall(getmatch, data, re.I)
    except:
        print 'connection failed'
    return data


def findAsin(url_best):

    data = getURL(str(url_best)).read().decode('utf-8')

    # print data

    get_asin = re.search(asin_1, data, re.I)
    if get_asin is None:
        get_asin = re.search(asin_3, data, re.I)

    a = get_asin.group()

    if a not in asin_list:
        get_asin_B0 = re.search(asin_4, a, re.I)
        print get_asin_B0.group() + " put in asin_list!"
        lock.acquire()
        asin_list.append(get_asin_B0.group())
        asin_link_list.append("https://www.asinseed.com/cn/UK?q=" + get_asin_B0.group())
        lock.release()


if __name__ == '__main__':
    print("===============start===============")

    data = getURL(url).read()
    hrefList = sreaching(href, data)

    print "get the best 50 products link:"
    for hre in hrefList:
        asinList = sreaching(link, hre)
        if asinList is not None:
            if str(asinList) != "[]":
                if asinList not in best_List:
                    best_List.append(url_uk + str(asinList).strip().strip('[]\''))
                    print url_uk + str(asinList).strip().strip('[]\'')

    print "===============get asin==============="
    # TODO LONG TIME IN HERE NEED TO GET GIL

    threads = []
    lock = threading.Lock()

    for url_best in best_List:
        # i += 1
        t = threading.Thread(target=findAsin, args=(url_best,))
        threads.append(t)

    for t in threads:
        t.start()

    for t in threads:
        t.join()



    print "===============get asin list==============="

    wbk = xlwt.Workbook()
    sheet = wbk.add_sheet('sheet 1')
    i = 0
    for l in asin_list:
        print l
        sheet.write(0, i, l)  # 第0行第一列写入内容
        i = i + 2

    row = 1
    col = 0
    for asinSeedLink in asin_link_list:
        print asinSeedLink
        data = getURL(asinSeedLink).read()
        hrefList = sreaching(flow_word, data)
        for asin in hrefList:
            print asin
            print "\n"
            sheet.write(row, col, asin[0])
            sheet.write(row, col + 1, asin[1])
            row = row + 1
        col = col + 2
        row = 1

    wbk.save('Asin.xls')
    print "Finish!"
