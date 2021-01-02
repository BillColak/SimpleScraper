from PyQt5.QtWidgets import QAction, QMainWindow, QFileDialog, QDialog, QDialogButtonBox, QGridLayout, QLineEdit, QLabel, QToolButton, QStyle, QComboBox, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSignal, Qt
from data_file import my_data

from functools import partial
from treeview_model import view
# from urllib.parse import urlparse
import os
import json


# TODO when a new project is made the treeview project does not change.


class InvalidFile(Exception): pass


class MenuBar(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MenuBar, self).__init__(*args, **kwargs)
        self.setWindowTitle('Automaton')

        self.treemodel_view = view()
        self.project = None  # TODO
        # self.filename = None
        # self.project_name = None
        # self.project_url = None
        # self.file_format = None
        # self.project_uri = None
        # self.domain = None

    def initUI(self):
        self.createActions()
        self.createMenus()

    def createActions(self):
        """Create basic `File` and `Edit` actions"""
        self.actNew = QAction('&New', self, shortcut='Ctrl+N', statusTip="Create new graph", triggered=self.onFileNew)
        # self.actOpen = QAction('&Open', self, shortcut='Ctrl+O', statusTip="Open file", triggered=self.onFileOpen)
        self.actSave = QAction('&Save', self, shortcut='Ctrl+S', statusTip="Save file", triggered=self.onFileSave)
        self.actSaveAs = QAction('Save &As...', self, shortcut='Ctrl+Shift+S', statusTip="Save file as...", triggered=self.onFileSaveAs)
        self.settings = QAction('&Settings', self, shortcut='Ctrl+Alt+S', statusTip="Project settings", triggered=self.onSettings)
        self.actExit = QAction('E&xit', self, shortcut='Ctrl+Q', statusTip="Exit application", triggered=self.closeApp)

        self.actUndo = QAction('&Undo', self, shortcut='Ctrl+Z', statusTip="Undo last operation", triggered=self.onEditUndo)
        self.actRedo = QAction('&Redo', self, shortcut='Ctrl+Shift+Z', statusTip="Redo last operation", triggered=self.onEditRedo)
        self.actCut = QAction('Cu&t', self, shortcut='Ctrl+X', statusTip="Cut to clipboard", triggered=self.onEditCut)
        self.actCopy = QAction('&Copy', self, shortcut='Ctrl+C', statusTip="Copy to clipboard", triggered=self.onEditCopy)
        self.actPaste = QAction('&Paste', self, shortcut='Ctrl+V', statusTip="Paste from clipboard", triggered=self.onEditPaste)
        self.actDelete = QAction('&Delete', self, shortcut='Del', statusTip="Delete selected items", triggered=self.onEditDelete)

    def createMenus(self):
        """Create Menus for `File` and `Edit`"""
        self.createFileMenu()
        self.createEditMenu()
        self.createOpenMenu()

    def createFileMenu(self):
        menubar = self.menuBar()
        self.fileMenu = menubar.addMenu('&File')
        self.fileMenu.addAction(self.actNew)
        self.fileMenu.addSeparator()
        # self.openprojectmenu = menubar.addMenu('&Open')
        self.openprojectmenu = self.fileMenu.addMenu('&Open')
        # self.fileMenu.addAction(self.actOpen)
        self.fileMenu.addAction(self.actSave)
        self.fileMenu.addAction(self.actSaveAs)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.settings)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.actExit)

    def createEditMenu(self):
        menubar = self.menuBar()
        self.editMenu = menubar.addMenu('&Edit')
        self.editMenu.addAction(self.actUndo)
        self.editMenu.addAction(self.actRedo)
        self.editMenu.addSeparator()
        self.editMenu.addAction(self.actCut)
        self.editMenu.addAction(self.actCopy)
        self.editMenu.addAction(self.actPaste)
        self.editMenu.addSeparator()
        self.editMenu.addAction(self.actDelete)

    def createOpenMenu(self):
        dirlist = os.listdir(os.path.join(os.path.dirname(__file__), 'projects'))
        for p in dirlist:
            project = p.split('.')[0]
            self.openprojectmenu.addAction(QAction(project, self, statusTip=f"Open file {project}", triggered=partial(self.onFileOpen, p)))

    # def createSettingMenu(self):
    #     menubar = self.menuBar()
    #     self.settingMenu = menubar.addMenu('&Setting')
    #     self.themesMenu = self.settingMenu.addMenu('&Themes')

    def setTitle(self, filename: str):
        """Function responsible for setting window title"""
        title = "Automaton"
        if filename is not None:
            title += " - " + filename
        self.setWindowTitle(title)

    def onSettings(self, s):
        print("click", s)
        settings = SettingDialog(self)
        if settings.exec_():
            print("Success!")
        else:
            print("Cancel!")

    def closeApp(self):
        print('ask to save and shutdown, discard and shutdown or cancel')

    def onFileNew(self, s):
        print("Click: ", s)
        dlg = NewProjectDialog(self)
        if dlg.exec_():
            self.filename = dlg.fname
            self.project_name = os.path.basename(self.filename)
            self.setTitle(self.project_name)
            # self.filename = dlg.filepath
            # self.project_name = dlg.project_name

        else:
            print("Cancel!")

    def getFileDialogDirectory(self):
        """Returns starting directory for ``QFileDialog`` file open/save"""
        return ''

    def getFileDialogFilter(self):
        """Returns ``str`` standard file open/save filter for ``QFileDialog``"""
        return 'CSV (*.csv);;JSON (*.json);;All files (*.*)'

    def onFileSave(self):
        print("save file")  # todo

   #OPEN FOLDER
    def onFileOpen(self, p):
        project = os.path.join(os.path.dirname(__file__), 'projects')
        filepath = os.path.join(project, p)
        print('selected project: ', os.path.join(project, p))
        # file = FileHandler(filepath) # why isn;t this working....
        # file.savefile()
        with open(filepath, 'r') as file:
            raw_data = file.read()
            try:
                data = json.loads(raw_data, encoding='utf-8')
                self.treemodel_view.importData(data)
            except json.JSONDecodeError:
                raise InvalidFile("%s is not a valid JSON file" % os.path.basename(filepath))

        # pass
        # self.treemodel_view.transverse_tree()
        # filename, _filter = QFileDialog.getOpenFileName(self, 'Open Project from file', self.getFileDialogDirectory(), self.getFileDialogFilter())
        # if filename == '':
        #     return False
        # else:
        #     with open(filename, "r") as file:
        #         raw_data = file.read()
        #         try:
        #             data = json.loads(raw_data, encoding='utf-8')
        #             self.treemodel_view.importData(data)
        #         except json.JSONDecodeError:
        #             raise InvalidFile("%s is not a valid JSON file" % os.path.basename(filename))
        #
        #     if filename is not None:
        #         self.filename = filename  # ful file path
        #         self.project_name = data[0]['url_name']  # name of the file
        #         self.file_format = str(self.filename).split('.')[-1]  # file extension / format
        #         self.project_uri = str(self.filename).split('/')[-1]  # file name with extension
        #         if len(data) > 1:
        #             self.domain = urlparse(data[1].get('url_name')).netloc
        #             self.project_url = data[1].get('url_name')

    # SAVE FOLDER AS
    def onFileSaveAs(self):
        self.treemodel_view.transverse_tree()
        fname, filter_ = QFileDialog.getSaveFileName(self, 'Save Project to file & file type', self.getFileDialogDirectory(), self.getFileDialogFilter())
        if fname == '':
            return False
        else:
            self.fileSave(fname)
        print('save file as')

    def fileSave(self, filename: str = None):
        file = FileHandler(filename)
        file.savefile()
        # if filename is not None:
        #     self.filename = filename
        #     with open(self.filename, "w") as file:
        #         pass
        #     project_name = filename.split('/')[-1].split('.')[0]
        #     self.project_name = os.path.join('projects', f'{project_name}.json')  # => does this actually work?
        #
        # with open(self.project_name, "w") as project:
        #     for idx, i in enumerate(my_data):
        #         if i.get('QItem', None) is not None:
        #             i.pop('QItem')
        #     my_data[0]['url_name'] = filename
        #     json.dump(my_data, project, indent=4)
        #     print("saving to", filename, "was successful.")
        # return True


    def onEditUndo(self):
        print('Edit Undo: wtf is this supposed to do')

    def onEditRedo(self):
        print('Edit Redo: wtf is this supposed to do')

    def onEditDelete(self):
        print('Edit delete: wtf is this suppose to do')

    def onEditCut(self):
        print('Cut')

    def onEditCopy(self):
        print('Copy')

    def onEditPaste(self):
        print('Paste')

    def show_popup(self, alert: str = None):
        msg = QMessageBox()
        msg.setWindowTitle('Invalid Operation')
        if alert:
            msg.setText(alert)
        else:
            msg.setText('Please provide a valid file name!')
        msg.setStandardButtons(QMessageBox.Ok)
        x = msg.exec_()


