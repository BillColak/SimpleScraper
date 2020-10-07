import sys
from collections import deque
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from functools import partial

from data_file import my_data, my_dict_data


class comboTree(QComboBox):
    def __init__(self, parent):
        super().__init__(parent)
        self.addItems(['Item', 'Multi-Item', 'Pagination'])
        # self.currentIndexChanged.connect(self.getComboValue)

    def getComboValue(self):
        # print(self.currentIndex(), self.currentText())
        return self.currentIndex()


class MyDelegate(QStyledItemDelegate):

    def sizeHint(self, option, index):
        my_fixed_height = 30
        size = super(MyDelegate, self).sizeHint(option, index)
        size.setHeight(my_fixed_height)
        return size


class view(QWidget):

    def __init__(self, data):
        super(view, self).__init__()
        self.tree = QTreeView(self)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.openMenu)
        layout = QVBoxLayout(self)
        layout.addWidget(self.tree)
        layout.setContentsMargins(0,0,0,0)

        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['Web Site', 'Value', 'XPath', 'Operation', 'IntelliSense'])
        self.tree.header().setSectionResizeMode(QHeaderView.Stretch)
        # self.tree.header().setSectionResizeMode(QHeaderView.Interactive)

        self.tree.setItemDelegate(MyDelegate(self.tree))
        self.tree.header().setDefaultAlignment(Qt.AlignCenter)
        self.tree.setModel(self.model)
        self.font = QFont("Arial", 12)
        self.tree.setFont(self.font)

        self.seen = dict()
        self.combodict = {}
        self.add_row(my_data[0])

    def create_row(self, row, tree_dict:dict=None, item_one=None):  # your basically gonna give a dict of what to write thats it. this will do the rest.

        unique_id = tree_dict['unique_id']
        if unique_id == 1:
            parent = self.model.invisibleRootItem()
        else:
            parent_id = tree_dict['parent_id']
            parent = self.seen[parent_id]

        if item_one is not None:  # reserved for insert up/down or child, USE PARTIAL FUNCTION.
            pass

        if tree_dict is not None:  # for when element is clicked from website
            comboItem = QStandardItem()
            parent.appendRow([
                QStandardItem(tree_dict['url_name']),
                QStandardItem(tree_dict['value']),
                QStandardItem(tree_dict['xpath']),
                comboItem,
            ])
            if unique_id > 1:
                combobox = comboTree(self)
                tree_dict['combobox'] = combobox
                self.tree.setIndexWidget(comboItem.index(), combobox)


    def add_row(self, tree_dict, root=None):
        if root is None:
            root = self.model.invisibleRootItem()

        unique_id = tree_dict['unique_id']
        if unique_id == 1:
            parent = root
        else:
            parent_id = tree_dict['parent_id']
            parent = self.seen[parent_id]
        comboItem = QStandardItem()
        parent.appendRow([
            QStandardItem(tree_dict['url_name']),
            QStandardItem(tree_dict['value']),
            QStandardItem(tree_dict['xpath']),
            comboItem,
        ])
        self.seen[unique_id] = parent.child(parent.rowCount() - 1)
        if unique_id > 1:
            combobox = comboTree(self)
            # tree_dict['combobox'] = combobox  # Can't import project from file, if you do this.
            self.combodict[unique_id] = combobox
            self.tree.setIndexWidget(comboItem.index(), combobox)

    # Function to save populate treeview with a dictionary
    def importData(self, my_data, root=None):  # note: this function works well because it does the tree traversal in one go. so the parent is always known.
        print('IMPORT DATA:   ')
        self.model.setRowCount(0)
        if root is None:
            root = self.model.invisibleRootItem()
        # seen = {}   # List of  QStandardItem
        values = deque(my_data)  # it's dequeing so only show the immediate parent child relationship.
        while values:
            value = values.popleft()
            if value['unique_id'] == 1:
                parent = root
            else:
                parent_id = value['parent_id']  # this is where you tell who the parent is...
                if parent_id not in self.seen:  # if parent got popped off earlier in the traversal, add it back in.
                    values.append(value)
                    continue
                parent = self.seen[parent_id]  # so there is a parent and a unique id and if they match thats where the child goes. and they match becuase thier just stupid intergers
                print('Parent: ', parent.data(0))
            unique_id = value['unique_id']
            # id_item = QStandardItem(str(unique_id))
            # id_item.setEditable(False)
            parent.appendRow([
                QStandardItem(value['url_name']),
                QStandardItem(value['value']),
                QStandardItem(value['xpath']),
                # id_item
            ])
            self.seen[unique_id] = parent.child(parent.rowCount() - 1)  # which means, when parent id == unique id.
            print(parent.child(parent.rowCount() - 1).data(0))
            print(self.seen)

    # Function to add right click menu to treeview item
    def openMenu(self, position):
            indexes = self.sender().selectedIndexes()
            mdlIdx = self.tree.indexAt(position)

            if not mdlIdx.isValid():
                return
            item = self.model.itemFromIndex(mdlIdx)  # this gets the specific cell value, but to do operations, need col1 item.
            if len(indexes) > 0:
                level = 0
                index = indexes[0]
                if index.isValid():
                    item_one = self.model.itemFromIndex(indexes[0])
                while index.parent().isValid():
                    index = index.parent()
                    level += 1
            else:
                level = 0
            right_click_menu = QMenu()
            act_add = right_click_menu.addAction(self.tr("Add Child Item"))
            act_add.triggered.connect(partial(self.TreeItem_Add, item_one))
            if item.parent() != None:
                insert_up = right_click_menu.addAction(self.tr("Insert Item Above"))
                insert_up.triggered.connect(partial(self.TreeItem_InsertUp, item_one))
                insert_down = right_click_menu.addAction(self.tr("Insert Item Below"))
                insert_down.triggered.connect(partial(self.TreeItem_InsertDown, item_one))
                act_del = right_click_menu.addAction(self.tr("Delete Item"))
                act_del.triggered.connect(partial(self.TreeItem_Delete, item_one))
            right_click_menu.exec_(self.sender().viewport().mapToGlobal(position))

    # # Function to add child item to treeview item
    def TreeItem_Add(self, item_one):
        unique_id = my_data[-1]['unique_id'] + 1
        url_name = QStandardItem('xx')
        value = QStandardItem('xx')
        xpath = QStandardItem('xx')
        comboItem = QStandardItem()
        # selecteditem = self.model.itemFromIndex(mdlIdx)
        item_one.appendRow([url_name, value, xpath, comboItem])
        self.tree.expandAll()
        self.seen[unique_id] = item_one.child(item_one.rowCount() - 1)

        combobox = comboTree(self)
        self.combodict[unique_id] = combobox
        self.tree.setIndexWidget(comboItem.index(), combobox)

        # finding the index of the selected which is also the parent item so it can be added to my_data.
        tree_dict = {"unique_id": unique_id, 'parent_id': None, 'url_name': 'xx', 'xpath': 'xx', 'value': 'xx', 'link': None, 'image_link': ''}
        # index = indexes[0]
        # val = self.model.itemFromIndex(index)
        for k, v in self.seen.items():
            if v == item_one:
                tree_dict['parent_id'] = k
        my_data.append(tree_dict)

    # Function to Insert sibling item above to treeview item
    def TreeItem_InsertUp(self, item_one):  # TODO use add_row to optimise the code.
        unique_id = my_data[-1]['unique_id'] + 1
        temp_key = QStandardItem('xx')
        temp_value1 = QStandardItem('xx')
        temp_value2 = QStandardItem('xx')
        comboItem = QStandardItem()
        current_row = item_one.row()
        parent = item_one.parent()
        parent.insertRow(current_row, [temp_key, temp_value1, temp_value2, comboItem])
        self.tree.expandAll()
        print(parent.rowCount(), current_row)

        self.seen[unique_id] = parent.child(current_row)  # this is the problem -> if its not already in self.seen, this is still the problem, check self.seen for duplicates
  # now some items are not getting deleted
        combobox = comboTree(self)
        self.combodict[unique_id] = combobox
        self.tree.setIndexWidget(comboItem.index(), combobox)

        tree_dict = {"unique_id": unique_id, 'parent_id': None, 'url_name': 'xx', 'xpath': 'xx', 'value': 'xx', 'link': None, 'image_link': ''}
        for k, v in self.seen.items():
            if v == parent:
                tree_dict['parent_id'] = k
        my_data.append(tree_dict)

    # Function to Insert sibling item above to treeview item
    def TreeItem_InsertDown(self, item_one):
        unique_id = my_data[-1]['unique_id'] + 1
        temp_key = QStandardItem('xx')
        temp_value1 = QStandardItem('xx')
        temp_value2 = QStandardItem('xx')
        comboItem = QStandardItem()
        current_row = item_one.row()
        parent = item_one.parent()
        parent.insertRow(current_row + 1, [temp_key, temp_value1, temp_value2, comboItem])
        self.tree.expandAll()
        self.seen[unique_id] = parent.child(parent.rowCount() - 1)
        # self.seen[unique_id] = self.model.itemFromIndex(mdlIdx)  # ^Both techniques work

        combobox = comboTree(self)
        self.combodict[unique_id] = combobox
        self.tree.setIndexWidget(comboItem.index(), combobox)

        tree_dict = {"unique_id": unique_id, 'parent_id': None, 'url_name': 'xx', 'xpath': 'xx', 'value': 'xx', 'link': None, 'image_link': ''}
        # val = self.model.itemFromIndex(mdlIdx).parent()
        for k, v in self.seen.items():
            if v == parent:
                tree_dict['parent_id'] = k
        my_data.append(tree_dict)

    # Function to Delete item
    def TreeItem_Delete(self, item_one):
        if item_one != None:
            if item_one.hasChildren():
                for i in range(item_one.rowCount()):
                    childitem = item_one.child(i)
                    if childitem != None:
                        for k, v in list(self.seen.items()):
                            if v == childitem:
                                for index, row in enumerate(my_data):
                                    if row['unique_id'] == k:
                                        x = my_data.pop(index)
                                del self.seen[k], self.combodict[k]

            for k, v in list(self.seen.items()):
                if v == item_one:
                    for index, row in enumerate(my_data):
                        if row['unique_id'] == k:
                            x = my_data.pop(index)
                            print('item deleted')
                    del self.seen[k], self.combodict[k]

        item_one.parent().removeRow(item_one.row())

    # Function to transverse treeview and derive tree_list
    def transverse_tree(self):  # TODO this is the serialization function.
        tree_list = []
        for i in range(self.model.rowCount()):
            item = self.model.item(i)
            level = 0
            self.GetItem(item, level, tree_list)

        for j in tree_list:
            for i in my_data:
                if str(i['unique_id']) == str(j['unique_id']):
                    i['operation'] = self.combodict[i['unique_id']].getComboValue()
                    i['url_name'] = j['url_name']
                    i['value'] = j['value']
                    i['xpath'] = j['xpath']

        print("Transverse Tree: ")
        for row in tree_list:
            print(row)

    def GetItem(self, item, level, tree_list):   # Does not represent parent accurately
        if item != None:
            if item.hasChildren():
                level = level + 1
                url_name = ' '
                value = ' '
                xpath = ' '
                row_id = ' '
                id = 0  # This id only get the item relative to the parent
                for i in range(item.rowCount()):
                    childrow = item.child(i)
                    id = id + 1
                    for j in reversed([0, 1, 2, 3]):  # parent.columnCount()
                        tree_dict = {}
                        childitem = item.child(i, j)
                        if childitem != None:
                            if j == 0:
                                url_name = childitem.data(0)
                            else:
                                url_name = url_name
                            if j == 1:
                                value = childitem.data(0)
                            else:
                                value = value
                            if j == 2:
                                xpath = childitem.data(0)
                            else:
                                xpath = xpath
                            if j == 3:
                                row_id = id
                                # for k, v in self.seen.items():
                                #     if v == childrow:
                                #         print('j:3: ',k,v,childrow)
                                #         # tree_dict['operation'] = self.combodict[k].getComboValue()
                                #         tree_dict['unique_id'] = k
                            else:
                                row_id = row_id
                            if j == 0:
                                for k, v in self.seen.items():
                                    if v == childrow:
                                        # print('j:0: ', v, childrow)
                                        tree_dict['operation'] = self.combodict[k].getComboValue()
                                        tree_dict['unique_id'] = k
                                tree_dict['parent_id'] = level  # TODO this is wrong
                                tree_dict['url_name'] = url_name
                                tree_dict['value'] = value
                                tree_dict['xpath'] = xpath
                                tree_list.append(tree_dict)
                            self.GetItem(childitem, level, tree_list)
                return tree_list

    # def resizeEvent(self, event):
    #     super(view, self).resizeEvent(event)
    #     tableSize = self.tree.width()
    #     sideHeaderWidth = self.tree.header().width()
    #     tableSize -= sideHeaderWidth
    #     numberOfColumns = self.model.columnCount()
    #
    #     remainingWidth = tableSize % numberOfColumns
    #     for columnNum in range(self.model.columnCount()):
    #         if remainingWidth > 0:
    #             self.tree.setColumnWidth(columnNum, int(tableSize/numberOfColumns) + 1 )
    #             remainingWidth -= 1
    #         else:
    #             self.tree.setColumnWidth(columnNum, int(tableSize/numberOfColumns) )
