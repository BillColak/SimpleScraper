my_data = [
    {'unique_id': 2, 'parent_id': 1, 'column_name': 'follow_link', 'url_name': 'https://books.toscrape.com/', 'xpath': '//h3/a/@href', 'value': 'A Light in the ...', 'link': 'https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html', 'class_name': '', 'image_link': '', 'local_name': 'a', 'parent_name': 'h3', 'attributes': {'href': 'catalogue/a-light-in-the-attic_1000/index.html', 'title': 'A Light in the Attic'}, 'comboIndex': 4},
    {'unique_id': 3, 'parent_id': 2, 'column_name': 'title', 'url_name': 'https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html', 'xpath': '//h1/text()', 'value': 'A Light in the Attic', 'link': '', 'class_name': '', 'image_link': '', 'local_name': 'h1', 'parent_name': 'div', 'attributes': None, 'comboIndex': 0},
    {'unique_id': 4, 'parent_id': 2, 'column_name': 'price', 'url_name': 'https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html', 'xpath': '//p[normalize-space(@class)="price_color"]/text()', 'value': '£51.77', 'link': '', 'class_name': 'price_color', 'image_link': '', 'local_name': 'p', 'parent_name': 'div', 'attributes': {'class': 'price_color'}, 'comboIndex': 0},
    {'unique_id': 5, 'parent_id': 1, 'column_name': 'next page', 'url_name': 'https://books.toscrape.com/', 'xpath': '//a[text()="next"]/@href', 'value': 'next', 'link': 'https://books.toscrape.com/catalogue/page-2.html', 'class_name': '', 'image_link': '', 'local_name': 'a', 'parent_name': 'li', 'attributes': {'href': 'catalogue/page-2.html'}, 'comboIndex': 2},
]

my_data_full_path = [
    {'unique_id': 2, 'parent_id': 1, 'column_name': 'follow_link', 'url_name': 'https://books.toscrape.com/', 'xpath': '/html/body/div/div/div/div/section/div[2]/ol/li[1]/article/h3/a', 'value': 'A Light in the ...', 'link': 'https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html', 'class_name': '', 'image_link': '', 'local_name': 'a', 'parent_name': 'h3', 'attributes': {'href': 'catalogue/a-light-in-the-attic_1000/index.html', 'title': 'A Light in the Attic'}, 'comboIndex': 4},
    {'unique_id': 3, 'parent_id': 2, 'column_name': 'title', 'url_name': 'https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html', 'xpath': '/html/body/div/div/div[2]/div[2]/article/div[1]/div[2]/h1', 'value': 'A Light in the Attic', 'link': '', 'class_name': '', 'image_link': '', 'local_name': 'h1', 'parent_name': 'div', 'attributes': None, 'comboIndex': 0},
    {'unique_id': 4, 'parent_id': 2, 'column_name': 'price', 'url_name': 'https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html', 'xpath': '/html/body/div/div/div[2]/div[2]/article/div[1]/div[2]/p[1]', 'value': '£51.77', 'link': '', 'class_name': 'price_color', 'image_link': '', 'local_name': 'p', 'parent_name': 'div', 'attributes': {'class': 'price_color'}, 'comboIndex': 0},
    {'unique_id': 5, 'parent_id': 1, 'column_name': 'next page', 'url_name': 'https://books.toscrape.com/', 'xpath': '/html/body/div/div/div/div/section/div[2]/div/ul/li[2]/a', 'value': 'next', 'link': 'https://books.toscrape.com/catalogue/page-2.html', 'class_name': '', 'image_link': '', 'local_name': 'a', 'parent_name': 'li', 'attributes': {'href': 'catalogue/page-2.html'}, 'comboIndex': 2},
]

