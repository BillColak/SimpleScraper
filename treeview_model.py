import sys
from collections import deque
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from functools import partial

from data_file import my_data


class comboTree(QComboBox):
    def __init__(self, parent):
        super().__init__(parent)
        self.addItems(['Multi-Item', 'Pagination'])
        self.currentIndexChanged.connect(self.getComboValue)

    def getComboValue(self):
        print(self.currentText(), self.currentIndex())
        # return self.currentText()
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
        self.model.setHorizontalHeaderLabels(['Web Site', 'Value', 'XPath', 'Index'])
        self.tree.header().setDefaultSectionSize(300)
        self.tree.header().setStretchLastSection(False)

        self.tree.setItemDelegate(MyDelegate(self.tree))
        self.tree.header().setDefaultAlignment(Qt.AlignCenter)
        self.tree.setModel(self.model)
        self.font = QFont("Arial", 12)
        self.tree.setFont(self.font)

        self.seen = {}
        self.combodict = {}
        self.add_row(my_data[0])

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
            self.combobox = comboTree(self)
            self.combodict[unique_id] = self.combobox
            self.tree.setIndexWidget(comboItem.index(), self.combobox)

        for k,v in self.combodict.items():
            v.getComboValue()

        # x = self.model.itemFromIndex(comboItem.index())
        # y = self.tree.indexWidget(comboItem.index())
        # z = self.model.indexFromItem(comboItem)
        # k = self.tree.model().itemFromIndex(comboItem.index())
        # t = comboItem.index()


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
        # self.tree_list = self.transverse_tree()

    # Function to add right click menu to treeview item
    def openMenu(self, position):
            indexes = self.sender().selectedIndexes()
            mdlIdx = self.tree.indexAt(position)
            # print(indexes, mdlIdx, position)
            if not mdlIdx.isValid():
                return
            item = self.model.itemFromIndex(mdlIdx)
            if len(indexes) > 0:
                level = 0
                index = indexes[0]
                while index.parent().isValid():
                    index = index.parent()
                    level += 1
            else:
                level = 0
            right_click_menu = QMenu()
            act_add = right_click_menu.addAction(self.tr("Add Child Item"))
            act_add.triggered.connect(partial(self.TreeItem_Add, level, mdlIdx))
            if item.parent() != None:
                insert_up = right_click_menu.addAction(self.tr("Insert Item Above"))
                insert_up.triggered.connect(partial(self.TreeItem_InsertUp, level, mdlIdx))
                insert_down = right_click_menu.addAction(self.tr("Insert Item Below"))
                insert_down.triggered.connect(partial(self.TreeItem_InsertDown, level, mdlIdx))
                act_del = right_click_menu.addAction(self.tr("Delete Item"))
                act_del.triggered.connect(partial(self.TreeItem_Delete, item))
            right_click_menu.exec_(self.sender().viewport().mapToGlobal(position))

    # # Function to add child item to treeview item
    def TreeItem_Add(self, level, mdlIdx):
        # unique_id = my_data[-1]['unique_id'] + 1
        url_name = QStandardItem('xx')
        value = QStandardItem('xx')
        xpath = QStandardItem('xx')
        # ID = QStandardItem(str(unique_id))
        # self.model.itemFromIndex(mdlIdx).appendRow([url_name, value, xpath, ID])
        self.model.itemFromIndex(mdlIdx).appendRow([url_name, value, xpath])
        self.tree.expandAll()
        # current_row = self.model.itemFromIndex(mdlIdx).row()
        # print('current row: ', current_row, level)
        # tree_list = self.transverse_tree()
        # print('next id', len(tree_list) + 1)
        # tree_dict = {'unique_id': unique_id, 'value': 'xx', 'xpath': 'xx', }

    # Function to Insert sibling item above to treeview item
    def TreeItem_InsertUp(self, level, mdlIdx):
        level = level - 1
        current_row = self.model.itemFromIndex(mdlIdx).row()
        temp_key = QStandardItem('xx')
        temp_value1 = QStandardItem('xx')
        temp_value2 = QStandardItem('xx')
        temp_value3 = QStandardItem('xx')
        self.model.itemFromIndex(mdlIdx).parent().insertRow(current_row, [temp_key, temp_value1, temp_value2, temp_value3])
        self.tree.expandToDepth(1 + level)
        # self.tree_list = self.transverse_tree()

    # Function to Insert sibling item above to treeview item
    def TreeItem_InsertDown(self, level, mdlIdx):
        unique_id = my_data[-1]['unique_id'] + 1
        level = level - 1
        temp_key = QStandardItem('xx')
        temp_value1 = QStandardItem('xx')
        temp_value2 = QStandardItem('xx')
        # temp_value3 = QStandardItem(str(unique_id))
        current_row = self.model.itemFromIndex(mdlIdx).row()
        # self.model.itemFromIndex(mdlIdx).parent().insertRow(current_row + 1, [temp_key, temp_value1, temp_value2, temp_value3])
        self.model.itemFromIndex(mdlIdx).parent().insertRow(current_row + 1, [temp_key, temp_value1, temp_value2])
        self.tree.expandToDepth(1 + level)

        self.seen[unique_id] = self.model.itemFromIndex(mdlIdx)

        tree_dict = {"unique_id": unique_id, 'parent_id': None, 'url_name': 'xx', 'xpath': 'xx', 'value': 'xx', 'link': None}
        val = self.model.itemFromIndex(mdlIdx).parent()
        for k, v in self.seen.items():
            if v == val:  # the trick is to compare objects in memory.
                tree_dict['parent_id'] = k
        my_data.append(tree_dict)
        # print(self.seen)
        # for d in my_data:
        #     print(d)

        # self.transverse_tree()


    # Function to Delete item
    def TreeItem_Delete(self, item):
        item.parent().removeRow(item.row())

    # Function to transverse treeview and derive tree_list
    def transverse_tree(self):
        tree_list = []
        for i in range(self.model.rowCount()):
            item = self.model.item(i)
            level = 0
            self.GetItem(item, level, tree_list)

        # for j in tree_list:
        #     for i in my_data:
        #         if str(i['unique_id']) == str(j['unique_id']):  #
        #             i['parent_id'] = j['parent_id']
        #             i['url_name'] = j['url_name']
        #             i['value'] = j['value']
        #             i['xpath'] = j['xpath']

                # if int(j['unique_id']) > int(i['unique_id']):
                #     print('ADD TO DICT: ', i['unique_id'], j['unique_id'], '|', i['value'], ':', j['value'])

                #     tree_dict = j
        # my_data.append(tree_dict)

        print("Transverse Tree: ")
        for row in tree_list:
            print(row)
        return tree_list

    def GetItem(self, item, level, tree_list):   # Does not represent parent accurately
        if item != None:
            if item.hasChildren():
                level = level + 1
                url_name = ' '
                value = ' '
                xpath = ' '
                row_id = ' '
                id = 0
                for i in range(item.rowCount()):
                    id = id + 1
                    for j in reversed([0, 1, 2, 3]):
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
                                row_id = childitem.getComboValue(self)
                            else:
                                row_id = row_id
                            if j == 0:
                                tree_dict = {}
                                tree_dict['unique_id'] = row_id
                                tree_dict['parent_id'] = level
                                tree_dict['url_name'] = url_name
                                tree_dict['value'] = value
                                tree_dict['xpath'] = xpath
                                tree_list.append(tree_dict)
                            self.GetItem(childitem, level, tree_list)
                return tree_list
