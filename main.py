# TODO dynamically generated pages like kijiji auto
# TODO json serialization,
# TODO Remove deleted items from dictionary
# TODO create pyqt5 file menu, window etc.. templates for future reference. settings -> editor ->templates.
# TODO highlight should be toggled on or off.
# TODO add back the footer, change the app name to simpescraper, not the webpage its on.
# TODO DELETE treeview row
# TODO show if the op is good or not by marking it with colors on treeview and give different color on browser?
# TODO prepare columns, Intellisense.
# TODO you have to hold the click button for kijiji....




# TODO NOTE: DON'T BE DELICATE WITH THE CODE! FUCK IT UP THE ASS!!!! <--- Such as intellisense BS.


import os

from PyQt5 import QtCore, QtWidgets, QtWebEngineWidgets, QtWebChannel, QtGui

from jinja2 import Template

from treeview_model import view

from data_file import my_data

from scrape import resp, xpath_root, xpath_builder, return_element_list_by_xpath

from string import Template as formTemplate


CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))


HOME = 'https://vancouver.craigslist.org/search/cto'
# HOME = 'https://www.kijiji.ca/b-cars-trucks/calgary/new__used/c174l1700199a49'
# HOME = 'https://www.kijijiautos.ca/cars/suv-crossover/'


class Element(QtCore.QObject):
    def __init__(self, name, parent=None):
        super(Element, self).__init__(parent)
        self._name = name  # = 'xpath_helper'
        # self._value = value

    @property
    def name(self):
        return self._name

    # @property
    # def value(self):
    #     return self._name

    def script(self):
        return ""


class WebEnginePage(QtWebEngineWidgets.QWebEnginePage):
    def __init__(self, parent=None):
        super(WebEnginePage, self).__init__(parent)
        self.loadFinished.connect(self.onLoadFinished)
        self._objects = []  # Helper object
        self._scripts = []   # only usage? more than one script?


    def add_object(self, obj):
        self._objects.append(obj)

    @QtCore.pyqtSlot(bool)
    def onLoadFinished(self, ok):
        print("Finished loading: ", ok)
        if ok:
            self.load_qwebchannel()
            self.add_objects()
            return ok

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
            objects = {obj.name: obj for obj in self._objects}  # 'xpath_helper': Helper object
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
                    self.runJavaScript(obj.script())


class Helper(Element):  # this is the object
    xpathClicked = QtCore.pyqtSignal(str, str, str, str, str, str, str, str)
    # js_exec = QtCore.pyqtSignal(str)

    def script(self):
        js = ""
        file = QtCore.QFile(os.path.join(CURRENT_DIR, "xpath_from_element.js"))
        if file.open(QtCore.QIODevice.ReadOnly):
            content = file.readAll()
            file.close()
            js = content.data().decode()

        js += """
            function getElementAttrs(el) {
              return [].slice.call(el.attributes).map((attr) => {
                return {
                  name: attr.name,
                  value: attr.value
                }
              });
            }
            document.addEventListener('contextmenu', function(e) {
                e.preventDefault();
                e = e || window.event;
                var target = e.target || e.srcElement;
                var xpath = Elements.DOMPath.xPath(target, false);
                var local_name = target.localName;
                var text = target.innerText;
                var class_name = target.className;
                var image = target.getAttribute("src");
                var link = target.href;
                var allAttrs = getElementAttrs(target);
                var onlyAttrNames = allAttrs.map(attr => attr.name).toString();
                var onlyAttrValues = allAttrs.map(attr => attr.value).toString();
                {{name}}.receive_xpath(onlyAttrNames,onlyAttrValues, xpath, local_name, text, class_name, image, link);
            }, false);
            """
        return Template(js).render(name=self.name)

    @QtCore.pyqtSlot(str, str, str, str, str, str, str, str)
    def receive_xpath(self, names, values, xpath, local_name, text, class_name, image, link):
        self.xpathClicked.emit(names, values, xpath, local_name, text, class_name, image, link)

    # @QtCore.pyqtSlot(str)
    # def receive_js(self, value):
    #     self.js_exec.emit(value)


