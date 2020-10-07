
# TODO json serialization,
# TODO Remove deleted items from dictionary
# TODO ScrollArea size -> possibly going to make a graphics scene
# TODO allow of clicking after loading?
# TODO refactor JS Children element count.
# TODO create pyqt5 file menu, window etc.. templates for future reference. settings -> editor ->templates.
# TODO highlight should be toggled on or off.
# TODO add back the footer, change the app name to simpescraper, not the webpage its on.
# TODO debug detItem
# TODO xpath highlight of what will be scraped
# TODO insertup and delete debugging
# TODO Overhaul serialization. turn ym_data to dict?

import os

from PyQt5 import QtCore, QtWidgets, QtWebEngineWidgets, QtWebChannel, QtGui

from jinja2 import Template

from treeview_model import view

from data_file import my_data, my_dict_data

import requests

from string import Template as form_template



CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))


HOME = 'https://vancouver.craigslist.org/search/cto'


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
        self._scripts = []

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
                    self.runJavaScript(obj.script())


class Helper(Element):
    xpathClicked = QtCore.pyqtSignal(str, str, str, str, str, str)

    def script(self):
        js = ""
        file = QtCore.QFile(os.path.join(CURRENT_DIR, "xpath_from_element.js"))
        if file.open(QtCore.QIODevice.ReadOnly):
            content = file.readAll()
            file.close()
            js = content.data().decode()

        js += """
        document.addEventListener('click', function(e) {
            e = e || window.event;
            var target = e.target || e.srcElement;
            var xpath = Elements.DOMPath.xPath(target, false);
            var childCount = target.tagName;
            var text = target.innerText;
            var link = target.href;
            var parent = target.className;
            var image = target.getAttribute("src");
            {{name}}.receive_xpath(xpath, text, link, parent, image, childCount);
        }, false);"""
        return Template(js).render(name=self.name)
    # var childCount = target.parentElement.childElementCount;
    # var childCount = target.parentNode.childElementCount;
    # var parent = target.parentNode.href;
    # var parent = target.className;

    @QtCore.pyqtSlot(str, str, str, str, str, str)
    def receive_xpath(self, xpath, text, link, parent, image, childcount):
        self.xpathClicked.emit(xpath, text, link, parent, image, childcount)


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
        self.page.add_object(self.xpath_helper)
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
        self.treemodel_view = view(my_data)
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
        for k, v in self.treemodel_view.seen.items():
            if v == val:  # if selected item is in self.seen:
                for row in my_data:
                    if str(row['unique_id']) == str(k):
                        print("SELECTED ROW: ", row)
                        _text = '\n\n' + row['value'] + '\n'
                        if row['image_link'] != '':
                            image_link = row['image_link']
        try:
            if image_link != '':
                image.loadFromData(requests.get(image_link).content)
                self.image_label.setPixmap(QtGui.QPixmap(image))
            else:
                self.image_label.setText(_text)
        except: print('messed up getting the image.')

    def return_xpath(self, xpath, text, link, class_name, image, name_tag):
        browser_url = self.browser.url().toString()

        url_list = [row['link'] for row in my_data if row['link'] is not None]  # if link is not in the list, add it as a main page to scrape. So need something for current page. TODO use sets for duplicates
        # my_url_list = [row['link'] for row in my_dict_data.values() if row['link'] is not None]
        # print(url_list == my_url_list)
        tree_dict = {'unique_id': None}

        try:
            if browser_url not in url_list:  # ADD MAIN CHILD
                tree_dict['unique_id'] = my_data[-1]['unique_id']+1
                tree_dict['parent_id'] = 1
                tree_dict['url_name'] = browser_url
                tree_dict['xpath'] = xpath
                tree_dict['value'] = text
                tree_dict['link'] = link
                tree_dict['class_name'] = class_name
                tree_dict['image_link'] = image
                tree_dict['childcount'] = name_tag

            for index, row in enumerate(my_data):  # if the selected link is the current page, add current page as a child to the page of the selected link.
                if row['link'] == browser_url:
                    tree_dict['unique_id'] = my_data[-1]['unique_id'] + 1
                    tree_dict['parent_id'] = row['unique_id']
                    tree_dict['url_name'] = browser_url
                    tree_dict['xpath'] = xpath
                    tree_dict['value'] = text
                    tree_dict['link'] = link
                    tree_dict['class_name'] = class_name
                    tree_dict['image_link'] = image
                    tree_dict['childcount'] = name_tag

            if tree_dict['unique_id'] is not None:
                self.treemodel_view.add_row(tree_dict)
                self.treemodel_view.tree.expandAll()
                url_list.clear()

                # my_data.append(tree_dict)
                # my_dict_data[next(reversed(my_dict_data.keys())) + 1] = tree_dict

        except: print('messed up here')

        # self.treemodel_view.add_row(tree_dict)
        # self.treemodel_view.tree.expandAll()
        # url_list.clear()

    def highlight_xpath(self):
        self.treemodel_view.transverse_tree()
        highlight_js = form_template("""elements = document.getElementsByClassName(${item});
                                for (var i = 0; i < elements.length; i++) {
                                elements[i].style.backgroundColor="#FDFF47";
                                }""")

        for row in my_data:
            if self.browser.url().toString() == row['url_name']:
                if int(row['operation']) == 1:
                    self.page.runJavaScript(highlight_js.substitute(item='"'+row['class_name']+'"'))
                else:
                    self.page.runJavaScript(f"""document.evaluate('{row['xpath']}', document, null,
                    XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.style.backgroundColor = "#FDFF47";""",
                                            )


    def run_scraper(self):
        # print("COMBOX: ")
        # for k,v in self.treemodel_view.combodict.items():
        #     print(k,v)

        # print("SEEN: ")
        # for k, v in self.treemodel_view.seen.items():  # This gives weird error when deleting rows and calling v.data(0)
        #     print(k, v.data(0))

        # self.treemodel_view.transverse_tree()

        print('MY_DATA: ')
        for d in my_data[1:]:
            print(d)

        # print('MY_DICT_DATA: ')
        # for k, v in my_dict_data.items():
        #     print(k, v)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())