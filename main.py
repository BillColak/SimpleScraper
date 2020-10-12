
# TODO json serialization,
# TODO Remove deleted items from dictionary
# TODO create pyqt5 file menu, window etc.. templates for future reference. settings -> editor ->templates.
# TODO highlight should be toggled on or off.
# TODO add back the footer, change the app name to simpescraper, not the webpage its on.
# TODO DELETE treeview row
# TODO show if the op is good or not by marking it with colors on treeview and give different color on browser?
# TODO prepare columns, intellisense.


import os

from PyQt5 import QtCore, QtWidgets, QtWebEngineWidgets, QtWebChannel, QtGui

from jinja2 import Template

from treeview_model import view

from data_file import my_data

import requests

from string import Template as formTemplate


CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))


HOME = 'https://vancouver.craigslist.org/search/cto'
# HOME = 'https://www.kijiji.ca/b-cars-trucks/calgary/new__used/c174l1700199a49'


class Element(QtCore.QObject):
    def __init__(self, name, parent=None):
        super(Element, self).__init__(parent)
        self._name = name

    @property
    def name(self):
        return self._name

    def script(self):
        return ""


class WebEnginePage(QtWebEngineWidgets.QWebEnginePage):
    def __init__(self, parent=None):
        super(WebEnginePage, self).__init__(parent)
        self.loadFinished.connect(self.onLoadFinished)
        self._objects = []
        self._scripts = []   # only usage? more than one script?

    def add_object(self, obj):
        self._objects.append(obj)

    @QtCore.pyqtSlot(bool)
    def onLoadFinished(self, ok):
        print("Finished loading: ", ok)
        if ok:
            self.load_qwebchannel()
            self.add_objects()

    def load_qwebchannel(self):
        file = QtCore.QFile(":/qtwebchannel/qwebchannel.js")
        if file.open(QtCore.QIODevice.ReadOnly):
            content = file.readAll()
            file.close()
            self.runJavaScript(content.data().decode())
        if self.webChannel() is None:
            channel = QtWebChannel.QWebChannel(self)
            self.setWebChannel(channel)

    def add_objects(self):
        if self.webChannel() is not None:
            objects = {obj.name: obj for obj in self._objects}
            self.webChannel().registerObjects(objects)
            _script = """
            {% for obj in objects %}
            var {{obj}};
            {% endfor %}
            new QWebChannel(qt.webChannelTransport, function (channel) {
            {% for obj in objects %}
                {{obj}} = channel.objects.{{obj}};
            {% endfor %}
            }); 
            """
            self.runJavaScript(Template(_script).render(objects=objects.keys()))
            for obj in self._objects:
                if isinstance(obj, Element):
                    self.runJavaScript(obj.script())  # TODO run JS: add script to object...


class Helper(Element):
    xpathClicked = QtCore.pyqtSignal(str, str, str, str, str, str, str)

    def script(self):
        js = ""
        file = QtCore.QFile(os.path.join(CURRENT_DIR, "xpath_from_element.js"))
        if file.open(QtCore.QIODevice.ReadOnly):
            content = file.readAll()
            file.close()
            js = content.data().decode()  # TODO doesn't work because it doesn't return anything other than string

        js += """
            function getElementAttrs(el) {
              return [].slice.call(el.attributes).map((attr) => {
                return {
                  name: attr.name,
                  value: attr.value
                }
              });
            }
            document.addEventListener('click', function(e) {
                e = e || window.event;
                var target = e.target || e.srcElement;
                var xpath = Elements.DOMPath.xPath(target, false);
                var localname = target.localName;
                var text = target.innerText;
                var class_name = target.className;
                var image = target.getAttribute("src");
                var allAttrs = getElementAttrs(target);
                var onlyAttrNames = allAttrs.map(attr => attr.name).toString();
                var onlyAttrValues = allAttrs.map(attr => attr.value).toString();
                {{name}}.receive_xpath(onlyAttrNames,onlyAttrValues, xpath, localname, text, class_name, image);
            }, false);"""
        return Template(js).render(name=self.name)

    @QtCore.pyqtSlot(str, str, str, str, str, str, str)
    def receive_xpath(self, names, values, xpath, localname, text, class_name, image):
        self.xpathClicked.emit(names, values, xpath, localname, text, class_name, image)

