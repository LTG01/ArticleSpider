import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import sys
from selenium import webdriver
import time
import pickle
import os
from ArticleSpider.settings import BASE_DIR
from PIL import Image
from selenium.webdriver import ActionChains
from chaojiying_Python.chaojiying import *
from mouse import move, click
import datetime
import time
from ArticleSpider.utils.common import get_md5
from ArticleSpider.items import LagouJobItem,LagouJobItemLoader
from scrapy.loader import ItemLoader
from selenium.webdriver.chrome.options import Options
import parsel
import  re
import pprint

class LagouSpider(CrawlSpider):
    name = 'dzdp'
    allowed_domains = ['www.dianping.com']
    start_urls = ['https://www.dianping.com/']
    headers = {


    }
    custom_settings = {
        "COOKIES_ENABLED": False
    }
    #//www.dianping.com/zhuhai/ch0/r1904
    rules = (
        Rule(LinkExtractor(allow=r'shanghai/ch0/r\d+'), follow=True),
        Rule(LinkExtractor(allow=r'shanghai/ch10/g\d+'), follow=True),
        Rule(LinkExtractor(allow=r'shop/'),process_links='processLinks', callback='parse_job', follow=True),
    )

    # def start_requests(self):
        # # 去使用selenium模拟登录后拿到cookie交给scrapy的request使用
        # # 1、通过selenium模拟登录
        #
        # # chrome_options = Options()
        # # chrome_options.add_argument("--disable-extensions")
        # # # chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'])
        # # chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        # # browser = webdriver.Chrome(chrome_options=chrome_options)
        # browser = webdriver.Chrome()
        # browser.get("https://account.dianping.com/login?redir=http://www.dianping.com")
        # # 最大化窗口
        # browser.implicitly_wait(2)
        # browser.maximize_window()
        # browser.implicitly_wait(2)
        #
        # browser.implicitly_wait(2)
        # browser.maximize_window()
        # browser.implicitly_wait(2)
        #
        # iframe = browser.find_elements_by_tag_name('iframe')[0]
        # browser.switch_to.frame(iframe)
        # browser.find_element_by_class_name('icon-pc').click()
        # browser.implicitly_wait(2)
        #
        # browser.find_element_by_id('tab-account').click()
        # browser.implicitly_wait(2)
        #
        # browser.find_element_by_id("account-textbox").send_keys("17628040175")
        # browser.implicitly_wait(1)
        # browser.find_element_by_id('password-textbox').send_keys("1qazxsw23edc")
        # browser.find_element_by_id('login-button-account').click()
        #
        #
        #
        # # 从文件中读取cookies
        # cookies = []
        # if os.path.exists(BASE_DIR + "/ArticleSpider/cookies/lagou.cookie"):
        #     cookies = pickle.load(open(BASE_DIR + "/ArticleSpider/cookies/lagou.cookie", "rb"))
        #     for cookie in cookies:
        #         browser.add_cookie(cookie)
        #     browser.get("https://www.lagou.com/")
        # if not cookies:
        #     browser.get("https://passport.lagou.com/login/login.html")
        #     browser.find_element_by_css_selector(".form_body .input.input_white").send_keys("17628040175")
        #     browser.find_element_by_css_selector('.form_body input[type="password"]').send_keys("1qazxsw23edc")
        #     browser.find_element_by_css_selector('login-button-account').click()
        #     time.sleep(10)
        #
        #     while True:
        #         # 截图登陆界面，保存为 lagou_login.png
        #         browser.save_screenshot('lagou_login.png')
        #         # 及验证图片
        #         geetest_widget = browser.find_element_by_class_name('geetest_widget')
        #         # 获取验证码图片 起点坐标
        #         location = geetest_widget.location
        #         print(location)
        #         # 获取验证码图片长和宽
        #         size = geetest_widget.size
        #         print(size)
        #         # 验证码图片在整个截图中占据的位置
        #         rangle = (int(location['x']), int(location['y']),int(location['x'] + size['width']),
        #                   int(location['y'] + size['height']))
        #         code_img_name = 'lagou_code1.png'
        #         img = Image.open('./lagou_login.png')
        #         print(rangle)
        #         frame = img.crop(rangle)
        #
        #         frame.save(code_img_name)
        #
        #         # 压缩图片
        #         image = Image.open(code_img_name)
        #         # 缩小
        #         # 图片对象.thumbnail(大小) - 按比例缩放
        #         p = 2
        #         image_w, image_h = image.size
        #         image.thumbnail((image_w / p, image_h / p))
        #         # image.show()
        #         image.save('lagou_code.png')
        #         #超级鹰识别
        #         chaojiying = Chaojiying_Client('yiqieanran01', '1qazxsw23edc', '904611')  # 用户中心>>软件ID 生成一个替换 96001
        #         im = open('lagou_code.png', 'rb').read()  # 本地图片文件路径 来替换 a.jpg 有时WIN系统须要//
        #         code = chaojiying.PostPic(im, 9004)['pic_str']
        #         print(code)
        #         # 227,230|318,185
        #         # 处理返回的坐标
        #         pointlist = []
        #         if '|' in code:
        #             pointlistStr = code.split('|')
        #             pointlist = [(int(pointStr.split(',')[0])*p, int(pointStr.split(',')[1])*p) for pointStr in pointlistStr]
        #         else:
        #             pointlist = [(int(code.split(',')[0])*p, int(code.split(',')[1])*p)]
        #
        #         for point in pointlist:
        #             # x = int(location['x'])+int(point[0])
        #             # y = int(location['y'])+int(point[1])
        #             # move(x, y)
        #             # click()
        #
        #             ActionChains(browser).move_to_element_with_offset(geetest_widget, point[0], point[1]).click().perform()
        #             time.sleep(0.5)
        #         #点击确认按钮
        #         browser.find_element_by_class_name('geetest_commit_tip').click()
        #         # # 点击刷新按钮
        #         # browser.find_element_by_class_name('geetest_refresh_tip').click()
        #         # # 点击关闭按钮
        #         # browser.find_element_by_class_name('geetest_close_tip').click()
        #         browser.implicitly_wait(10)
        #         try:
        #             user_dropdown = browser.find_element_by_class_name('user_dropdown')
        #             break
        #         except Exception as e:
        #             print(str(e))
        #             time.sleep(1)
        #
        #     cookies = browser.get_cookies()
        #     # 写入cookie到文件中
        #     pickle.dump(cookies, open(BASE_DIR + "/ArticleSpider/cookies/lagou.cookie", "wb"))
        #
        # cookie_dict = {}
        # for cookie in cookies:
        #     cookie_dict[cookie["name"]] = cookie["value"]
        #
        # for url in self.start_urls:
        #     yield scrapy.Request(url, dont_filter=True, cookies=cookie_dict)

    def processLinks(self,links):

        for link in links:
            # if  str(link.url).__contains__('/review_all'):
            #     index = str(link.url).find('review_all')
            #     link.url = str(link.url)[:index+10]
            try:
                link.url = re.match('(https://www.dianping.com/shop/[a-zA-Z0-9]+/)', str(link.url)).group(0)+ 'review_all'
            except Exception as e:
                link.url += '/review_all'
            print('link.url',link.url)
        return links


    def get_html(self,response, t=''):
        '''
        获取网页源码
        :param url:
        :param headers:
        :return:
        '''

        if os.makedirs('./html', exist_ok=True):
            os.makedirs('./html')
        # shop-name

        # selector = parsel.Selector(response)
        shopname = response.css('.shop-name::text').get()

        name = './html/' + shopname + str(t) + '.html'
        with open(name, 'w', encoding='utf-8') as f:
            f.write(str(response.text))
        return response

    def get_css(self, response):
        '''
        根据网页获取 包含 svg的css 网址，并请求数据
        :param html_content:
        :return:
        '''
        # 获取css 文件路径
        #    <link rel="stylesheet" type="text/css" href="//s3plus.meituan.net/v1/mss_0a06a471f9514fc79c981b5466f56b91/svgtextcss/534bd1e1c2f9db95b1372081831d10e1.css">

        css_url = "http:" + re.findall(
            '<link rel="stylesheet" type="text/css" href="(//s3plus.meituan.net/v1/mss_0a06a471f9514fc79c981b5466f56b91/svgtextcss/.*?\.css)">',
            response.text)[0]

        # 获取 css内容
        css_content = requests.get(css_url).text
        # print(css_content)
        return css_content

    def get_backDic(self,css_content):
        '''

        根据css内容 获取背景
         获取类名称,根据不同类型获取不同的 svg 的url

        css内容 有如下三种

        svgmtsi[class^="dm"]{width: 14px;height: 24px;margin-top: -14px;background-image:

        cc[class^="tz"]{width: 14px;height: 16px;margin-top: -7px;

        bb[class^="rt"]{width: 14px;height: 22px;margin-top: -1px;

        :param css_content:
        :return:
        '''

        background_images = re.findall('(\w+)\[class\^="(\w+)"\]\{width:.*?background-image: url\((.*?)\);',
                                       css_content)
        # print(background_images)

        # 获取所有像素点坐标
        pattern = re.compile('.(\w+){background:-(\d+\.\d+)px -(\d+\.\d+)px;}')
        class_map = re.findall(pattern, css_content)
        # print(class_map)

        background_dics = {}
        for background_image in background_images:
            background_dic = {}
            back_type = background_image[0]
            back_className = background_image[1]
            back_url = 'http:' + background_image[2]

            background_dic['className'] = back_className
            background_dic['url'] = back_url

            class_name = {}
            for item in class_map:
                if item[0].startswith(back_className):
                    class_name[item[0]] = (float(item[1]), float(item[2]))
                pass

            background_dic[back_className] = class_name

            background_dics[back_type] = background_dic

        # pprint.pprint(background_dics)

        return background_dics

    def getvalue(self,posXY, index, values):
        '''

        根据坐标找出 被替换的字体
        :param posXY:  元组 ()
        :param index:  列表 [(),()]
        :param values: 列表 [[],[]]
        :return:
        '''

        if len(index) > 1:
            # 判断是否x的值一样
            if index[0][0] == index[1][0]:
                x = 0
                # 找到第几行
                for xindex in range(len(index)):

                    if posXY[1] <= int(index[xindex][1]):
                        value = values[x]
                        xyindex = int(posXY[0] / 14)
                        return value[xyindex]
                    x += 1

            # 判断是否y的值一样
            elif index[0][1] == index[1][1]:
                y = 0
                # 找到第几行
                for xindex in range(len(index)):

                    if posXY[1] <= int(index[xindex][0]):
                        value = values[y]
                        xyindex = int(posXY[0] / 14)
                        return value[xyindex]
                    y += 1

            else:
                xindex = 0
                for yindex in range(len(index)):
                    if posXY[1] <= int(index[yindex][1]):
                        xindex = int(index[yindex][0])
                        break
                # 找到具体的位置
                value = values[xindex - 1]
                xyindex = int(posXY[0] / 14)
                return value[xyindex]

    def getClassNames(self,dic, html_content, t=''):
        '''
         找到被替换的字体，
        :param dic:
        :param html_content:
        :return:
        '''

        for itemskey, itemsvalue in dic.items():

            tagList = re.findall('<' + itemskey + ' class="(.*?)"></' + itemskey + '>', html_content)

            svg_url = itemsvalue.get('url', None)
            svg_classValue = itemsvalue.get('className', None)

            svgcont = requests.get(svg_url).text

            # t=time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime())

            if os.makedirs('./html', exist_ok=True):
                os.makedirs('./html')
            svg_name = './html/' + itemskey + str(t) + '.svg'

            with open(svg_name, 'w') as f:
                f.write(svgcont)

            defs = re.findall('<defs>', svgcont)
            if len(defs) > 0:
                '''
                    <?xml version="1.0" encoding="UTF-8" standalone="no"?>
                    <!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
                    <svg xmlns="http://www.w3.org/2000/svg" version="1.1" xmlns:xlink="http://www.w3.org/1999/xlink" width="650px" height="322.0px">

                    <style>text {font-family:PingFangSC-Regular, Microsoft YaHei, 'Hiragino Sans GB', Helvetica; ;font-size:14px;fill:#666;}</style>
                    <defs><path id="1" d="M0 38 H600"/><path id="2" d="M0 75 H600"/><path id="3" d="M0 102 H600"/><path id="4" d="M0 132 H600"/><path id="5" d="M0 174 H600"/><path id="6" d="M0 202 H600"/><path id="7" d="M0 237 H600"/><path id="8" d="M0 276 H600"/></defs>
                    <text lengthAdjust="spacing">
                    <textPath xlink:href="#1" textLength="336">健关农街泉银肥宾津化信县淄民工迁孝盐安平光京乌振</textPath>
                    <textPath xlink:href="#2" textLength="308">淮青连康人红甘定公上汕二烟哈鞍胜合无大三主朝</textPath>
                    <textPath xlink:href="#3" textLength="588">衡园蒙常向夏府乐衢层台生头齐杭锡黑心岛苏十治山南海皇金云郑藏绍晋前石福清襄曙庆华鲁站</textPath>
                    <textPath xlink:href="#4" textLength="448">泰旗六太龙惠才陕湾体遵洛富中沙建肃楼机四绵一明徽沈迎家宿远嘉昌谐</textPath>
                    <textPath xlink:href="#5" textLength="532">育辽潍七木温天源友疆博圳幸九宜通号利团浙爱创邢东道梅花德庄兴港汉茂莞文学佛年</textPath>
                    <textPath xlink:href="#6" textLength="574">封昆汾春冈锦乡阳波广湛永谊内吉市古八弄贵廊湖解教祥充感省拥林环威沿风城保开桂肇西村</textPath>
                    <textPath xlink:href="#7" textLength="448">门黄尔珠凰赣军徐北长场放韶厦结和五重义交武香成名隆深设扬凤宁区坊</textPath>
                    <textPath xlink:href="#8" textLength="210">江川济都进业澳岳新河滨临路镇州</textPath>
                    </text></svg>     
                 '''
                # index 列表[(),(),()]
                index = re.findall('<path id="(\d+)" d="M0 (\d+) H\d+"/>', svgcont)
                textPath = re.findall('">(.*?)</textPath>', svgcont)
                values = [list(textPath[v]) for v in range(len(textPath))]

            else:
                # 第一种
                '''
                    <?xml version="1.0" encoding="UTF-8" standalone="no"?>
                    <!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
                    <svg xmlns="http://www.w3.org/2000/svg" version="1.1" xmlns:xlink="http://www.w3.org/1999/xlink" width="650px" height="64.0px">

                    <style>text {font-family:PingFangSC-Regular, Microsoft YaHei, 'Hiragino Sans GB', Helvetica; ;font-size:14px;fill:#666;}</style>
                        <text x="14 28 42 56 70 84 98 112 126 140 " y="41">4598036127</text>
                    </svg>
                '''
                # 第二种
                '''
                    <?xml version="1.0" encoding="UTF-8" standalone="no"?>
                    <!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
                    <svg xmlns="http://www.w3.org/2000/svg" version="1.1" xmlns:xlink="http://www.w3.org/1999/xlink" width="650px" height="274.0px">               
                    <style>text {font-family:PingFangSC-Regular, Microsoft YaHei, 'Hiragino Sans GB', Helvetica; ;font-size:14px;fill:#666;}</style>
                        <text x="0" y="26">宾吉汾化民西工襄前庆朝开路市感邢福曙新合友泰金家黑衡设隆常迎通沿富太层庄才川贵头园清</text>
                        <text x="0" y="63">谊无团晋佛城七主定辽台四鞍广莞乐嘉教州交公安蒙云湛遵尔关郑向源弄昌成三夏华黄徽苏梅济</text>
                        <text x="0" y="98">银惠锡泉港军康东滨山保宁鲁藏廊八肃年学重五宿皇宜结京茂楼名大人南岛乌都生圳淮区青沈文</text>
                        <text x="0" y="132">幸昆治津爱长内淄珠春甘凤澳远坊旗古香武中浙湾省林十六桂站深赣杭迁洛心兴业祥德孝烟红湖</text>
                        <text x="0" y="156">威创河齐一厦花博利场号健扬村韶九放阳石镇门永临明冈汕振府谐拥波解县建陕盐光哈上封农汉</text>
                        <text x="0" y="192">胜疆龙肇温二风木义肥江北衢进连绵徐信育沙和平秦街天绍机充锦环岳凰乡潍体海道</text>
                    </svg>
                '''
                # [(),()]
                posxydata = re.findall('<text x="(.*?)" y="(.*?)">(.*?)</text>', svgcont)

                if len(posxydata) > 1:
                    if posxydata[0][0] == posxydata[1][0]:
                        #
                        index = re.findall('<text x="(\d+)" y="(\d+)">', svgcont)
                        textPath = re.findall('">(.*?)</text>', svgcont)

                        values = [list(textPath[v]) for v in range(len(textPath))]
                else:
                    xs = posxydata[0][0].strip().split(' ')
                    index = [(int(i), float(posxydata[0][1])) for i in xs]
                    values = [list(posxydata[0][2]) for i in xs]

            for tag in tagList:
                pos = itemsvalue.get(svg_classValue, {}).get(tag)

                posxy = (float(pos[0]), float(pos[1]))
                fontvalue = self.getvalue(posxy, index, values)

                html_content = html_content.replace('<' + itemskey + ' class="' + tag + '"></' + itemskey + '>',
                                                    fontvalue)

        # t=time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime())
        selector = parsel.Selector(html_content)
        shopname = selector.css('.shop-name::text').get()

        name = './html/替换之后的-' + shopname + str(t) + '.html'
        with open(name, 'w', encoding='utf-8') as f:
            f.write(html_content)
        return html_content

    def parse_job(self, response):
        print(response.url)
        # print(response.text)

        t = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
        response = self.get_html(response,t)
        css_content = self.get_css(response)
        background_dics = self.get_backDic(css_content)
        html_content = self.getClassNames(background_dics, response.text, t=t)

        selector = parsel.Selector(html_content)
        shopname = response.css('.shop-name::text').get()
        print(shopname)
        total_reviews = selector.css('.reviews::text').get()
        print(total_reviews)
        total_price = selector.css('.price::text').get()
        print(total_price)
        total_score = selector.css('.rank-info .score .item::text').getall()
        print(total_score)
        adress = selector.css('.address-info::text').get()
        print(adress.strip())
        phone = selector.css('.phone-info::text').get()
        print(phone.strip())

        return ''