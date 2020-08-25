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


class LagouSpider(CrawlSpider):
    name = 'lagou'
    allowed_domains = ['www.lagou.com']
    start_urls = ['https://www.lagou.com/']
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.8",
        "Connection": "keep-alive",
        # "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36",
        "Referer": 'https://www.lagou.com',
        'Connection': 'keep-alive',
        "HOST": "www.lagou.com"
    }
    custom_settings = {
        "COOKIES_ENABLED": True
    }
    rules = (
        # Rule(LinkExtractor(allow=r'gongsi/j/\d+.html'), follow=True),
        # Rule(LinkExtractor(allow=r'zhaopin/.*'), follow=True),
        Rule(LinkExtractor(allow=r'jobs/\d+.html'), callback='parse_job', follow=True),
    )

    def parse_item(self, response):
        pass

    def start_requests(self):
        # 去使用selenium模拟登录后拿到cookie交给scrapy的request使用
        # 1、通过selenium模拟登录

        browser = webdriver.Chrome()

        browser.get("https://passport.lagou.com/login/login.html")
        #最大化窗口
        browser.implicitly_wait(2)
        browser.maximize_window()
        browser.implicitly_wait(2)
        # 从文件中读取cookies
        cookies = []
        if os.path.exists(BASE_DIR + "/ArticleSpider/cookies/lagou.cookie"):
            cookies = pickle.load(open(BASE_DIR + "/ArticleSpider/cookies/lagou.cookie", "rb"))
            for cookie in cookies:
                browser.add_cookie(cookie)
            browser.get("https://www.lagou.com/")
        if not cookies:
            browser.get("https://passport.lagou.com/login/login.html")
            browser.find_element_by_css_selector(".form_body .input.input_white").send_keys("17628040175")
            browser.find_element_by_css_selector('.form_body input[type="password"]').send_keys("1qazxsw23edc")
            browser.find_element_by_css_selector('div[data-view="passwordLogin"] input.btn_lg').click()
            time.sleep(10)

            while True:
                # 截图登陆界面，保存为 lagou_login.png
                browser.save_screenshot('lagou_login.png')
                # 及验证图片
                geetest_widget = browser.find_element_by_class_name('geetest_widget')
                # 获取验证码图片 起点坐标
                location = geetest_widget.location
                print(location)
                # 获取验证码图片长和宽
                size = geetest_widget.size
                print(size)
                # 验证码图片在整个截图中占据的位置
                rangle = (int(location['x']), int(location['y']),int(location['x'] + size['width']),
                          int(location['y'] + size['height']))
                code_img_name = 'lagou_code1.png'
                img = Image.open('./lagou_login.png')
                print(rangle)
                frame = img.crop(rangle)

                frame.save(code_img_name)

                # 压缩图片
                image = Image.open(code_img_name)
                # 缩小
                # 图片对象.thumbnail(大小) - 按比例缩放
                p = 2
                image_w, image_h = image.size
                image.thumbnail((image_w / p, image_h / p))
                # image.show()
                image.save('lagou_code.png')
                #超级鹰识别
                chaojiying = Chaojiying_Client('yiqieanran01', '1qazxsw23edc', '904611')  # 用户中心>>软件ID 生成一个替换 96001
                im = open('lagou_code.png', 'rb').read()  # 本地图片文件路径 来替换 a.jpg 有时WIN系统须要//
                code = chaojiying.PostPic(im, 9004)['pic_str']
                print(code)
                # 227,230|318,185
                # 处理返回的坐标
                pointlist = []
                if '|' in code:
                    pointlistStr = code.split('|')
                    pointlist = [(int(pointStr.split(',')[0])*p, int(pointStr.split(',')[1])*p) for pointStr in pointlistStr]
                else:
                    pointlist = [(int(code.split(',')[0])*p, int(code.split(',')[1])*p)]

                for point in pointlist:
                    # x = int(location['x'])+int(point[0])
                    # y = int(location['y'])+int(point[1])
                    # move(x, y)
                    # click()

                    ActionChains(browser).move_to_element_with_offset(geetest_widget, point[0], point[1]).click().perform()
                    time.sleep(0.5)
                #点击确认按钮
                browser.find_element_by_class_name('geetest_commit_tip').click()
                # # 点击刷新按钮
                # browser.find_element_by_class_name('geetest_refresh_tip').click()
                # # 点击关闭按钮
                # browser.find_element_by_class_name('geetest_close_tip').click()
                browser.implicitly_wait(10)
                try:
                    user_dropdown = browser.find_element_by_class_name('user_dropdown')
                    break
                except Exception as e:
                    print(str(e))
                    time.sleep(1)

            cookies = browser.get_cookies()
            # 写入cookie到文件中
            pickle.dump(cookies, open(BASE_DIR + "/ArticleSpider/cookies/lagou.cookie", "wb"))

        cookie_dict = {}
        for cookie in cookies:
            cookie_dict[cookie["name"]] = cookie["value"]

        for url in self.start_urls:
            yield scrapy.Request(url, dont_filter=True, cookies=cookie_dict)

    def parse_job(self, response):
        print(response.text)
        #解析拉勾网的职位
        item_loader = LagouJobItemLoader(item=LagouJobItem(), response=response)
        item_loader.add_css("title", ".job-name::attr(title)")
        item_loader.add_value("url", response.url)
        item_loader.add_value("url_object_id", get_md5(response.url))
        item_loader.add_css("salary", ".job_request .salary::text")
        item_loader.add_xpath("job_city", "//*[@class='job_request']/p/span[2]/text()")
        item_loader.add_xpath("work_years", "//*[@class='job_request']/p/span[3]/text()")
        item_loader.add_xpath("degree_need", "//*[@class='job_request']/p/span[4]/text()")
        item_loader.add_xpath("job_type", "//*[@class='job_request']/p/span[5]/text()")

        item_loader.add_css("tags", '.position-label li::text')
        item_loader.add_css("publish_time", ".publish_time::text")
        item_loader.add_css("job_advantage", ".job-advantage p::text")
        item_loader.add_css("job_desc", ".job_bt div")
        item_loader.add_css("job_addr", ".work_addr")
        item_loader.add_css("company_name", "#job_company dt a img::attr(alt)")
        item_loader.add_css("company_url", "#job_company dt a::attr(href)")
        # item_loader.add_value("crawl_time", datetime.datetime.now())

        job_item = item_loader.load_item()

        return job_item