# class Helper(Element):
#     xpathClicked = QtCore.pyqtSignal(str, str, str, str, str, str)
#
#     def script(self):
#         js = ""
#         file = QtCore.QFile(os.path.join(CURRENT_DIR, "xpath_from_element.js"))
#         if file.open(QtCore.QIODevice.ReadOnly):
#             content = file.readAll()
#             file.close()
#             js = content.data().decode()
#
#         js += """
#         document.addEventListener('click', function(e) {
#             e = e || window.event;
#             var target = e.target || e.srcElement;
#             var xpath = Elements.DOMPath.xPath(target, false);
#             var childCount = target.localName;
#             var text = target.innerText;
#             var link = target.href;
#             var parent = target.className;
#             var image = target.getAttribute("src");
#             {{name}}.receive_xpath(xpath, text, link, parent, image, childCount);
#         }, false);"""
#         return Template(js).render(name=self.name)
#     # var childCount = target.parentElement.childElementCount;
#     # var childCount = target.parentNode.childElementCount;
#     # var parent = target.parentNode.href;
#     # var parent = target.className;
#     # var parent = target.textContent;
#     # var childCount = target.tagName;
#     #var childCount = target.localName;
#
#     @QtCore.pyqtSlot(str, str, str, str, str, str)
#     def receive_xpath(self, xpath, text, link, parent, image, childcount):
#         self.xpathClicked.emit(xpath, text, link, parent, image, childcount)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setWindowTitle("Simple Scraper")
        self.setWindowIcon(QtGui.QIcon(os.path.join('images', 'icon.ico')))
        self.setGeometry(450, 150, 1650, 950)
        self.xpath_helper = Helper("xpath_helper")
        self.xpath_helper.xpathClicked.connect(self.return_xpath)
        self.UI()
        self.show()

    def UI(self):
        self.QtBrowser()
        self.stackedWidget()
        self.toolBar()
        self.Dark_Orange_Theme()

    def stackedWidget(self):
        central_widget = QtWidgets.QWidget()
        self.stackedlay = QtWidgets.QStackedLayout(central_widget)
        self.stackedlay.addWidget(self.browserwindow)

        self.tree_window()
        self.stackedlay.addWidget(self.tree_window_widget)
        self.setCentralWidget(central_widget)

    def QtBrowser(self):
        self.browserwindow = QtWidgets.QWidget()
        self.browserwindow.setLayout(QtWidgets.QVBoxLayout())
        # BROWSER
        self.browser = QtWebEngineWidgets.QWebEngineView()
        self.page = WebEnginePage()
        self.page.add_object(self.xpath_helper)  # TODO ADD OBJECTS to the list
        self.browser.setPage(self.page)

        self.browser.urlChanged.connect(self.update_urlbar)
        self.browser.loadFinished.connect(self.update_title)

        # BROWSER NAVIGATION BAR
        self.browsernavbar = QtWidgets.QWidget()
        self.browsernavbar.setLayout(QtWidgets.QHBoxLayout())
        self.browsernavbar.layout().setAlignment(QtCore.Qt.AlignHCenter)
        self.browsernavbar.layout().setContentsMargins(0,0,0,0)
        self.browsernavbar.setFixedHeight(30)

        back_btn = QtWidgets.QPushButton(QtGui.QIcon(os.path.join('icons', 'arrow-left.svg')), "Back", self)
        back_btn.clicked.connect(self.browser.back)
        self.browsernavbar.layout().addWidget(back_btn)

        next_btn = QtWidgets.QPushButton(QtGui.QIcon(os.path.join('icons', 'arrow-right.svg')), "Forward", self)
        next_btn.clicked.connect(self.browser.forward)
        self.browsernavbar.layout().addWidget(next_btn)

        reload_btn = QtWidgets.QPushButton(QtGui.QIcon(os.path.join('icons', 'arrow-clockwise.svg')), "Reload", self)
        reload_btn.clicked.connect(self.browser.reload)
        self.browsernavbar.layout().addWidget(reload_btn)

        home_btn = QtWidgets.QPushButton(QtGui.QIcon(os.path.join('icons', 'house-fill.svg')), "Home", self)
        home_btn.clicked.connect(self.navigate_home)
        self.browsernavbar.layout().addWidget(home_btn)

        self.httpsicon = QtWidgets.QLabel()
        self.httpsicon.setPixmap(QtGui.QPixmap(os.path.join('icons', 'shield-lock-fill.svg')))
        self.browsernavbar.layout().addWidget(self.httpsicon)

        self.urlbar = QtWidgets.QLineEdit()
        self.urlbar.returnPressed.connect(self.navigate_to_url)
        self.browsernavbar.layout().addWidget(self.urlbar)

        self.browserwindow.layout().addWidget(self.browsernavbar)
        self.browserwindow.layout().addWidget(self.browser)
        self.browser.load(QtCore.QUrl(HOME))

        # self.page.profile().clearHttpCache()
        # self.browser.page().profile().clearHttpCache()
        # self.page.profile().defaultProfile().cookieStore().deleteAllCookies()

    def toolBar(self):
        navtb = QtWidgets.QToolBar("Navigation")
        navtb.setIconSize(QtCore.QSize(24, 24))
        self.addToolBar(QtCore.Qt.LeftToolBarArea, navtb)

        self.file = QtWidgets.QAction(QtGui.QIcon('icons/globe2.svg'), "Open File", self)
        navtb.addAction(self.file)
        self.file.triggered.connect(self.window1)
        navtb.addSeparator()

        # self.filetree = QtWidgets.QAction(QtGui.QIcon('images/filetree.png'), "TreeView", self)
        self.filetree = QtWidgets.QAction(QtGui.QIcon('icons/diagram-3-fill.svg'), "TreeView", self)
        navtb.addAction(self.filetree)
        self.filetree.triggered.connect(self.window2)
        navtb.addSeparator()

        self.highlight = QtWidgets.QAction(QtGui.QIcon('images/Hlighter.png'), 'Hightlight', self)
        navtb.addAction(self.highlight)
        self.highlight.triggered.connect(self.highlight_xpath)
        navtb.addSeparator()

        self.arrow_up = QtWidgets.QAction(QtGui.QIcon('icons/arrow-up-circle.svg'), "Up", self)
        navtb.addAction(self.arrow_up)
        navtb.addSeparator()

        self.arrow_down = QtWidgets.QAction(QtGui.QIcon('icons/arrow-down-circle.svg'), "Down", self)
        navtb.addAction(self.arrow_down)
        navtb.addSeparator()

        left_spacer = QtWidgets.QWidget()
        left_spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        navtb.addWidget(left_spacer)

        self.run = QtWidgets.QAction(QtGui.QIcon('images/play-hot.png'), 'Run', self)
        navtb.addAction(self.run)
        self.run.triggered.connect(self.run_scraper)

    def update_title(self):
        title = self.browser.page().title()
        self.setWindowTitle(title)

    def navigate_home(self):
        self.browser.setUrl(QtCore.QUrl(HOME))

    def navigate_to_url(self):
        q = QtCore.QUrl(self.urlbar.text())
        if q.scheme() == "":
            q.setScheme("http")
        self.browser.setUrl(q)

    def update_urlbar(self, q):
        if q.scheme() == 'https':
            self.httpsicon.setPixmap(QtGui.QPixmap(os.path.join('icons', 'shield-lock-fill.svg')))
        else:
            self.httpsicon.setPixmap(QtGui.QPixmap(os.path.join('icons', 'shield-slash.png')))

        self.urlbar.setText(q.toString())
        self.urlbar.setCursorPosition(0)

    def Dark_Orange_Theme(self):
        style = open('themes/darkorange.css', 'r')
        style = style.read()
        self.setStyleSheet(style)

    def window1(self):
        self.stackedlay.setCurrentIndex(0)

    def window2(self):
        self.stackedlay.setCurrentIndex(1)

    def tree_window(self):
        self.tree_window_widget = QtWidgets.QWidget()
        self.tree_window_widget.setLayout(QtWidgets.QVBoxLayout())
        self.tree_window_widget.layout().setContentsMargins(0, 0, 0, 0)

        self.scrollarea = QtWidgets.QScrollArea()
        # self.treemodel_view = view(data)
        self.treemodel_view = view()
        self.treemodel_view.tree.clicked.connect(self.change_image)

        self.image_label = QtWidgets.QLabel()
        self.image_label.setMinimumHeight(350)
        self.image_label.setMinimumWidth(350)
        self.image_label.setWordWrap(True)

        self.image_label.setFont(QtGui.QFont("Arial", 12))
        self.image_label.setAlignment(QtCore.Qt.AlignCenter)
        self.scrollarea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.scrollarea.setWidget(self.image_label)
        self.scrollarea.setWidgetResizable(True)

        self.tree_window_widget.layout().addWidget(self.scrollarea)
        self.tree_window_widget.layout().addWidget(self.treemodel_view)

    def change_image(self):  # TODO This is suppose to show you what you get if you scraped it.
        image = QtGui.QImage()
        _text = ''
        image_link = ''

        index = self.treemodel_view.tree.selectedIndexes()[0]
        val = index.model().itemFromIndex(index)
        for item in my_data:
            if item['QItem'] == val:
                print("SELECTED ROW: ", item)
                _text = '\n\n' + item['value'] + '\n'
                if item['image_link'] != '':
                    image_link = item['image_link']

        try:
            if image_link != '':
                image.loadFromData(requests.get(image_link).content)
                self.image_label.setPixmap(QtGui.QPixmap(image))
            else:
                self.image_label.setText(_text)
        except: print('messed up getting the image.')

    def return_xpath(self, names, values, xpath, localname, text, class_name, image):
        n = str(names).split(",")
        v = str(values).split(",")
        d = dict(zip(n, v))

        element_path = localname + '.' + class_name.replace(' ', '.')
        for name in n:
            element_path += '['+name.replace(' ', '.')+']'
        print(element_path)

    def xpath_builder(self, level, path_item, elements):
        path_item = str(path_item).split('/')
        if int(level) > 0:
            element_path = '[' + ' and '.join([f'normalize-space(@{key})="{value.strip()}"' for key, value in elements.items()]) + ']'
            depth = "/".join(path_item[int(level):])  # TODO reverse this when using arrow and take care of indexing error.
            depth += element_path
            return '//' + depth

    # def return_xpath(self, xpath, text, link, class_name, image, name_tag):
    #     print('xpath: ',xpath,'text: ',text,'link: ',link,'class_name: ',class_name,'image: ',image,'name_tag: ',name_tag)
        # browser_url = self.browser.url().toString()
        # url_list = [row['link'] for row in my_data if row['link'] is not None]
        # tree_item = {'unique_id': None}
        #
        # if browser_url not in url_list:  # ADD MAIN CHILD
        #     tree_item['unique_id'] = my_data[-1]['unique_id']+1
        #     tree_item['parent_id'] = 1
        #     tree_item['url_name'] = browser_url
        #     tree_item['xpath'] = xpath
        #     tree_item['value'] = text
        #     tree_item['link'] = link
        #     tree_item['class_name'] = class_name
        #     tree_item['image_link'] = image
        #     tree_item['name_tag'] = name_tag
        #
        # for index, row in enumerate(my_data):  # if previously selected link is the current page, add it as a child.
        #     if row['link'] == browser_url:
        #         tree_item['unique_id'] = my_data[-1]['unique_id'] + 1
        #         tree_item['parent_id'] = row['unique_id']
        #         tree_item['url_name'] = browser_url
        #         tree_item['xpath'] = xpath
        #         tree_item['value'] = text
        #         tree_item['link'] = link
        #         tree_item['class_name'] = class_name
        #         tree_item['image_link'] = image
        #         tree_item['name_tag'] = name_tag
        #
        # if tree_item['unique_id'] is not None:
        #     self.treemodel_view.create_row(tree_dict=tree_item)
        #     self.treemodel_view.tree.expandAll()
        #     url_list.clear()



    def highlight_xpath(self):
        # TODO this is suppose to show u what u are scraping especially with xpath traversal. Also make the traversal
        #  reversed start with lower restrictions and increase them to be more specific.
        # the issue with this is how are you going to traverse in js?

        highlight_js = formTemplate("""var item = document.querySelectorAll('${item}');
                                                item.forEach((e)=>{
                                                    e.style.backgroundColor = '#FDFF47';
                                                    });""")

        for row in my_data:  # TODO should not be using my_data but row selection instead
            if self.browser.url().toString() == row['url_name']:
                if int(row['combobox'].getComboValue()) == 1:  # change color for operation / pagination.
                    name_tag, class_name = row['name_tag'].lower(), row['class_name'].strip().replace(' ', '.')
                    query_ = ".".join((name_tag, class_name))
                    # TODO kijiji next page; also a more robust querying
                    self.page.runJavaScript(highlight_js.substitute(item=query_))
                else:
                    self.page.runJavaScript(f"""document.evaluate('{row['xpath']}', document, null,
                    XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.style.backgroundColor = "#FDFF47";""",
                                            )

        # self.treemodel_view.transverse_tree()
        # highlight_js = form_template("""elements = document.getElementsByClassName(${item});
        #                         for (var i = 0; i < elements.length; i++) {
        #                         elements[i].style.backgroundColor="#FDFF47";
        #                         }""")
        #
        # for row in my_data:
        #     if self.browser.url().toString() == row['url_name']:
        #         if int(row['operation']) == 1:
        #             self.page.runJavaScript(highlight_js.substitute(item='"'+row['class_name']+'"'))
        #         else:
        #             self.page.runJavaScript(f"""document.evaluate('{row['xpath']}', document, null,
        #             XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.style.backgroundColor = "#FDFF47";""",
        #                                     )

    def run_scraper(self):
        # self.treemodel_view.transverse_tree()
        print('MY_DATA: ')
        for d in my_data:
            print(d)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())