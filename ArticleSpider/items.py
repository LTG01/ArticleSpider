# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
import re
import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose,Join,TakeFirst,Identity
import datetime
from ArticleSpider.utils.common import *
from w3lib.html import remove_tags
from ArticleSpider.settings import SQL_DATETIME_FORMAT, SQL_DATE_FORMAT


class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

def date_convert(value):
    match_re = re.match(".*?(\d+.*)", value)
    if match_re:
        return match_re.group(1)
    else:
        return "0000-00-00"


def get_nums(value):
    match_re = re.match(".*?(\d+).*", value)
    if match_re:
        nums = int(match_re.group(1))
    else:
        nums = 0

    return nums

class ArticleItemLoader(ItemLoader):
    #自定义itemloader
    default_output_processor = TakeFirst()
class JobBoleArticleItem(scrapy.Item):
    title = scrapy.Field()
    create_date = scrapy.Field(
        input_processor=MapCompose(date_convert)
    )
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    front_image_url = scrapy.Field(
        # input_processor = MapCompose(add_author, add_test), # 测试用
        output_processor=Identity()
    )
    front_image_path = scrapy.Field()
    praise_nums = scrapy.Field()
    comment_nums = scrapy.Field()
    fav_nums = scrapy.Field()
    tags = scrapy.Field(
        output_processor=Join(separator=",")
    )
    content = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
                insert into cnblog_article
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE content=VALUES(fav_nums)
            """
        params = (
            self.get("title", ""),
            self.get("url", ""),
            self.get("url_object_id", ""),
            self.get("front_image_path", ""),
            self.get("front_image_url", ""),
            self.get("parise_nums", 0),
            self.get("comment_nums", 0),
            self.get("fav_nums", 0),
            self.get("tags", ""),
            self.get("content", ""),
            self.get("create_date", "0000-00-00"),
        )

        return insert_sql, params


class ZhihuQuestionItem(scrapy.Item):
    #知乎的问题 item
    zhihu_id = scrapy.Field()
    topics = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    answer_num = scrapy.Field()
    comments_num = scrapy.Field()
    watch_user_num = scrapy.Field()
    click_num = scrapy.Field()
    crawl_time = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        #插入知乎question表的sql语句 zhihu_question
        insert_sql = """
            insert into zhihu_question(zhihu_id, topics, url, title, content, answer_num, comments_num,
              watch_user_num, click_num, crawl_time
              )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE content=VALUES(content), answer_num=VALUES(answer_num), comments_num=VALUES(comments_num),
              watch_user_num=VALUES(watch_user_num), click_num=VALUES(click_num)
        """
        zhihu_id = self["zhihu_id"][0]
        topics = ",".join(self["topics"])
        url = self["url"][0]
        title = "".join(self["title"])
        content = "".join(self["content"])
        answer_num = extract_num("".join(self["answer_num"]))
        comments_num = extract_num("".join(self["comments_num"]))

        if len(self["watch_user_num"]) == 2:
            watch_user_num = int(self["watch_user_num"][0].replace(',', ''))
            click_num = int(self["watch_user_num"][1].replace(',', ''))
        else:
            watch_user_num = int(self["watch_user_num"][0].replace(',', ''))
            click_num = 0

        crawl_time = datetime.datetime.now().strftime(SQL_DATETIME_FORMAT)

        params = (zhihu_id, topics, url, title, content, answer_num, comments_num,
                  watch_user_num, click_num, crawl_time)

        return insert_sql, params

class ZhihuAnswerItem(scrapy.Item):
    #知乎的问题回答item
    zhihu_id = scrapy.Field()
    url = scrapy.Field()
    question_id = scrapy.Field()
    author_id = scrapy.Field()
    content = scrapy.Field()
    parise_num = scrapy.Field()
    comments_num = scrapy.Field()
    create_time = scrapy.Field()
    update_time = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        #插入知乎question表的sql语句
        insert_sql = """
            insert into zhihu_answer(zhihu_id, url, question_id, author_id, content, parise_num, comments_num,
              create_time, update_time, crawl_time
              ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
              ON DUPLICATE KEY UPDATE content=VALUES(content), comments_num=VALUES(comments_num), parise_num=VALUES(parise_num),
              update_time=VALUES(update_time)
        """

        create_time = datetime.datetime.fromtimestamp(self["create_time"]).strftime(SQL_DATETIME_FORMAT)
        update_time = datetime.datetime.fromtimestamp(self["update_time"]).strftime(SQL_DATETIME_FORMAT)

        # create_time = '2020-08-04 18:52:24'
        # update_time = '2020-08-04 18:52:24'


        params = (
            self["zhihu_id"], self["url"], self["question_id"],
            self["author_id"], self["content"], self["parise_num"],
            self["comments_num"], create_time, update_time,
            datetime.datetime.now().strftime(SQL_DATETIME_FORMAT),
        )

        return insert_sql, params



def remove_splash(value):
    #去掉工作城市的斜线
    return value.replace("/","")

def handle_jobaddr(value):
    addr_list = value.split("\n")
    addr_list = [item.strip() for item in addr_list if item.strip()!="查看地图"]
    return "".join(addr_list)

class LagouJobItemLoader(ItemLoader):
    #自定义itemloader
    default_output_processor = TakeFirst()


class LagouJobItem1(scrapy.Item):
    #拉勾网职位信息
    title = scrapy.Field()
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    salary = scrapy.Field()
    job_city = scrapy.Field(

    )
    work_years = scrapy.Field(

    )
    degree_need = scrapy.Field(

    )
    job_type = scrapy.Field()
    publish_time = scrapy.Field()
    job_advantage = scrapy.Field()
    job_desc = scrapy.Field()
    job_addr = scrapy.Field(

    )
    company_name = scrapy.Field()
    company_url = scrapy.Field()
    tags = scrapy.Field(

    )
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
            insert into lagou_job(title, url, url_object_id, salary, job_city, work_years, degree_need,
            job_type, publish_time, job_advantage, job_desc, job_addr, company_name, company_url,
            tags, crawl_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE salary=VALUES(salary), job_desc=VALUES(job_desc)
        """
        params = (
            self.get("title", ""),
            self.get("url", ""),
            self.get("url_object_id", ""),
            self.get("salary", ""),
            self.get("job_city", ""),
            self.get("work_years", ""),
            self.get("degree_need", ""),
            self.get("job_type", ""),
            self.get("publish_time", "0000-00-00"),
            self.get("job_advantage", ""),
            self.get("job_desc", ""),
            self.get("job_addr", ""),
            self.get("company_name", ""),
            self.get("company_url", ""),
            self.get("job_addr", ""),
            self["crawl_time"].strftime(SQL_DATETIME_FORMAT),
        )

        return insert_sql, params

    # def save_to_es(self):
    #     job = LagouJobType()
    #     job.title = self.get('title', '')
    #     job.create_date = self.get("create_date", "")
    #     job.url = self.get("url")
    #     job.tags = self.get("tags", "")
    #     job.salary = self.get("salary", "")
    #     job.job_city = self.get("job_city", "")
    #     job.work_years = self.get("work_years", "")
    #     job.degree_need = self.get("degree_need", "")
    #     job.job_type = self.get("job_type", "")
    #     job.publish_time = self.get("publish_time", "")
    #     job.job_advantage = self.get("job_advantage", "")
    #     job.job_addr = self.get("job_addr", "")
    #     job.job_desc = self.get("job_desc", "")
    #     job.company_name = self.get("company_name", "")
    #     job.company_url = self.get("company_url", "")
    #     job.meta.id = self["url_object_id"]
    #
    #     job.suggest = gen_suggests(ArticleType._doc_type.index, ((job.title,10),(job.tags, 7)))
    #
    #     job.save()
    #
    #     redis_cli.incr("lagou_count")

class LagouJobItem(scrapy.Item):
    #拉勾网职位信息
    title = scrapy.Field()
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    salary = scrapy.Field()
    job_city = scrapy.Field(
        input_processor=MapCompose(remove_splash),
    )
    work_years = scrapy.Field(
        input_processor = MapCompose(remove_splash),
    )
    degree_need = scrapy.Field(
        input_processor = MapCompose(remove_splash),
    )
    job_type = scrapy.Field()
    publish_time = scrapy.Field()
    job_advantage = scrapy.Field()
    job_desc = scrapy.Field()
    job_addr = scrapy.Field(
        input_processor=MapCompose(remove_tags, handle_jobaddr),
    )
    company_name = scrapy.Field()
    company_url = scrapy.Field()
    tags = scrapy.Field(
        input_processor = Join(",")
    )
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
            insert into lagou_job(title, url, url_object_id, salary, job_city, work_years, degree_need,
            job_type, publish_time, job_advantage, job_desc, job_addr, company_name, company_url,
            tags, crawl_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE salary=VALUES(salary), job_desc=VALUES(job_desc)
        """
        params = (
            self.get("title", ""),
            self.get("url", ""),
            self.get("url_object_id", ""),
            self.get("salary", ""),
            self.get("job_city", ""),
            self.get("work_years", ""),
            self.get("degree_need", ""),
            self.get("job_type", ""),
            self.get("publish_time", "0000-00-00"),
            self.get("job_advantage", ""),
            self.get("job_desc", ""),
            self.get("job_addr", ""),
            self.get("company_name", ""),
            self.get("company_url", ""),
            self.get("job_addr", ""),
            # self["crawl_time"].strftime(SQL_DATETIME_FORMAT),
            datetime.datetime.now().strftime(SQL_DATETIME_FORMAT),
        )

        return insert_sql, params

    # def save_to_es(self):
    #     job = LagouJobType()
    #     job.title = self.get('title', '')
    #     job.create_date = self.get("create_date", "")
    #     job.url = self.get("url")
    #     job.tags = self.get("tags", "")
    #     job.salary = self.get("salary", "")
    #     job.job_city = self.get("job_city", "")
    #     job.work_years = self.get("work_years", "")
    #     job.degree_need = self.get("degree_need", "")
    #     job.job_type = self.get("job_type", "")
    #     job.publish_time = self.get("publish_time", "")
    #     job.job_advantage = self.get("job_advantage", "")
    #     job.job_addr = self.get("job_addr", "")
    #     job.job_desc = self.get("job_desc", "")
    #     job.company_name = self.get("company_name", "")
    #     job.company_url = self.get("company_url", "")
    #     job.meta.id = self["url_object_id"]
    #
    #     job.suggest = gen_suggests(ArticleType._doc_type.index, ((job.title,10),(job.tags, 7)))
    #
    #     job.save()
    #
    #     redis_cli.incr("lagou_count")