class SettingDialog(QDialog):

    def __init__(self, *args, **kwargs):
        super(SettingDialog, self).__init__(*args, **kwargs)
        # The operation done in the dialog will only change the settings.json file instead of some methods n shit.

        self.filename = None
        self.setWindowTitle("Settings")
        self.resize(600, 300)

        theme_options = QLabel('Theme Options: ')  # so this will only
        self.combobox = QComboBox()
        self.combobox.addItems(['darkblue', 'darkgray', 'darkorange', 'qdark'])

        buttons = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(buttons)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QGridLayout()
        self.layout.addWidget(theme_options, 0, 0)
        self.layout.addWidget(self.combobox, 0, 1)
        self.layout.addWidget(self.buttonBox, 2, 1)
        self.setLayout(self.layout)

    def accept(self):
        super().accept()
        file = self.combobox.currentText()
        filetheme = f'{file}.css'
        filetheme2 = os.path.join('themes', filetheme)
        print(filetheme, filetheme2)


class NewProjectDialog(QDialog, MenuBar):

    def __init__(self, *args, **kwargs):
        super(NewProjectDialog, self).__init__(*args, **kwargs)

        self.setWindowTitle("New Project")
        self.resize(600, 300)

        self.fname = None

        self.project_location_label = QLabel('Output Location: ')
        self.project_location_lineEdit = ButtonLineEdit(QIcon(os.path.join('images', 'openfile - Copy.svg')))
        self.project_location_lineEdit.buttonClicked.connect(self.save_new_project)

        buttons = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(buttons)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QGridLayout()
        self.layout.addWidget(self.project_location_label, 0, 0)
        self.layout.addWidget(self.project_location_lineEdit, 0, 1)
        self.layout.addWidget(self.buttonBox, 2, 1)
        self.setLayout(self.layout)

    def accept(self):
        super().accept()

        if self.project_location_lineEdit.text() != '' and self.fname is None:
            self.fname = os.path.join(os.path.dirname(__file__), f'{self.project_location_lineEdit.text()}.csv')
        elif self.project_location_lineEdit.text() == '':
            self.show_popup()
            return False

        file = FileHandler(self.fname)
        file.savefile()

    def save_new_project(self):
        self.fname, filter_ = QFileDialog.getSaveFileName(self, 'Save Project to file & file type', self.getFileDialogDirectory(), 'CSV (*.csv)')
        if self.fname != '':
            self.project_location_lineEdit.setText(str(self.fname))
        # else:
        #     self.show_popup()
            # return False
        # else:
        #     self.project_location_lineEdit.setText(str(self.fname))

    # def fileSave(self, filename: str = None):
    #     print('base: ', os.path.basename(filename), 'dirname: ', os.path.dirname(filename))
    #     if filename is not None:
    #         self.filepath = filename
    #
    #         with open(self.filepath, "w") as file:
    #             pass
    #
    #         self.project_name = filename.split('/')[-1].split('.')[0]
    #         my_data[0]['url_name'] = self.project_name
    #
    #         self.treemodel_view.importData(my_data)
    #         project_name = os.path.join('projects', f'{self.project_name}.json')
    #
    #         with open(project_name, "w") as project:
    #             for idx, i in enumerate(my_data):
    #                 if i.get('QItem', None) is not None:
    #                     i.pop('QItem')
    #
    #             json.dump(my_data, project, indent=4)
    #             print("saving to", filename, "was successful.")
    #
    #             return True


