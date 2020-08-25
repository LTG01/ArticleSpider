import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import time
from mouse import move, click
from chaojiying_Python.chaojiying import Chaojiying_Client
import base64
import re
try:
    import urlparse as parse
except:
    from urllib import parse

import scrapy
from scrapy.loader import ItemLoader
from ArticleSpider.items import ZhihuQuestionItem, ZhihuAnswerItem
import datetime


class ZhihuSpider(scrapy.Spider):
    # C:\Users\LTG\AppData\Local\Google\Chrome\Application
    # C:\Users\LTG\AppData\Local\Google\Chrome\Application>chrome.exe --remote-debugging-port=9222
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['https://www.zhihu.com/']

    #question的第一页answer的请求url
    # start_answer_url = "https://www.zhihu.com/api/v4/questions/{0}/answers?limit={1}&offset={2}"
    start_answer_url = 'https://www.zhihu.com/api/v4/questions/{0}/answers?include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cis_labeled%2Cis_recognized%2Cpaid_info%2Cpaid_info_content%3Bdata%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cbadge%5B%2A%5D.topics&limit={1}&offset={2}&platform=desktop&sort_by=default'

    headers = {
        "HOST": "www.zhihu.com",
        "Referer": "https://www.zhizhu.com"
        # 'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0"
    }
    def start_requests(self):
        chrome_options = Options()
        chrome_options.add_argument("--disable-extensions")
        # chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'])
        chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

        browser = webdriver.Chrome(chrome_options=chrome_options)

        try:
            browser.maximize_window()  # 将窗口最大化防止定位错误
        except:
            pass
        browser.get("https://www.zhihu.com/signin")
        # logo_element = browser.find_element_by_class_name("SignFlowHeader")
        # y_relative_coord = logo_element.location['y']
        #此处一定不要将浏览器放大 会造成高度获取失败！！！
        browser_navigation_panel_height = browser.execute_script('return window.outerHeight - window.innerHeight;')
        time.sleep(5)
        browser.implicitly_wait(5)
        #用来测试验证码，特意输入错误的密码
        #
        # try:
        #     tabs = browser.find_elements_by_css_selector(
        #         ".SignFlow-tabs div")
        #     tabs[1].click()
        # except:
        #     pass
        # browser.find_element_by_css_selector(".SignFlow-accountInput.Input-wrapper input").send_keys(Keys.CONTROL + "a")
        # browser.find_element_by_css_selector(".SignFlow-accountInput.Input-wrapper input").send_keys(
        #     "17628040175")
        #
        # browser.find_element_by_css_selector(".SignFlow-password input").send_keys(Keys.CONTROL + "a")
        # browser.find_element_by_css_selector(".SignFlow-password input").send_keys(
        #     "2014@ltg1")
        # browser.find_element_by_css_selector(
        #     ".Button.SignFlow-submitButton").click()
        # browser.implicitly_wait(5)

        # 先判断是否登录成功
        login_success = False
        while not login_success:
            try:
                notify_element = browser.find_element_by_class_name("AppHeader-profile")
                login_success = True

            except:
                pass
            try:
                tabs = browser.find_elements_by_css_selector(
                    ".SignFlow-tabs div")
                tabs[1].click()
            except :
                pass
            try:
                #查询是否有英文验证码
                english_captcha_element = browser.find_element_by_class_name("Captcha-englishImg")
                base64_text = english_captcha_element.get_attribute("src")
                #'data:image/jpg;base64,null'
                code = base64_text.replace('data:image/jpg;base64,', '').replace("%0A", "")
                if code == 'null':
                    english_captcha_element = None
            except:
                english_captcha_element = None
            try:
                # 查询是否有中文验证码
                chinese_captcha_element = browser.find_element_by_class_name("Captcha-chineseImg")
                base64_text = chinese_captcha_element.get_attribute("src")
                #'data:image/jpg;base64,null'
                code = base64_text.replace('data:image/jpg;base64,', '').replace("%0A", "")
                if code == 'null':
                    chinese_captcha_element = None
            except:
                chinese_captcha_element = None

            if not english_captcha_element and not chinese_captcha_element and not login_success:
                browser.find_element_by_css_selector(".SignFlow-accountInput.Input-wrapper input").send_keys(
                    Keys.CONTROL + "a")
                browser.find_element_by_css_selector(".SignFlow-accountInput.Input-wrapper input").send_keys(
                    "17628040175")
                browser.find_element_by_css_selector(".SignFlow-password input").send_keys(Keys.CONTROL + "a")
                browser.find_element_by_css_selector(".SignFlow-password input").send_keys(
                    "2014@ltg")
                browser.find_element_by_css_selector(
                    ".Button.SignFlow-submitButton").click()
                browser.implicitly_wait(5)

            if chinese_captcha_element:
                y_relative_coord = chinese_captcha_element.location['y']
                y_absolute_coord = y_relative_coord + browser_navigation_panel_height
                x_absolute_coord = chinese_captcha_element.location['x']
                # x_absolute_coord = 842
                # y_absolute_coord = 428

                """
                保存图片
                1. 通过保存base64编码
                2. 通过crop方法
                """
                # 1. 通过保存base64编码
                # base64_text = chinese_captcha_element.get_attribute("src")
                # #'data:image/jpg;base64,null'
                # code = base64_text.replace('data:image/jpg;base64,', '').replace("%0A", "")
                # print code
                fh = open("yzm_cn.jpeg", "wb")
                fh.write(base64.b64decode(code))
                fh.close()

                from zheye import zheye
                z = zheye()
                positions = z.Recognize("yzm_cn.jpeg")

                pos_arr = []
                if len(positions) == 2:
                    if positions[0][1] > positions[1][1]:
                        pos_arr.append([positions[1][1], positions[1][0]])
                        pos_arr.append([positions[0][1], positions[0][0]])
                    else:
                        pos_arr.append([positions[0][1], positions[0][0]])
                        pos_arr.append([positions[1][1], positions[1][0]])
                else:
                    pos_arr.append([positions[0][1], positions[0][0]])

                if len(positions) == 2:
                    first_point = [int(pos_arr[0][0] / 2), int(pos_arr[0][1] / 2)]
                    second_point = [int(pos_arr[1][0] / 2), int(pos_arr[1][1] / 2)]

                    move((x_absolute_coord + first_point[0]), y_absolute_coord + first_point[1])
                    click()

                    move((x_absolute_coord + second_point[0]), y_absolute_coord + second_point[1])
                    click()

                else:
                    first_point = [int(pos_arr[0][0] / 2), int(pos_arr[0][1] / 2)]

                    move((x_absolute_coord + first_point[0]), y_absolute_coord + first_point[1])
                    click()

                browser.find_element_by_css_selector(".SignFlow-accountInput.Input-wrapper input").send_keys(
                    Keys.CONTROL + "a")
                browser.find_element_by_css_selector(".SignFlow-accountInput.Input-wrapper input").send_keys(
                    "17628040175")

                browser.find_element_by_css_selector(".SignFlow-password input").send_keys(Keys.CONTROL + "a")
                browser.find_element_by_css_selector(".SignFlow-password input").send_keys(
                    "2014@ltg")
                browser.find_element_by_css_selector(
                    ".Button.SignFlow-submitButton").click()

            if english_captcha_element:
                # 2. 通过crop方法
                # from pil import Image
                # image = Image.open(path)
                # image = image.crop((locations["x"], locations["y"], locations["x"] + image_size["width"],
                #                     locations["y"] + image_size["height"]))  # defines crop points
                #
                # rgb_im = image.convert('RGB')
                # rgb_im.save("D:/ImoocProjects/python_scrapy/coding-92/ArticleSpider/tools/image/yzm.jpeg",
                #             'jpeg')  # saves new cropped image
                # # 1. 通过保存base64编码
                # base64_text = english_captcha_element.get_attribute("src")
                # code = base64_text.replace('data:image/jpg;base64,', '').replace("%0A", "")
                # print code
                fh = open("yzm_en.jpeg", "wb")
                fh.write(base64.b64decode(code))
                fh.close()

                # from tools.yundama_requests import YDMHttp
                # yundama = YDMHttp("da_ge_da1", "dageda", 3129, "40d5ad41c047179fc797631e3b9c3025")
                # code = yundama.decode("yzm_en.jpeg", 5000, 60)
                # while True:
                #     if code == "":
                #         code = yundama.decode("yzm_en.jpeg", 5000, 60)
                #     else:
                #         break
                chaojiying = Chaojiying_Client('yiqieanran01', '1qazxsw23edc',
                                               '904611')  # 用户中心>>软件ID 生成一个替换 96001
                im = open('yzm_en.jpeg', 'rb').read()  # 本地图片文件路径 来替换 a.jpg 有时WIN系统须要//
                code = chaojiying.PostPic(im, 1902)['pic_str']
                while True:
                    if code == '':
                        code = chaojiying.PostPic(im, 1902)['pic_str']
                    else:
                        break
                browser.find_element_by_xpath(
                    '//*[@id="root"]/div/main/div/div/div/div[1]/div/form/div[4]/div/div/label/input').send_keys(code)

                browser.find_element_by_css_selector(".SignFlow-accountInput.Input-wrapper input").send_keys(
                    Keys.CONTROL + "a")
                browser.find_element_by_css_selector(".SignFlow-accountInput.Input-wrapper input").send_keys(
                    "17628040175")
                browser.find_element_by_css_selector(".SignFlow-password input").send_keys(Keys.CONTROL + "a")
                browser.find_element_by_css_selector(".SignFlow-password input").send_keys(
                    "2014@ltg")
                browser.find_element_by_css_selector(
                    ".Button.SignFlow-submitButton").click()

            browser.implicitly_wait(5)
            try:
                notify_element = browser.find_element_by_class_name("AppHeader-profile")
                login_success = True

                Cookies = browser.get_cookies()
                print(Cookies)
                cookie_dict = {}
                import pickle
                f = open('C:\\LTG\\code\\ArticleSpider\\ArticleSpider\\cookies\\zhihu.cookie', 'wb')
                pickle.dump(Cookies, f)
                f.close()
                for cookie in Cookies:
                    # 写入文件
                    # 此处大家修改一下自己文件的所在路径
                    # f = open('C:\\LTG\\code\\ArticleSpider\\ArticleSpider\\cookies\\' + cookie['name'] + '.zhihu', 'wb')
                    # pickle.dump(cookie, f)
                    # f.close()
                    cookie_dict[cookie['name']] = cookie['value']
                # browser.close()
                return [scrapy.Request(url=self.start_urls[0], dont_filter=True, cookies=cookie_dict)]
            except:
                pass

        print("yes")

    def start_requests1(self):

        #C:\Users\LTG\AppData\Local\Google\Chrome\Application
        # C:\Users\LTG\AppData\Local\Google\Chrome\Application>chrome.exe --remote-debugging-port=9222
        chrome_options = Options()
        chrome_options.add_argument("--disable-extensions")
        # chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'])
        chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

        browser = webdriver.Chrome(chrome_options=chrome_options)

        # cookiese = pickle.load(open('C:\\LTG\\code\\ArticleSpider\\ArticleSpider\\cookies\\zhihu.cookie','rb'))
        # cookie_dict = {}
        # for cookie in cookiese:
        #     cookie_dict[cookie['name']] = cookie['value']
        # return [scrapy.Request(url=self.start_urls[0],dont_filter=True,cookies=cookie_dict)]

        browser.get("https://www.zhihu.com/signin")
        # logo_element = browser.find_element_by_class_name("SignFlowHeader")
        # y_relative_coord = logo_element.location['y']
        # 此处一定不要将浏览器放大 会造成高度获取失败！！！
        # browser_navigation_panel_height = browser.execute_script('return window.outerHeight - window.innerHeight;')
        time.sleep(5)
        browser.find_element_by_css_selector(".SignFlow-accountInput.Input-wrapper input").send_keys(Keys.CONTROL + "a")
        browser.find_element_by_css_selector(".SignFlow-accountInput.Input-wrapper input").send_keys(
            "17628040175")

        browser.find_element_by_css_selector(".SignFlow-password input").send_keys(Keys.CONTROL + "a")
        browser.find_element_by_css_selector(".SignFlow-password input").send_keys(
            "2014@ltg")
        time.sleep(5)
        browser.find_element_by_css_selector(
            ".Button.SignFlow-submitButton").click()
        # move(800, 400 ,True)
        # move(582, 493, True)
        # time.sleep(2)
        # click()

        # browser.get("https://www.zhihu.com")
        # cookiese = browser.get_cookies()
        #
        # pickle.dump(cookiese,open('C:\\LTG\\code\\ArticleSpider\\ArticleSpider\\cookies\\zhihu.cookie','wb'))
        # cookie_dict = {}
        # for cookie in cookiese:
        #     cookie_dict[cookie['name']] = cookie['value']
        # return [scrapy.Request(url=self.start_urls[0],dont_filter=True,cookies=cookie_dict)]

    def parse(self, response):
        """
              提取出html页面中的所有url 并跟踪这些url进行一步爬取
              如果提取的url中格式为 /question/xxx 就下载之后直接进入解析函数
              """
        all_urls = response.css("a::attr(href)").extract()
        all_urls = [parse.urljoin(response.url, url) for url in all_urls]
        all_urls = filter(lambda x: True if x.startswith("https") else False, all_urls)
        for url in all_urls:
            match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$).*", url)
            if match_obj:
                # 如果提取到question相关的页面则下载后交由提取函数进行提取
                request_url = match_obj.group(1)
                yield scrapy.Request(request_url, headers=self.headers, callback=self.parse_question)

            else:
                # 如果不是question页面则直接进一步跟踪
                yield scrapy.Request(url, headers=self.headers, callback=self.parse)
                pass

    def parse_question(self, response):
        #处理question页面， 从页面中提取出具体的question item
        if "QuestionHeader-title" in response.text:
            #处理新版本
            match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$).*", response.url)
            if match_obj:
                question_id = int(match_obj.group(2))

            item_loader = ItemLoader(item=ZhihuQuestionItem(), response=response)
            item_loader.add_css("title", "h1.QuestionHeader-title::text")
            item_loader.add_css("content", ".QuestionHeader-detail")
            item_loader.add_value("url", response.url)
            item_loader.add_value("zhihu_id", question_id)
            item_loader.add_css("answer_num", ".List-headerText span::text")
            # item_loader.add_css("comments_num", ".QuestionHeader-actions button::text")
            item_loader.add_css("comments_num", ".QuestionHeader-Comment button::text")

            # item_loader.add_css("watch_user_num", ".NumberBoard-value::text")
            item_loader.add_css("watch_user_num", ".NumberBoard-itemValue::text")
            item_loader.add_css("topics", ".QuestionHeader-topics .Popover div::text")

            question_item = item_loader.load_item()
        else:
            #处理老版本页面的item提取
            match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$).*", response.url)
            if match_obj:
                question_id = int(match_obj.group(2))

            item_loader = ItemLoader(item=ZhihuQuestionItem(), response=response)
            # item_loader.add_css("title", ".zh-question-title h2 a::text")
            item_loader.add_xpath("title", "//*[@id='zh-question-title']/h2/a/text()|//*[@id='zh-question-title']/h2/span/text()")
            item_loader.add_css("content", "#zh-question-detail")
            item_loader.add_value("url", response.url)
            item_loader.add_value("zhihu_id", question_id)
            item_loader.add_css("answer_num", "#zh-question-answer-num::text")
            item_loader.add_css("comments_num", "#zh-question-meta-wrap a[name='addcomment']::text")
            # item_loader.add_css("watch_user_num", "#zh-question-side-header-wrap::text")
            item_loader.add_xpath("watch_user_num", "//*[@id='zh-question-side-header-wrap']/text()|//*[@class='zh-question-followers-sidebar']/div/a/strong/text()")
            item_loader.add_css("topics", ".zm-tag-editor-labels a::text")

            question_item = item_loader.load_item()
        yield scrapy.Request(self.start_answer_url.format(question_id, 20, 0), headers=self.headers, callback=self.parse_answer)
        yield question_item

    def parse_answer(self, response):
        #处理question的answer
        ans_json = json.loads(response.text)
        is_end = ans_json["paging"]["is_end"]
        next_url = ans_json["paging"]["next"]
        #提取answer的具体字段
        for answer in ans_json["data"]:
            answer_item = ZhihuAnswerItem()
            answer_item["zhihu_id"] = answer["id"]
            answer_item["url"] = answer["url"]
            answer_item["question_id"] = answer["question"]["id"]
            answer_item["author_id"] = answer["author"]["id"] if "id" in answer["author"] else None
            answer_item["content"] = answer["content"] if "content" in answer else None
            answer_item["parise_num"] = answer["voteup_count"]
            answer_item["comments_num"] = answer["comment_count"]
            answer_item["create_time"] = answer["created_time"]
            answer_item["update_time"] = answer["updated_time"]
            # answer_item["crawl_time"] = datetime.datetime.now()

            yield answer_item

        if not is_end:
            yield scrapy.Request(next_url, headers=self.headers, callback=self.parse_answer)
