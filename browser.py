

from PyQt5 import QtWidgets, QtWebEngineWidgets, QtGui

DEBUG_CONTEXT = True


class QuteBrowser(QtWebEngineWidgets.QWebEngineView):
    def __init__(self, *args, **kwargs):
        super(QuteBrowser, self).__init__(*args, **kwargs)
        # self.value = value
        # self.setUrl(QtCore.QUrl("http://google.com"))

    def contextMenuEvent(self, event):
        try:
            self.menu = QtWebEngineWidgets.QWebEnginePage.createStandardContextMenu(self.page())
            self.custom_menu = QtWidgets.QAction(QtGui.QIcon('images/diagram-3-fill.svg'), "TreeView", self)
            self.custom_menu.triggered.connect(self.customMenuAction)
            self.menu.addAction(self.custom_menu)
            self.menu.exec_(self.mapToGlobal(event.pos()))
        except:
            print('Error at ContextMenu Event')

    def customMenuAction(self):
        print('lalalalla')
        # self.value.js_exec.connect(self.return_left_click)


    # def return_left_click(self, names):
    #     print('LEFTCLICK: ', names)

# https://doc.qt.io/qt-5/qtwebengine-webenginewidgets-simplebrowser-example.html


# class MainWindow(QtWidgets.QMainWindow):
#     def __init__(self, *args, **kwargs):
#         super(MainWindow, self).__init__(*args, **kwargs)
#         self.browser = QuteBrowser()
#         self.setCentralWidget(self.browser)
#         self.show()


# app = QtWidgets.QApplication(sys.argv)
# window = MainWindow()
# app.exec_()
