import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from quotes_spider.spiders.simplespider import SimpleSpider

process = CrawlerProcess(settings=get_project_settings())
process.crawl(SimpleSpider)
process.start()
