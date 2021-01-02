# TODO images associated with themes needed to be added to their respective css files. (honestly all themes need to be looked at)
# TODO dynamically generated pages like kijiji auto
# TODO json serialization
# TODO create pyqt5 file menu, window etc.. templates for future reference. settings -> editor ->templates. check node_editor_window. : make it a json like dictionary and you can comment out the shit you dont want/
# TODO highlight should be toggled on or off.
# TODO add back the footer, change the app name to simpescraper, not the webpage its on.
# TODO show if the op is good or not by marking it with colors on treeview and give different color on browser?
# TODO you have to hold the click button for kijiji....
# TODO if it opens a new tab go to that web page.
# TODO customise the highlight button to also work as a radio button.
# release project to open source.
# TODO someday implement node_editor into this. Since discord should be easier.
# overwrite the original context manager. as it still shows up before page loads.
# tODO https://stackoverflow.com/questions/12394184/scrapy-call-a-function-when-a-spider-quits
# todo the app crashes when you use more than one spider.
# TODO add to combobox: text contains -> the value.
# TODO test out full xpath because alternative causes problems sometimes.
# kijiji giving a 403 response.

import os

from PyQt5 import QtCore, QtWidgets, QtGui, QtWebEngineWidgets, QtWebChannel

from jinja2 import Template

from treeview_model import view

from data_file import my_data

# from test_data import my_data_full_path

from automaton_menu import MenuBar

from quotes_spider.spiders.simplespider import SpiderRunner

from functools import partial

from urllib.parse import urlparse

import time

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))

DEBUG = True

WEBSCRAPERIO = 'https://webscraper.io/test-sites/e-commerce/static'
CRAIGSLIST = 'https://vancouver.craigslist.org/search/cto'
Kijiji = 'https://www.kijiji.ca/b-cars-trucks/calgary/new__used/c174l1700199a49'
KIJIJIAUTO = 'https://www.kijijiautos.ca/cars/suv-crossover/#c=Suv&od=down&sb=ct&shortDescription=true'
HOME = 'https://books.toscrape.com/'
# HOME = 'http://quotes.toscrape.com/'
# HOME = 'https://www.google.com/'

colors = {
    'yellow': '#FDFF47',
    'blue': '#2896FF',
    'white': 'white',
}


class WorkerSignals(QtCore.QObject):
    """
    Defines the signals available from a running worker thread.

    data
        tuple of (identifier, data)
    """
    worker_signal = QtCore.pyqtSignal(tuple)


class Worker(QtCore.QRunnable):
    """
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals
    and wrap-up.

    :param worker_id: The id for this worker
    :param url: The url to retrieve
    """

    def __init__(self, worker_id, url):
        super(Worker, self).__init__()
        self.id = worker_id
        self.url = url

        self.signals = WorkerSignals()

    @QtCore.pyqtSlot()
    def run(self):
        pass

        # r = requests.get(self.url)
        #
        # for line in r.text.splitlines():
        #     self.signals.data.emit((self.id, line))


class Element(QtCore.QObject):
    def __init__(self, name, parent=None):
        super(Element, self).__init__(parent)
        self._name = name  # = 'xpath_helper'

    @property
    def name(self):
        return self._name

    def script(self):
        return ""