class LeftClick(Element):
    js_exec = QtCore.pyqtSignal(str)

    def script(self):
        js = ""
        file = QtCore.QFile(os.path.join(CURRENT_DIR, "xpath_from_element.js"))
        if file.open(QtCore.QIODevice.ReadOnly):
            content = file.readAll()
            file.close()
            js = content.data().decode()

        js += """
            document.addEventListener('contextmenu', function(e) {
                e.preventDefault();
                e = e || window.event;
                var target = e.target || e.srcElement;
                var xpath = Elements.DOMPath.xPath(target, false);
                {{name}}.receive_js(xpath);
                }, false);
                """
        return Template(js).render(name=self.name)

    @QtCore.pyqtSlot(str)
    def receive_js(self, value):
        self.js_exec.emit(value)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setWindowTitle("Simple Scraper")
        self.setWindowIcon(QtGui.QIcon(os.path.join('images', 'icon.ico')))
        self.setGeometry(450, 150, 1650, 950)
        # self.xpath_helper = Helper("xpath_helper")
        # self.xpath_helper.xpathClicked.connect(self.return_xpath)
        # self.left_click = LeftClick("left_click")
        # self.left_click.js_exec.connect(self.return_left_click)
        self.UI()
        self.show()
        self.level = 1

    def UI(self):
        self.QtBrowser()
        self.stackedWidget()
        self.toolBar()
        self.GUI_Theme()

    def stackedWidget(self):
        central_widget = QtWidgets.QWidget()
        self.stackedlay = QtWidgets.QStackedLayout(central_widget)
        self.stackedlay.addWidget(self.browserwindow)

        self.tree_window()
        self.stackedlay.addWidget(self.tree_window_widget)
        self.setCentralWidget(central_widget)

    # def leftClickEvent(self):
    #     self.page.add_object(self.left_click)

    def QtBrowser(self):
        self.browserwindow = QtWidgets.QWidget()
        self.browserwindow.setLayout(QtWidgets.QVBoxLayout())
        # BROWSER
        self.browser = QtWebEngineWidgets.QWebEngineView()
        self.page = WebEnginePage()

        self.xpath_helper = Helper("xpath_helper")
        self.xpath_helper.xpathClicked.connect(self.return_xpath)

        # self.left_click = LeftClick("left_click")
        # self.left_click.js_exec.connect(self.return_left_click)

        self.page.add_object(self.xpath_helper)
        # self.page.add_object(self.left_click)
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

    def toolBar(self):
        navtb = QtWidgets.QToolBar("Navigation")
        navtb.setIconSize(QtCore.QSize(24, 24))
        self.addToolBar(QtCore.Qt.LeftToolBarArea, navtb)

        self.file = QtWidgets.QAction(QtGui.QIcon('icons/globe2.svg'), "Open File", self)
        navtb.addAction(self.file)
        self.file.triggered.connect(self.window1)
        navtb.addSeparator()

        self.filetree = QtWidgets.QAction(QtGui.QIcon('images/diagram-3-fill.svg'), "TreeView", self)
        navtb.addAction(self.filetree)
        self.filetree.triggered.connect(self.window2)
        navtb.addSeparator()

        self.highlight = QtWidgets.QAction(QtGui.QIcon('images/Hlighter.png'), 'Highlight', self)
        navtb.addAction(self.highlight)
        self.highlight.triggered.connect(self.highlight_xpath)
        navtb.addSeparator()

        self.arrow_up = QtWidgets.QAction(QtGui.QIcon('images/arrow-up-circle.svg'), "Increase Restrictions", self)
        navtb.addAction(self.arrow_up)
        self.arrow_up.triggered.connect(self.traverse_up)
        navtb.addSeparator()

        self.arrow_down = QtWidgets.QAction(QtGui.QIcon('images/arrow-down-circle.svg'), "Decrease Restrictions", self)
        navtb.addAction(self.arrow_down)
        self.arrow_down.triggered.connect(self.traverse_down)
        navtb.addSeparator()

        left_spacer = QtWidgets.QWidget()
        left_spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        navtb.addWidget(left_spacer)

        self.intellisense_icon = QtWidgets.QAction(QtGui.QIcon('images/purple-cube.svg'), 'Intellisense', self)
        navtb.addAction(self.intellisense_icon)

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

    def GUI_Theme(self):
        style = open('themes/darkblue.css', 'r')
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

    def change_image(self):
        image = QtGui.QImage()
        _text = ''
        image_link = ''

        index = self.treemodel_view.tree.selectedIndexes()[0]
        selected_row = index.model().itemFromIndex(index)
        for item in my_data:
            if item['QItem'] == selected_row:
                print("SELECTED ROW: ", item)
                html_page = xpath_root(resp(item['url_name']))
                element_xpath, query_, parent_localname = xpath_builder(item['xpath'], item['attributes'], item['local_name'],
                                                                item['class_name'], level=self.level, multi_item=False)
                item_value = return_element_list_by_xpath(html_page, element_xpath, attribute='/text()')
                print(item_value)
                # _text = '\n\n' + item['value'] + '\n'
                # _text = '\n\n' + item_value + '\n'
                if item['image_link'] != '':
                    image_link = item['image_link']

        try:
            if image_link != '':
                image.loadFromData(resp(image_link))
                self.image_label.setPixmap(QtGui.QPixmap(image))
            else:
                self.image_label.setText(_text)
        except: print('messed up getting the image.')

    def return_xpath(self, names, values, xpath, local_name, text, class_name, image, link):
        # self.browser.customMenuAction(names)
        if names or values:
            attributes = dict(zip(str(names).split(","), str(values).split(
                ",")))
        else:
            attributes = None
        # print(attributes)
        browser_url = self.browser.url().toString()
        url_list = [row['link'] for row in my_data if row['link'] is not None]
        tree_item = {'unique_id': None}

        if browser_url not in url_list:  # ADD MAIN CHILD
            tree_item['unique_id'] = my_data[-1]['unique_id']+1
            tree_item['parent_id'] = 1
            tree_item['url_name'] = browser_url
            tree_item['xpath'] = xpath
            tree_item['value'] = text
            tree_item['link'] = link
            tree_item['class_name'] = class_name
            tree_item['image_link'] = image
            tree_item['local_name'] = local_name
            tree_item['attributes'] = attributes

        for index, row in enumerate(my_data):  # if previously selected link is the current page, add it as a child.
            if row['link'] == browser_url:
                tree_item['unique_id'] = my_data[-1]['unique_id'] + 1
                tree_item['parent_id'] = row['unique_id']
                tree_item['url_name'] = browser_url
                tree_item['xpath'] = xpath
                tree_item['value'] = text
                tree_item['link'] = link
                tree_item['class_name'] = class_name
                tree_item['image_link'] = image
                tree_item['local_name'] = local_name
                tree_item['attributes'] = attributes

        if tree_item['unique_id'] is not None:
            self.treemodel_view.create_row(tree_dict=tree_item)
            self.treemodel_view.tree.expandAll()
            url_list.clear()

    def return_left_click(self, names):
        print('LEFTCLICK: ', names)

    def highlight_xpath(self):
        highlight_js = formTemplate("""var item = document.querySelectorAll('${item}');
                                        if(item[0]${parentNode} === '${localName}') {
                                            item.forEach((e) => {
                                                e.style.backgroundColor = '#FDFF47';
                                            });
                                        }
                                        """)

        parentnode = "".join(['.parentNode' for i in range(int(self.level)-1)]) + '.localName'

        for row in my_data:
            if self.browser.url().toString() == row['url_name']:
                if int(row['combobox'].getComboValue()) == 0:  # change color for operation / pagination.

                    self.page.runJavaScript(f"""document.evaluate('{row['xpath']}', document, null,
                    XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.style.backgroundColor = "#FDFF47";""",
                                            )
                elif int(row['combobox'].getComboValue()) == 1:
                    depth, query_, parent_localname = xpath_builder(row['xpath'], row['attributes'], row['local_name'], row['class_name'], level=self.level, multi_item=True)
                    print(depth, query_, parent_localname)
                    self.page.runJavaScript(highlight_js.substitute(item=query_, parentNode=parentnode, localName=parent_localname))
                else:
                    depth, query_, parent_localname = xpath_builder(row['xpath'], row['attributes'], row['local_name'], row['class_name'], level=self.level, multi_item=False)
                    print(depth, query_, parent_localname)
                    self.page.runJavaScript(highlight_js.substitute(item=query_, parentNode=parentnode, localName=parent_localname))

    def traverse_up(self):
        # self.browser.reload()
        self.level += 1
        # self.page.loadFinished.connect(self.highlight_xpath)
        self.highlight_xpath()

    def traverse_down(self):
        # self.browser.reload()
        self.level -= 1
        # self.page.loadFinished.connect(self.highlight_xpath)
        self.highlight_xpath()

    def run_scraper(self):
        print('MY_DATA: ')
        for d in my_data:
            print(d)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())