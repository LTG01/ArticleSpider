import scrapy
from urllib import parse
from scrapy import Request
import re
import json
from ArticleSpider.items import JobBoleArticleItem,ArticleItemLoader
from ArticleSpider.utils import common


class CnblogsSpider(scrapy.Spider):
    name = 'cnblog'
    allowed_domains = ['news.cnblogs.com']
    start_urls = ['https://news.cnblogs.com/']

    def parse(self, response):
        #news_block
        post_nodes = response.css('#news_list .news_block')
        for node in post_nodes:
            img_url = node.css('.entry_summary a img::attr(src)').extract_first('')
            post_url = node.css('h2.news_entry a::attr(href)').extract_first('')
            yield Request(url=parse.urljoin(response.url,post_url),meta={"front_image_url":img_url},callback=self.parse_detail)

        #下一页
        # next_url = response.xpath('//div[@class="pager"]//a[contains(text(),"Next >")]/@href').extract_first("")
        # yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)

    def parse_detail(self, response):
        match_re = re.match(".*?(\d+)", response.url)
        if match_re:
            post_id = match_re.group(1)
            # article_item = JobBoleArticleItem()
            # title = response.css('#news_title a::text').extract_first('')
            # create_date = response.css('#news_info .time::text').extract_first('')
            # match_re = re.match(".*?(\d+.*)", create_date)
            # if match_re:
            #     create_date = match_re.group(1)
            # content = response.css('#news_content').extract()[0]
            # tag_list = response.css('.news_tags a::text').extract()
            # tags = '，'.join(tag_list)
            #
            # article_item["title"] = title
            # article_item["create_date"] = create_date
            # article_item["content"] = content
            # article_item["tags"] = tags
            # img_url = response.meta.get('front_image_url',"")
            # if img_url:
            #     if img_url.startswith('http'):
            #         article_item["front_image_url"] = [img_url]
            #     else:
            #         article_item["front_image_url"] = ["https:"+img_url]
            # article_item["url"] = response.url

            item_loader = ArticleItemLoader(item=JobBoleArticleItem(), response=response)
            item_loader.add_css("title", "#news_title a::text")
            item_loader.add_css("create_date", "#news_info .time::text")
            item_loader.add_css("content", "#news_content")
            item_loader.add_css("tags", ".news_tags a::text")
            item_loader.add_value("url", response.url)
            img_url = response.meta.get('front_image_url', "")
            if img_url:
                if img_url.startswith('http'):
                    item_loader.add_value("front_image_url", [img_url])
                else:
                    item_loader.add_value("front_image_url", ["https:"+img_url])
            yield Request(url=parse.urljoin(response.url, f'/NewsAjax/GetAjaxNewsInfo?contentId={post_id}'),

                          meta={'article_item' : item_loader,'url':response.url},
                          callback=self.parse_nums)

    def parse_nums(self, response):
        j_data = json.loads(response.text)
        item_loader = response.meta.get("article_item", "")

        praise_nums = j_data["DiggCount"]
        fav_nums = j_data["TotalView"]
        comment_nums = j_data["CommentCount"]

        item_loader.add_value("praise_nums", j_data["DiggCount"])
        item_loader.add_value("fav_nums", j_data["TotalView"])
        item_loader.add_value("comment_nums", j_data["CommentCount"])
        item_loader.add_value("url_object_id", common.get_md5(response.meta.get("url", "")))
        '''
        article_item["praise_nums"] = praise_nums
        article_item["fav_nums"] = fav_nums
        article_item["comment_nums"] = comment_nums
        article_item["url_object_id"] = common.get_md5(article_item["url"])
        '''

        article_item = item_loader.load_item()

        yield article_item
