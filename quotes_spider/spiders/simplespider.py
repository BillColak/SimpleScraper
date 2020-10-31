import scrapy
from scrapy.crawler import CrawlerProcess
from quotes_spider.items import SpiderItemLoader
from scrapy import Request
from scrapy.shell import inspect_response
import re

# scrapy parse --spider=simplespider -c parse_item https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html
# https://docs.scrapy.org/en/latest/topics/loaders.html

DEBUG = False
allowed_domains = ['books.toscrape.com']
start_urls = ['http://books.toscrape.com/']
file_format = 'csv'
uri = 'test.csv'


def get_numbers(value):
    if value:
        number = re.search(r'\d+\.\d+', value)
        return float(number.group())


def test_func(val):
    print(val)
    return val


class SimpleSpider(scrapy.Spider):

    name = 'simple_spider'

    custom_settings = {
        'FEED_FORMAT': file_format,
        'FEED_URI': uri
    }

    def __init__(self, *args, **kwargs):
        super(SimpleSpider, self).__init__(*args, **kwargs)

        self.allowed_domains = allowed_domains
        self.start_urls = start_urls
        self.func_dict = {1: self.parse_link, 2: self.parse_item}
        # so depending on combobox callback in parse will be decided

    def parse(self, response, **kwargs):
        # title = response.css('h1::text').get()
        # price = get_numbers(response.css('.price_color::text').get())
        # test_func((title, price))

        if DEBUG:
            inspect_response(response, self)
        else:
            urls = response.css('h3 a::attr(href)').getall()
            for url in urls:
                yield response.follow(  # this assumes that a item is being hopped.
                    url,
                    # callback=self.parse_link,
                    callback=self.parse_item,
                )

            next_page_url = response.xpath('//a[text()="next"]/@href').extract_first()
            absolute_next_page_url = response.urljoin(next_page_url)
            pagination = Request(absolute_next_page_url)
            yield pagination

    def parse_link(self, response):
        if DEBUG:
            inspect_response(response, self)
        else:
            urls = response.css('.image_container a::attr(href)').getall()
            for url in urls:
                yield response.follow(
                    url=response.urljoin(url),
                    callback=self.parse_item,
                )

    def parse_item(self, response):
        if DEBUG:
            inspect_response(response, self)
        else:
            title = response.css('h1::text').get()
            price = get_numbers(response.css('.price_color::text').get())
            loader = SpiderItemLoader(response=response)
            loader.add_value('title', title)
            loader.add_value('price', price)
            yield loader.load_item()


if __name__ == '__main__':
    process = CrawlerProcess()
    process.crawl(SimpleSpider)
    process.start()
