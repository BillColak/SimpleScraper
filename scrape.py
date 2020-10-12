import requests
from lxml import html as lxml_html

# //a[normalize-space(@class)='result-title hdrlnk']/@href

header = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                        'Chrome/85.0.4183.121 Safari/537.36'}

# url_name = 'https://vancouver.craigslist.org/search/cto'  # craigslist
url_name = 'https://www.kijiji.ca/b-cars-trucks/calgary/new__used/c174l1700199a49'  # kijiji
# item_path = '/html/body/section/form/div[4]/ul/li[1]/div/h2/a'  # craigslist
item_path = '/html/body/div[3]/div[3]/div[3]/div[3]/div[3]/div[4]/div[1]/div[2]/div/div[2]/a'  # kijiji

resp = requests.get(url=url_name, headers=header)


def xpath_root(page_source) -> lxml_html.HtmlElement:
    return lxml_html.fromstring(html=page_source)


el_src = xpath_root(resp.content)


def return_element_list_by_xpath(element_source: lxml_html.HtmlElement, xpath_expression: str, attribute=None) -> list:
    expression_list = []

    if attribute is not None:
        xpath_expression = xpath_expression + attribute

    expression = element_source.xpath(xpath_expression)
    for item in expression:
        if isinstance(item, lxml_html.HtmlElement):
            expression_list.append(str(lxml_html.tostring(item, pretty_print=True, with_tail=False), 'utf-8'))
        else:
            expression_list.append(item)
    return expression_list


# //a[normalize-space(@class)='result-title hdrlnk']/@href
def xpath_intellisense(tag, class_text, attrib):
    return f"//{tag}[normalize-space(@class)='{class_text}']/{attrib}"


def single_item(level, class_text, attrib, path_item):
    path_item = str(path_item).split('/')
    if int(level) > 0:
        depth = "/".join(path_item[int(level):])
        return "//" + depth + f"[normalize-space(@class)='{class_text}']/{attrib}"


# does not work for kijiji
item_class = return_element_list_by_xpath(el_src, item_path, attribute='//@class')
item_href = return_element_list_by_xpath(el_src, item_path, attribute='//@href')
item_text = return_element_list_by_xpath(el_src, item_path, attribute='/text()')
print(item_class, item_href, item_text)


# -----------craigslist-----------
# href_xpath = xpath_intellisense('a', 'result-title hdrlnk', '@href')  # href
# href_list = el_src.xpath(href_xpath)  # href
# text_xpath = xpath_intellisense('a', 'result-title hdrlnk', 'text()')  # text
# text_list = el_src.xpath(text_xpath)  # text

# -----------kijiji-----------
href_xpath = xpath_intellisense('a', 'title', '@href')  # href
href_list = el_src.xpath(href_xpath)  # href
text_xpath = xpath_intellisense('a', 'title', 'text()')  # text
text_list = el_src.xpath(text_xpath)  # text

single_text_item_xpath = single_item(6, 'title', 'text()', item_path)
single_text_item = el_src.xpath(single_text_item_xpath)
print(single_text_item_xpath, single_text_item[0].strip())

print(len(href_list), len(text_list))

