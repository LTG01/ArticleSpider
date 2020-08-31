
import requests
import re
import json
import time
import multiprocessing
# from lagou_spider.handle_insert_data import lagou_mysql
import pprint

class HandleLaGou(object):
    def __init__(self, ):
        self.lagou_session = requests.Session()
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
        }
        self.city_dict = dict()  # 用于存储所有城市的名字和对应的代码编号
        self.city_name_list = list()  # 用于存储所有城市的名字
        self.api_url = "http://dynamic.goubanjia.com/dynamic/get/4fb8e6f11b87aab615e95c55691b669e.html"
        self.ip_port = ""

    # 获取全国所有城市code的方法
    def handle_city_code(self):
        city_url = "https://www.lagou.com/jobs/list_python?labelWords=&fromSearch=true&suginput="
        city_result = self.handle_request(method='GET', url=city_url)
        city_code = re.search(r'global.cityNumMap = (.*);', city_result)
        if city_code:
            self.city_dict = json.loads(city_code.group(1))
            self.city_name_list = self.city_dict.keys()
        self.lagou_session.cookies.clear()

    def handle_city(self, city):
        first_request_url = "https://www.lagou.com/jobs/list_python/p-city_%s?px=default" % self.city_dict[city]
        first_response = self.handle_request(method="GET", url=first_request_url)
        try:
            total_page = int(re.search(r'span totalNum.*?(\d+)</span>', first_response).group(1))
            print(city)
        # 有些城市没有该岗位信息 造成异常所以直接return
        except Exception as e:
            return
        else:
            for i in range(1, total_page + 1):
                # post请求要携带的参数
                data = {
                    'first': 'true',
                    'pn': i,
                    'kd': 'python'
                }
                page_url = "https://www.lagou.com/jobs/positionAjax.json?px=default&city=%s&needAddtionalResult=false" % city
                referer_url = "https://www.lagou.com/jobs/list_python/p-city_%s?px=default" % self.city_dict[city]
                self.headers["Referer"] = referer_url
                # self.headers["Referer"] = referer_url.encode("utf8")
                response = self.handle_request(method="POST", url=page_url, data=data, info=city)
                lagou_data = json.loads(response)
                job_list = lagou_data["content"]["positionResult"]["result"]
                pprint.pprint(job_list)
                # for job in job_list:
                #     # lagou_mysql.insert_item(job)
                #     pass


    def handle_request(self, method, url, data=None, info=None):
        while True:
            if method == "GET":
                response = self.lagou_session.get(url=url, headers=self.headers)
            elif method == "POST":
                response = self.lagou_session.post(url=url, headers=self.headers, data=data)
            response.encoding = "utf8"
            if "频繁" in response.text:
                print(response.text)
                # 需要先清除cookies信息 然后在重新获取cookies信息
                self.lagou_session.cookies.clear()
                first_request_url = "https://www.lagou.com/jobs/list_python/p-city_%s?px=default" % self.city_dict[info]
                self.handle_request(method="GET", url=first_request_url)
                time.sleep(10)
                continue
            return response.text


if __name__ == '__main__':
    lagou = HandleLaGou()
    lagou.handle_city_code()
    # pool = multiprocessing.Pool(5)
    # city_list = list(set(lagou.city_name_list))
    city_list = ["宁波", "常州", "沈阳", "石家庄", "昆明", "南昌",
                 "南宁", "哈尔滨", "海口", "中山", "惠州", "贵阳", "长春", "太原", "嘉兴", "泰安", "昆山", "烟台", "兰州", "泉州"]

    for city_name in city_list:
        lagou.handle_city(city_name)
        # pool.apply_async(lagou.handle_city, args=(city_name,))
    # pool.close()  # 关闭进程池，关闭后pool不再接受新的任务请求
    # pool.join()  # 等待子进程结束