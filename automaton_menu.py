from PyQt5.QtWidgets import QAction, QMainWindow


class MenuBar(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MenuBar, self).__init__(*args, **kwargs)

    def initUI(self):
        self.createActions()
        self.createMenus()
        self.setTitle()

    def createActions(self):
        """Create basic `File` and `Edit` actions"""
        self.actNew = QAction('&New', self, shortcut='Ctrl+N', statusTip="Create new graph", triggered=self.onFileNew)
        self.actOpen = QAction('&Open', self, shortcut='Ctrl+O', statusTip="Open file", triggered=self.onFileOpen)
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

    def createFileMenu(self):
        menubar = self.menuBar()
        self.fileMenu = menubar.addMenu('&File')
        self.fileMenu.addAction(self.actNew)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.actOpen)
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

    def setTitle(self):
        """Function responsible for setting window title"""
        title = "Automaton - "
        title += "Project Name"
        self.setWindowTitle(title)

    def onSettings(self):
        print('Make changes to settings')

    def closeApp(self):
        print('ask to save and shutdown, discard and shutdown or cancel')

    def onFileNew(self):
        print("create and save new file")

    def onFileOpen(self):
        print("Open file")

    def onFileSave(self):
        print("save file")

    def onFileSaveAs(self):
        print('save file as')

    def onEditUndo(self):
        print('Edit Undo: wtf is this supposed to do')

    def onEditRedo(self):
        print('Edit Redo: wtf is this supposed to do')

    def onEditDelete(self):
        print('Edit delete: wtf is this soppos to do')

    def onEditCut(self):
        print('Cut')

    def onEditCopy(self):
        print('Copy')

    def onEditPaste(self):
        print('Paste')