class WebEnginePage(QtWebEngineWidgets.QWebEnginePage):
    def __init__(self, parent=None):
        super(WebEnginePage, self).__init__(parent)
        self.loadFinished.connect(self.onLoadFinished)
        self._objects = []  # Helper object
        self._scripts = []  # only usage? more than one script?

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
    xpathClicked = QtCore.pyqtSignal(str, str, str, str, str, str, str, str, str)

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
                var parent_name = target.parentNode.localName;
                var text = target.innerText;
                var class_name = target.className;
                var image = target.getAttribute("src");
                var link = target.href;
                var allAttrs = getElementAttrs(target);
                var onlyAttrNames = allAttrs.map(attr => attr.name).toString();
                var onlyAttrValues = allAttrs.map(attr => attr.value).toString();
                {{name}}.receive_xpath(onlyAttrNames,onlyAttrValues, xpath, local_name, text, class_name, image, link, parent_name);
            }, false);
            """
        return Template(js).render(name=self.name)

    @QtCore.pyqtSlot(str, str, str, str, str, str, str, str, str)
    def receive_xpath(self, names, values, xpath, local_name, text, class_name, image, link, parent_name):
        self.xpathClicked.emit(names, values, xpath, local_name, text, class_name, image, link, parent_name)


class MainWindow(MenuBar):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setWindowIcon(QtGui.QIcon(os.path.join('images', 'cubes.svg')))
        self.setGeometry(450, 150, 1650, 950)
        self.UI()
        self.show()
        # self.thread_pool = QtCore.QThreadPool()
        # print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())
        # self.level = 1

    def UI(self):
        self.initUI()
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

    def QtBrowser(self):
        self.browserwindow = QtWidgets.QWidget()
        self.browserwindow.setLayout(QtWidgets.QVBoxLayout())
        # BROWSER
        self.browser = QtWebEngineWidgets.QWebEngineView()
        self.page = WebEnginePage()

        self.xpath_helper = Helper("xpath_helper")
        self.xpath_helper.xpathClicked.connect(self.return_xpath)

        self.page.add_object(self.xpath_helper)
        self.browser.setPage(self.page)

        self.browser.urlChanged.connect(self.update_urlbar)
        self.browser.loadFinished.connect(self.update_title)
        profile = self.page.profile().httpUserAgent()
        print(profile)
        # BROWSER NAVIGATION BAR
        self.browsernavbar = QtWidgets.QWidget()
        self.browsernavbar.setLayout(QtWidgets.QHBoxLayout())
        self.browsernavbar.layout().setAlignment(QtCore.Qt.AlignHCenter)
        self.browsernavbar.layout().setContentsMargins(0, 0, 0, 0)
        self.browsernavbar.setFixedHeight(30)

        back_btn = QtWidgets.QPushButton(QtGui.QIcon(os.path.join('images', 'arrow-left.svg')), "Back", self)
        back_btn.clicked.connect(self.browser.back)
        self.browsernavbar.layout().addWidget(back_btn)

        next_btn = QtWidgets.QPushButton(QtGui.QIcon(os.path.join('images', 'arrow-right.svg')), "Forward", self)
        next_btn.clicked.connect(self.browser.forward)
        self.browsernavbar.layout().addWidget(next_btn)

        reload_btn = QtWidgets.QPushButton(QtGui.QIcon(os.path.join('images', 'arrow-clockwise.svg')), "Reload", self)
        reload_btn.clicked.connect(self.browser.reload)
        self.browsernavbar.layout().addWidget(reload_btn)

        home_btn = QtWidgets.QPushButton(QtGui.QIcon(os.path.join('images', 'house-fill.svg')), "Home", self)
        home_btn.clicked.connect(self.navigate_home)
        self.browsernavbar.layout().addWidget(home_btn)

        self.httpsicon = QtWidgets.QLabel()
        self.httpsicon.setPixmap(QtGui.QPixmap(os.path.join('images', 'shield-lock-fill.svg')))
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

        self.file = QtWidgets.QAction(QtGui.QIcon('images/globe2.svg'), "Open Browser", self)
        navtb.addAction(self.file)
        self.file.triggered.connect(self.window1)
        navtb.addSeparator()

        self.filetree = QtWidgets.QAction(QtGui.QIcon('images/diagram-3-fill.svg'), "TreeView", self)
        navtb.addAction(self.filetree)
        self.filetree.triggered.connect(self.window2)
        navtb.addSeparator()

        self.highlight = QtWidgets.QAction(QtGui.QIcon('images/Hlighter.png'), 'Highlight', self)
        navtb.addAction(self.highlight)
        self.highlight.triggered.connect(self.inspect_element)
        navtb.addSeparator()

        # self.arrow_up = QtWidgets.QAction(QtGui.QIcon('images/arrow-up-circle.svg'), "Increase Restrictions", self)
        # navtb.addAction(self.arrow_up)
        # self.arrow_up.triggered.connect(self.traverse_up)
        # navtb.addSeparator()

        # self.arrow_down = QtWidgets.QAction(QtGui.QIcon('images/arrow-down-circle.svg'), "Decrease Restrictions", self)
        # navtb.addAction(self.arrow_down)
        # self.arrow_down.triggered.connect(self.traverse_down)
        # navtb.addSeparator()

        if DEBUG:
            self.kijiji = QtWidgets.QAction(QtGui.QIcon('images/logo_kijiji.svg'), "Kijiji", self)
            navtb.addAction(self.kijiji)
            self.kijiji.triggered.connect(partial(self.navigate_to_page, Kijiji))
            navtb.addSeparator()

            self.craigslist = QtWidgets.QAction(QtGui.QIcon('images/logo_craigslist.png'), "Craigslist", self)
            navtb.addAction(self.craigslist)
            self.craigslist.triggered.connect(partial(self.navigate_to_page, CRAIGSLIST))
            navtb.addSeparator()

            self.webscraperio = QtWidgets.QAction(QtGui.QIcon('images/logo_white.svg'), "webscraper.io", self)
            navtb.addAction(self.webscraperio)
            self.webscraperio.triggered.connect(partial(self.navigate_to_page, WEBSCRAPERIO))
            navtb.addSeparator()

            self.kijiji_auto = QtWidgets.QAction(QtGui.QIcon('images/logo_kijijiauto2.png'), "Kijiji Auto", self)
            navtb.addAction(self.kijiji_auto)
            self.kijiji_auto.triggered.connect(partial(self.navigate_to_page, KIJIJIAUTO))
            navtb.addSeparator()

        left_spacer = QtWidgets.QWidget()
        left_spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        navtb.addWidget(left_spacer)

        # self.intellisense_icon = QtWidgets.QAction(QtGui.QIcon('images/purple-cube.svg'), 'Intellisense', self)
        # navtb.addAction(self.intellisense_icon)
        # self.intellisense_icon.triggered.connect(self.inspect_element)

        self.run = QtWidgets.QAction(QtGui.QIcon('images/play-hot.png'), 'Run', self)
        navtb.addAction(self.run)
        self.run.triggered.connect(self.run_scraper)

    def navigate_to_page(self, page):
        self.browser.setUrl(QtCore.QUrl(page))

    def update_title(self):  # TODO statusbar here
        title = self.browser.page().title()
        self.statusBar().showMessage(title)

    def navigate_home(self):
        self.browser.setUrl(QtCore.QUrl(HOME))

    def navigate_to_url(self):
        q = QtCore.QUrl(self.urlbar.text())
        if q.scheme() == "":
            q.setScheme("http")
        self.browser.setUrl(q)

    def update_urlbar(self, q):
        if q.scheme() == 'https':
            self.httpsicon.setPixmap(QtGui.QPixmap(os.path.join('images', 'shield-lock-fill.svg')))
        else:
            self.httpsicon.setPixmap(QtGui.QPixmap(os.path.join('images', 'shield-slash.png')))

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

    def change_image(self):  # tODO
        image = QtGui.QImage()
        _text = ''
        image_link = ''
        index = self.treemodel_view.tree.selectedIndexes()[0]
        selected_row = index.model().itemFromIndex(index)
        for item in my_data:
            if item['QItem'] == selected_row:
                _text = '\n\n' + item['value'] + '\n'
                if item['image_link'] != '':
                    image_link = item['image_link']
        # try:
        #     if image_link != '':
        #         image.loadFromData(resp(image_link).content)
        #         self.image_label.setPixmap(QtGui.QPixmap(image))
        #     else:
        #         self.image_label.setText(_text)
        # except:
        #     print('messed up getting the image.')

    def return_xpath(self, names, values, xpath, local_name, text, class_name, image, link, parent_name):

        if names or values:
            attributes = dict(zip(str(names).split(","), str(values).split(",")))
        else:
            attributes = None
        # print(parent_name)
        browser_url = self.browser.url().toString()
        # web = urljoin(browser_url, link)
        # print(web)

        url_list = [row['link'] for row in my_data if row['link'] is not None]
        tree_item = {'unique_id': None}

        if browser_url not in url_list:  #
            tree_item['unique_id'] = my_data[-1]['unique_id'] + 1
            tree_item['parent_id'] = 1
            tree_item['column_name'] = 'Column ' + str(my_data[-1]['unique_id'])
            tree_item['url_name'] = browser_url
            tree_item['xpath'] = xpath
            tree_item['value'] = text
            tree_item['link'] = link
            tree_item['class_name'] = class_name
            tree_item['image_link'] = image
            tree_item['local_name'] = local_name
            tree_item['parent_name'] = parent_name
            tree_item['attributes'] = attributes

        for index, row in enumerate(my_data):  # if previously selected link is the current page, add it as a child.
            if row['link'] == browser_url:
                tree_item['unique_id'] = my_data[-1]['unique_id'] + 1
                tree_item['parent_id'] = row['unique_id']
                tree_item['column_name'] = 'Column ' + str(my_data[-1]['unique_id'])
                tree_item['url_name'] = browser_url
                tree_item['xpath'] = xpath
                tree_item['value'] = text
                tree_item['link'] = link
                tree_item['class_name'] = class_name
                tree_item['image_link'] = image
                tree_item['local_name'] = local_name
                tree_item['parent_name'] = parent_name
                tree_item['attributes'] = attributes

        if tree_item['unique_id'] is not None:
            if tree_item not in my_data:  ##########
                print(tree_item)
                self.treemodel_view.create_row(tree_dict=tree_item)
                self.treemodel_view.tree.expandAll()
                url_list.clear()

    def highlight_xpath(self):
        for row in my_data:
            if self.browser.url().toString() == row['url_name']:
                if int(row['combobox'].getComboValue()) == 0:  # single_item change color for operation / pagination.
                    pass
                #     self.page.runJavaScript(single_item(row['xpath']))
                # elif int(row['combobox'].getComboValue()) == 1:  # Multi_item
                #     x = multi_item(row['local_name'], row['attributes'], row['xpath'])[0]
                #     self.page.runJavaScript(x)
                # elif int(row['combobox'].getComboValue()) == 2:  # single_link
                #     self.page.runJavaScript()
                # elif int(row['combobox'].getComboValue()) == 3:  # multi_link
                #     self.page.runJavaScript()
                # elif int(row['combobox'].getComboValue()) == 2:  # pagination
                #     self.page.runJavaScript(single_item(row['xpath'], colors['blue']))

    # def traverse_up(self):
    #     self.treemodel_view.transverse_tree()
        # print('MY_DATA: ')
        # for d in my_data[1:]:
        #     print(d)

        # self.level += 1
        # self.highlight_xpath()

    # def traverse_down(self):
    #     self.level -= 1
    #     self.highlight_xpath()

    def inspect_element(self):
        # TODO import js files like python files for style points.
        # https: // gist.github.com / oakfang / f65e10dd10992045c968
        if self.page.onLoadFinished:
            self.page.runJavaScript(
                """
            document.body.addEventListener('mouseenter', function(e) {
            e = e || window;
            const item = e.target;
            item.addEventListener('mouseover', function (event) {
                event.target.style.backgroundColor = '#21cdff';
            })
            item.addEventListener('mouseout', function (event) {
                event.target.style.backgroundColor = '';
            })
            }, false);
            """)

    def run_scraper(self):
        self.treemodel_view.transverse_tree()
        print('MY_DATA: ')
        for d in my_data:
            print(d)

        print("\n\n============================INITIALIZING SPIDER============================\n\n")
        time.sleep(3)
        print('DONE')
        # self.exec_spider()

    # def exec_spider(self):
    #     print(self.filename,
    #           self.project_name,
    #           self.project_url,
    #           self.file_format,
    #           self.project_uri,
    #           self.domain)

        # SpiderRunner.run_spider(file_format='csv',
        #                         uri='kijiji_honda.csv',
        #                         url=my_data[1].get('url_name'),
        #                         domains=urlparse(my_data[1].get('url_name')).netloc,
        #                         tree_dict=my_data[1:]
        #                         )

    #     """This is the execute button"""
    #     worker = Worker(n, url)
    #     worker.signals.worker_signal.connect(self.display_output)
    #
    #     # Execute
    #     self.threadpool.start(worker)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