craigs_list = [
    {'unique_id': 2, 'parent_id': 1, 'column_name': 'next page',
     'url_name': 'https://vancouver.craigslist.org/search/cto?query=honda',
     'xpath': '/html/body/section/form/div[3]/div[3]/span[2]/a[3]',
     'value': 'next >',
     'link': 'https://vancouver.craigslist.org/d/cars-trucks-by-owner/search/cto?s=120', 'class_name': 'button next',
     'image_link': '', 'local_name': 'a', 'parent_name': 'span',
     'attributes': {'href': '/d/cars-trucks-by-owner/search/cto?s=120', 'class': 'button next', 'title': 'next page'},
     'QItem': '< PyQt5.QtGui.QStandardItem object at 0x1328C6E8 >', 'comboIndex': 2},

    {'unique_id': 3, 'parent_id': 1, 'column_name': 'follow', 'url_name': 'https://vancouver.craigslist.org/search/cto?query=honda',
     'xpath': '/html/body/section/form/div[4]/ul/li[1]/div/h3/a',
     'value': '2007 Cadillac Escalade',
     'link': 'https://vancouver.craigslist.org/rds/cto/d/langley-city-2007-cadillac-escalade/7227213444.html',
     'class_name': 'result-title hdrlnk', 'image_link': '', 'local_name': 'a', 'parent_name': 'h3', 'attributes': {
        'href': 'https://vancouver.craigslist.org/rds/cto/d/langley-city-2007-cadillac-escalade/7227213444.html',
        'data-id': '7227213444', 'class': 'result-title hdrlnk', 'id': 'postid_7227213444'}, 'QItem'
     : '< PyQt5.QtGui.QStandardItemobjectat0x1328C898 >', 'comboIndex': 4},

    {'unique_id': 4, 'parent_id': 3, 'column_name': 'title',
     'url_name': 'https://vancouver.craigslist.org/rds/cto/d/langley-city-2007-cadillac-escalade/7227213444.html',
     'xpath': '/html/body/section/section/section/div[1]/p[1]/span/b',
     'value': '2007 cadillac escalade', 'link': '',
     'class_name': '', 'image_link': '', 'local_name': 'b', 'parent_name': 'span', 'attributes': None, 'QItem'
     : '< PyQt5.QtGui.QStandardItemobjectat0x1328CA48 >', 'comboIndex': 0},

    {'unique_id': 5, 'parent_id': 3, 'column_name': 'condition',
     'url_name': 'https://vancouver.craigslist.org/rds/cto/d/langley-city-2007-cadillac-escalade/7227213444.html',
     'xpath': '/html/body/section/section/section/div[1]/p[2]/span[1]/b',
     'value': 'excellent', 'link': '',
     'class_name': '', 'image_link': '', 'local_name': 'b', 'parent_name': 'span', 'attributes': None, 'QItem'
     : '< PyQt5.QtGui.QStandardItemobjectat0x1328CB20 >', 'comboIndex': 0}
]

BOOKS = [
    {'unique_id': 2, 'parent_id': 1, 'column_name': 'FOLLOW', 'url_name': 'https://books.toscrape.com/', 'xpath': '/html/body/div/div/div/div/section/div[2]/ol/li[1]/article/h3/a', 'value': 'A Light in the ...', 'link': 'https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html', 'class_name': '', 'image_link': '', 'local_name': 'a', 'parent_name': 'h3', 'attributes': {'href': 'catalogue/a-light-in-the-attic_1000/index.html', 'title': 'A Light in the Attic'}, 'QItem': '<PyQt5.QtGui.QStandardItem object at 0x04D4C778>', 'object_id': 81053560, 'comboIndex': 4},
    {'unique_id': 3, 'parent_id': 2, 'column_name': 'TITLE', 'url_name': 'https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html', 'xpath': '/html/body/div/div/div[2]/div[2]/article/div[1]/div[2]/h1', 'value': 'A Light in the Attic', 'link': '', 'class_name': '', 'image_link': '', 'local_name': 'h1', 'parent_name': 'div', 'attributes': None, 'QItem': '<PyQt5.QtGui.QStandardItem object at 0x04D4C8E0>', 'object_id': 81053920, 'comboIndex': 0},
    {'unique_id': 4, 'parent_id': 2, 'column_name': 'PRICE', 'url_name': 'https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html', 'xpath': '/html/body/div/div/div[2]/div[2]/article/div[1]/div[2]/p[1]', 'value': '£51.77', 'link': '', 'class_name': 'price_color', 'image_link': '', 'local_name': 'p', 'parent_name': 'div', 'attributes': {'class': 'price_color'}, 'QItem': '<PyQt5.QtGui.QStandardItem object at 0x04D4CA00>', 'object_id': 81054208, 'comboIndex': 0},
    {'unique_id': 5, 'parent_id': 2, 'column_name': 'STOCK', 'url_name': 'https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html', 'xpath': '/html/body/div/div/div[2]/div[2]/article/table/tbody/tr[6]/td', 'value': 'In stock (22 available)', 'link': '', 'class_name': '', 'image_link': '', 'local_name': 'td', 'parent_name': 'tr', 'attributes': None, 'QItem': '<PyQt5.QtGui.QStandardItem object at 0x04D4CBB0>', 'object_id': 81054640, 'comboIndex': 0},
    {'unique_id': 6, 'parent_id': 2, 'column_name': 'TAX', 'url_name': 'https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html', 'xpath': '/html/body/div/div/div[2]/div[2]/article/table/tbody/tr[5]/td', 'value': '£0.00', 'link': '', 'class_name': '', 'image_link': '', 'local_name': 'td', 'parent_name': 'tr', 'attributes': None, 'QItem': '<PyQt5.QtGui.QStandardItem object at 0x04D4CD60>', 'object_id': 81055072, 'comboIndex': 0},
    {'unique_id': 7, 'parent_id': 1, 'column_name': 'PAGINATION', 'url_name': 'https://books.toscrape.com/', 'xpath': '/html/body/div/div/div/div/section/div[2]/div/ul/li[2]/a', 'value': 'next', 'link': 'https://books.toscrape.com/catalogue/page-2.html', 'class_name': '', 'image_link': '', 'local_name': 'a', 'parent_name': 'li', 'attributes': {'href': 'catalogue/page-2.html'}, 'QItem': '<PyQt5.QtGui.QStandardItem object at 0x04D4CEC8>', 'object_id': 81055432, 'comboIndex': 2},
]

