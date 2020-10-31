import scrapy
from scrapy.crawler import CrawlerProcess
# from quotes_spider.quotes_spider.spiders import books_copy
# books_copy.pagination = False

# class PostsSpider(scrapy.Spider):
#     name = "posts"
#
#     start_urls = [
#         'https://blog.scrapinghub.com/'
#     ]
#
#     def parse(self, response):
#         for post in response.css('div.post-item'):
#             yield {
#                 'title': post.css('.post-header h2 a::text')[0].get(),
#                 'date': post.css('.post-header a::text')[1].get(),
#                 'author': post.css('.post-header a::text')[2].get()
#             }
#         next_page = response.css('a.next-posts-link::attr(href)').get()
#         if next_page is not None:
#             next_page = response.urljoin(next_page)
#             yield scrapy.Request(next_page, callback=self.parse)

# import scrapy
#
#
# class PostsSpider(scrapy.Spider):
#     name = "posts"
#
#     start_urls = [
#         'https://blog.scrapinghub.com/'
#     ]
#
#     def parse(self, response):
#         for post in response.css('div.post-item'):
#             yield {
#                 'title': post.css('.post-header h2 a::text')[0].get(),
#                 'date': post.css('.post-header a::text')[1].get(),
#                 'author': post.css('.post-header a::text')[2].get()
#             }
#         next_page = response.css('a.next-posts-link::attr(href)').get()
#         if next_page is not None:
#             next_page = response.urljoin(next_page)
#             yield scrapy.Request(next_page, callback=self.parse)


class QuotesSpider(scrapy.Spider):
    name = "quotes"

    def start_requests(self):
        urls = [
            'http://quotes.toscrape.com/page/1/',
            'http://quotes.toscrape.com/page/2/',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        page = response.url.split("/")[-2]
        filename = f'quotes-{page}.html'
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log(f'Saved file {filename}')

if __name__ == '__main__':
    process = CrawlerProcess()
    # process.crawl(PostsSpider)
    process.crawl(QuotesSpider)
    process.start()
