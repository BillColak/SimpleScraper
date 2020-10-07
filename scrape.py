
import requests
from lxml import html as lxml_html

# //a[normalize-space(@class)='result-title hdrlnk']/@href

header = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                        'Chrome/85.0.4183.121 Safari/537.36'}

url_name = 'https://vancouver.craigslist.org/search/cto'
item_path = '/html/body/section/form/div[4]/ul/li[1]/div/h2/a'


resp = requests.get(url=url_name, headers=header)
# print(resp.status_code, resp.cookies)


def xpath_root(page_source) -> lxml_html.HtmlElement:
    return lxml_html.fromstring(html=page_source)


el_src = xpath_root(resp.content)


def return_element_list_by_xpath(element_source: lxml_html.HtmlElement, xpath_expression: str, attribute=None) -> list:
    expression_list = []

    if attribute is not None:  # get the attribute of the element: used for multi-items (class attribute is used for
        # multi item atm...)
        xpath_expression = xpath_expression + attribute

    expression = element_source.xpath(xpath_expression)
    for item in expression:
        if isinstance(item, lxml_html.HtmlElement):
            expression_list.append(str(lxml_html.tostring(item, pretty_print=True, with_tail=False), 'utf-8'))
        else:
            expression_list.append(item)
    return expression_list


def element_class_xpath(element_class: str):
    return f"//div*[contains(@class, '{element_class}')]"


def xpath_intellisense(x):

    level = 'section'
    attrib1 = '@class'
    attrib1_text = 'title'
    attrib2 = '@href'

    return f"//*/descendant::{level}[{attrib1}='{attrib1_text}' and //*[{attrib2}]]"


# exp = return_element_list_by_xpath(el_src, item_path, attribute='//@href')
# exp = return_element_list_by_xpath(el_src, item_path, attribute='/text()')
# exp = return_element_list_by_xpath(el_src, item_path, attribute='//@href')


item_class_attrib = return_element_list_by_xpath(el_src, item_path, attribute='//@class')  # get the class attrib.
print(element_class_xpath(item_class_attrib[0]))
all_text_elements = return_element_list_by_xpath(el_src, element_class_xpath(item_class_attrib[0]), attribute='/text()')
print(len(all_text_elements))


# $(document).click(function (e) {
#     var saldir = e.target.attributes;
#     var haci = e.target.innerHTML;
#     console.log(saldir, haci);
#
# });