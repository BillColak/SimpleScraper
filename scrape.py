import requests
from lxml import html as lxml_html
from string import Template

# //a[normalize-space(@class)='result-title hdrlnk']/@href

header = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                        'Chrome/85.0.4183.121 Safari/537.36'}

# url_name = 'https://vancouver.craigslist.org/search/cto'  # craigslist
# url_name = 'https://www.kijiji.ca/b-cars-trucks/calgary/new__used/c174l1700199a49'  # kijiji
# item_path = '/html/body/section/form/div[4]/ul/li[1]/div/h2/a'  # craigslist
# item_path = '/html/body/div[3]/div[3]/div[3]/div[3]/div[3]/div[4]/div[1]/div[2]/div/div[2]/a'  # kijiji

# resp = requests.get(url=url_name, headers=header)


# def resp(url):
#     return requests.get(url=url, headers=header).content
#
#
# def xpath_root(page_source) -> lxml_html.HtmlElement:
#     return lxml_html.fromstring(html=page_source)


# el_src = xpath_root(resp.content)


# //a[normalize-space(@class)='result-title hdrlnk']/@href
# def xpath_intellisense(tag, class_text, attrib):
#     return f"//{tag}[normalize-space(@class)='{class_text}']/{attrib}"
#
#
# def single_item(level, class_text, attrib, path_item):
#     path_item = str(path_item).split('/')
#     if int(level) > 0:
#         depth = "/".join(path_item[int(level):])
#         return "//" + depth + f"[normalize-space(@class)='{class_text}']/{attrib}"
#
#
# # does not work for kijiji
# item_class = return_element_list_by_xpath(el_src, item_path, attribute='//@class')
# item_href = return_element_list_by_xpath(el_src, item_path, attribute='//@href')
# item_text = return_element_list_by_xpath(el_src, item_path, attribute='/text()')
# print(item_class, item_href, item_text)


# -----------craigslist-----------
# href_xpath = xpath_intellisense('a', 'result-title hdrlnk', '@href')  # href
# href_list = el_src.xpath(href_xpath)  # href
# text_xpath = xpath_intellisense('a', 'result-title hdrlnk', 'text()')  # text
# text_list = el_src.xpath(text_xpath)  # text

# -----------kijiji-----------
# href_xpath = xpath_intellisense('a', 'title', '@href')  # href
# href_list = el_src.xpath(href_xpath)  # href
# text_xpath = xpath_intellisense('a', 'title', 'text()')  # text
# text_list = el_src.xpath(text_xpath)  # text
#
# single_text_item_xpath = single_item(6, 'title', 'text()', item_path)
# single_text_item = el_src.xpath(single_text_item_xpath)
# print(single_text_item_xpath, single_text_item[0].strip())
# print(len(href_list), len(text_list))


# TODO: Scraping Standards:
#  1) The JS query must reflect the Xpath not the other way around.
#  2) The scraper is used in two places: Intellisense and the main scraper.
#      2.1)If combobox selection does not match the the data type give error.

def resp(url):
    return requests.get(url=url, headers=header).content


def return_element_list_by_xpath(element_source: lxml_html.HtmlElement, xpath_expression: str, attribute=None) -> list:
    """ If attribute is set to text() it will get text -> item:combobox, else it will return a list"""
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


def xpath_root(page_source) -> lxml_html.HtmlElement:
    return lxml_html.fromstring(html=page_source)


def xpath_builder(path_item, attributes, localname, class_name, level=1, multi_item=False):
    # TODO automate by checking for li,lu,rows etc..?

    # TODO keep working on improving this method in identifying items.
    path_item = str(path_item).split('/')[1:][-int(level):]
    xpath_ = "/".join(path_item)

    if class_name != "":
        query_ = localname + '.' + class_name.replace(' ', '.')
    else:
        query_ = localname

    if multi_item:
        if attributes:
            element_path = '[' + ' and '.join([f'@{key}' for key in attributes.keys()]) + ']'
            query_ += "".join([f'[{key}]' for key in attributes.keys()])
        else:
            element_path = ""
    else:
        if attributes:
            element_path = '[' + ' and '.join([f'normalize-space(@{key})="{value.strip()}"' for key, value in attributes.items()]) + ']'
            query_ += "".join([f'[{key}="{value}"]' for key, value in attributes.items()])
        else:
            element_path = ""

    xpath_ += element_path
    return '//' + xpath_, query_, path_item[0]


def single_item(path: str) -> str:
    """ This function returns the js only for a single element"""
    return f"""document.evaluate('{path}', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, 
    null).singleNodeValue.style.backgroundColor = "#FDFF47"; """


def multi_item(local_name: str, attributes: dict) -> tuple:
    attributes_ = attributes.copy()

    js = Template("""
    var item = document.querySelectorAll('${item}');
    if(item[0]${parentNode} === '${localName}') {
        item.forEach((e) => {
        e.style.backgroundColor = '#FDFF47';
            });
        }""")

    query_ = local_name
    if 'class' in attributes_.keys():
        query_ += '.' + attributes_['class'].replace(' ', '.')
        del attributes_['class']
    query_ += "".join([f'[{key}]' for key in attributes_.keys()])

    level = 2
    parentnode = "".join(['.parentNode' for i in range(int(level)-1)]) + '.localName'
    js.substitute(item=query_, parentNode=parentnode, localName=local_name )

    element_path = f'//{local_name}[' + ' and '.join([f'@{key}' for key in attributes.keys()]) + ']'

    return js, element_path


def single_link():
    pass


def multi_link():
    pass


def pagination():
    pass


def generated_item():
    pass