class ButtonLineEdit(QLineEdit):
    buttonClicked = pyqtSignal(bool)

    def __init__(self, icon_file, parent=None):
        super(ButtonLineEdit, self).__init__(parent)

        self.button = QToolButton(self)
        self.button.setIcon(QIcon(icon_file))
        self.button.setStyleSheet('border: 0px; padding: 0px; background-color:rgba(0,0,0,0);')

        self.button.setCursor(Qt.PointingHandCursor)
        self.button.clicked.connect(self.buttonClicked.emit)

        frameWidth = self.style().pixelMetric(QStyle.PM_DefaultFrameWidth)
        buttonSize = self.button.sizeHint()

        self.setStyleSheet('QLineEdit {padding-right: %dpx; }' % (buttonSize.width() + frameWidth + 1))
        self.setMinimumSize(max(self.minimumSizeHint().width(), buttonSize.width() + frameWidth*2 + 2),
                            max(self.minimumSizeHint().height(), buttonSize.height() + frameWidth*2 + 2))

    def resizeEvent(self, event):
        buttonSize = self.button.sizeHint()
        frameWidth = self.style().pixelMetric(QStyle.PM_DefaultFrameWidth)
        self.button.move(self.rect().right() - frameWidth - buttonSize.width(),
                         (self.rect().bottom() - buttonSize.height() + 1)/2)
        super(ButtonLineEdit, self).resizeEvent(event)


class FileHandler:
    def __init__(self, file):
        self.treemodel_view = view()
        self.file = file

    def savefile(self):
        if self.file is not None:
            if os.path.exists(self.file):  # if file exists open file
                with open(self.file, "r") as file:
                    raw_data = file.read()
                    try:
                        data = json.loads(raw_data, encoding='utf-8')
                        self.treemodel_view.importData(data)
                    except json.JSONDecodeError:
                        raise InvalidFile("%s is not a valid JSON file" % os.path.basename(self.file))

            else:  # if file does not exist, create a new one.
                with open(self.file, "w") as file: pass  # make the csv

                name = os.path.basename(self.file).split('.')[0]
                my_data[0]['url_name'] = name
                my_data[0]['project_name'] = name
                my_data[0]['output_location'] = self.file

                self.treemodel_view.importData(my_data)
                project_file = os.path.join('projects', f'{name}.json')
                with open(project_file, "w") as project:
                    for i in my_data:
                        if i.get('QItem', None) is not None:
                            i.pop('QItem')
                    json.dump(my_data, project, indent=4)
                    print("saving to", self.file, "was successful.")



