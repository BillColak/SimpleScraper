# import requests
# from urllib.parse import urljoin
# from lxml import html as lxml_html
from string import Template as form_Template

# //a[normalize-space(@class)='result-title hdrlnk']/@href

header = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                        'Chrome/85.0.4183.121 Safari/537.36'}

colors = {
    'yellow': '#FDFF47',
    'blue': '#2896FF'
}


def resp(url):
    response = requests.get(url=url, headers=header)
    response.close()
    return response


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


def single_item(path: str, color: str = colors['yellow']) -> str:
    """ This function returns the js only for a single element"""
    return f"""document.evaluate('{path}', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, 
    null).singleNodeValue.style.backgroundColor = "{color}"; """


def multi_item(local_name: str, attributes: dict, path: str) -> tuple:
    """ This functions returns xpath to select all html elements with
     similar attributes and the javascript to highlight them"""
    attributes_ = attributes.copy()

    js = form_Template("""
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
    parentnode = "".join(['.parentNode' for _ in range(int(level)-1)]) + '.localName'
    parent_level = str(path).split('/')[1:][-int(level):][0]
    element_path = f'//{local_name}[' + ' and '.join([f'@{key}' for key in attributes.keys()]) + ']'
    return js.substitute(item=query_, parentNode=parentnode, localName=parent_level), element_path


def scrape_single_link(path: str, attributes: dict):
    import re
    parent_level = re.findall(r'[A-z]', str(path).split('/')[-1])[0]
    return '//' + parent_level + '[' + ' and '.join([f'normalize-space(@{key})="{value.strip()}"' for key, value in
                                                     attributes.items() if key != 'href']) + ' and @href' + ']'


def scrape_multi_link():
    pass


def scrape_generated_item():
    pass


def scrape_pagination(url: str, path: str):

    page = resp(url)
    if page.status_code == 200:
        next_page = return_element_list_by_xpath(xpath_root(page.content), path, '//@href')
        if next_page[0] != '' and len(next_page) != 0:
            next_page_url = urljoin(base=url, url=next_page[0])
            print(next_page_url)
            scrape_pagination(next_page_url, path)
    else: print('Web page is not valid')


# ------------ CRAIGSLIST -------------------------


# attrib = {'href': 'https://vancouver.craigslist.org/search/cto',
#           'data-id': '7211067848', 'class': 'result-title hdrlnk', 'id': 'postid_7211067848'}
# attrib = {'href': '/search/cto?s=120', 'class': 'button next', 'title': 'next page'}
# url ='https://vancouver.craigslist.org/search/cto'
# path = '/html/body/section/form/div[3]/div[3]/span[2]/a[3]'

#/html/body/section/form/div[3]/div[3]/span[2]/a[3]
# element = scrape_single_link(path, attrib)
# print(element)
# scrape_pagination(url, element)

# ------------ KIJIJI -------------------------


# attrib = {'title': 'Next', 'href': '/b-cars-trucks/calgary/new__used/page-2/c174l1700199a49'}
# url = 'https://www.kijiji.ca/b-cars-trucks/calgary/new__used/c174l1700199a49'
# path = '/html/body/div[3]/div[3]/div[3]/div[3]/div[3]/div[57]/div/a[10]'

# element = scrape_single_link(path, attrib)
# scrape_pagination(url, element)
