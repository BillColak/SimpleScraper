import scrapy
from scrapy.crawler import CrawlerProcess
from quotes_spider.items import SpiderItemLoader
from scrapy import Request
from scrapy.shell import inspect_response
import re
from functools import partial
from test_data import my_data

# TODO xpaths must be changed from full

# scrapy parse --spider=simple_spider -c parse_item https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html
# scrapy parse --spider=simple_spider -c pagination https://books.toscrape.com/
# https://stackoverflow.com/questions/16909106/scrapyin-a-request-fails-eg-404-500-how-to-ask-for-another-alternative-reque?noredirect=1&lq=1


DEBUG = False
allowed_domains = ['books.toscrape.com']
start_urls = ['http://books.toscrape.com/']

file_format = 'csv'
uri = 'test.csv'

# parse_link_xpath = '//h3/a/@href'
# pagination_xpath = '//a[text()="next"]/@href'
# output_iter_xpath = {'title': '//h1/text()', 'price': '//p[normalize-space(@class)="price_color"]/text()'}
# command = {'parse_link_xpath': ""}
# combodict = {'Item': 1, 'Multi-Item': 2, 'Pagination': 3, 'Follow-Link': 4, 'Follow-All-Links': 5}


def get_numbers(value):
    if value:
        number = re.search(r'\d+\.\d+', value)
        return float(number.group())


class SimpleSpider(scrapy.Spider):
    # name = 'simple_spider'

    def __init__(self, *args, **kwargs):
        super(SimpleSpider, self).__init__(*args, **kwargs)

        # self.allowed_domains = allowed_domains
        # self.start_urls = start_urls

    def parse(self, response, **kwargs):
        """This function must yield a request or an item object. Also there is no purpose for the kwargs
        they are just there to look pretty. Whoever wrote this library is a fucking dumbass."""
        # pass
        pagination = None
        follow_all_links_path = None
        item_dict = dict()

        for row in my_data:
            if row['comboIndex'] == 2:
                pagination = row['xpath']

            if row['comboIndex'] == 4:
                follow_all_links_id = row['unique_id']
                follow_all_links_path = row['xpath']

                for items in my_data:
                    if follow_all_links_id == items['parent_id']:
                        item_dict[items.get('column_name', None)] = items.get('xpath', None)

        if follow_all_links_path:
            for i in self.parse_link(response, follow_link=follow_all_links_path, **item_dict):
                yield i

        if pagination:
            yield self.pagination(response, page=pagination)

    def parse_link(self, response, follow_link=None, **kwargs):
        if follow_link:
            urls = response.xpath(follow_link).getall()
            for url in urls:
                yield response.follow(
                    url=response.urljoin(url),
                    callback=partial(self.parse_item, **kwargs)
                )

    def pagination(self, response, page=None):
        if page:
            next_page_url = response.xpath(page).extract_first()
            absolute_next_page_url = response.urljoin(next_page_url)
            return Request(absolute_next_page_url)

    def parse_item(self, response, **kwargs):
        loader = SpiderItemLoader(response=response)
        for column, value in kwargs.items():
            loader.add_value(column, response.xpath(value).get())
        yield loader.load_item()


class SpiderRunner(SimpleSpider):
    name = 'simple_spider'

    custom_settings = {
        'FEED_FORMAT': 'csv',
        'FEED_URI': 'test.csv'
    }

    def __init__(self, *args, **kwargs):
        super(SpiderRunner, self).__init__(*args, **kwargs)
        self.allowed_domains = allowed_domains
        self.start_urls = start_urls
        # self.executioner = partial(self.parse, **output_iter_xpath)
        # self.parse_link()
        # self.pagination()
        # self.parse_item()
        # item types


if __name__ == '__main__':
    process = CrawlerProcess()
    process.crawl(SpiderRunner)
    process.start()


