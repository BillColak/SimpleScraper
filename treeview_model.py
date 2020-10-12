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
        self.addItems(['Item', 'Multi-Item', 'Link', 'Multi-link', 'Pagination'])
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

    # def __init__(self, data):
    def __init__(self):
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
        xoxo = QStandardItem('xx')

        # self.seen = dict()
        # self.combodict = {}
        self.create_row(my_data[0])

    def create_row(self, tree_dict=None, item_one=None, row=None):
        # so basically only memory items are added here?

        if tree_dict is None:
            combobox = comboTree(self)
            parent = item_one.parent()

            url_name = QStandardItem('xx')
            value = QStandardItem('xx')
            xpath = QStandardItem('xx')
            comboItem = QStandardItem()

            if row is None:  # child
                item_one.appendRow([url_name, value, xpath, comboItem])
                self.tree.setIndexWidget(comboItem.index(), combobox)
                ze_childz = item_one.child(item_one.rowCount() - 1)

                for item in my_data:
                    if item['QItem'] == item_one:
                        tree_dict = {"unique_id": my_data[-1]['unique_id'] + 1, 'parent_id': item['unique_id'],
                                     'url_name': 'xx', 'xpath': 'xx', 'value': 'xx', 'link': None, 'image_link': '',
                                     'QItem': ze_childz, 'combobox': combobox}

            else:  # insert up/down
                parent.insertRow(row, [url_name, value, xpath, comboItem])
                self.tree.setIndexWidget(comboItem.index(), combobox)
                ze_brodarz = parent.child(item_one.rowCount() - 1)

                for item in my_data:
                    if item['QItem'] == parent:
                        tree_dict = {"unique_id": my_data[-1]['unique_id'] + 1, 'parent_id': item['unique_id'],
                                     'url_name': 'xx', 'xpath': 'xx', 'value': 'xx', 'link': None, 'image_link': '',
                                     'QItem': ze_brodarz, 'combobox': combobox}

        else:  # for when element is clicked from website: tree_dict != None
            unique_id = tree_dict['unique_id']
            if unique_id == 1:
                parent = self.model.invisibleRootItem()
            else:
                parent_id = tree_dict['parent_id']
                for item in my_data:
                    if item['unique_id'] == parent_id:
                        parent = item['QItem']
            comboItem = QStandardItem()
            parent.appendRow([
                QStandardItem(tree_dict['url_name']),
                QStandardItem(tree_dict['value']),
                QStandardItem(tree_dict['xpath']),
                comboItem,
                QStandardItem()
            ])
            tree_dict['QItem'] = parent.child(parent.rowCount() - 1)

            if unique_id > 1:
                combobox = comboTree(self)
                tree_dict['combobox'] = combobox
                self.tree.setIndexWidget(comboItem.index(), combobox)

        if tree_dict is not None:
            if tree_dict['unique_id'] > 1:
                my_data.append(tree_dict)
        self.tree.expandAll()

    # Function to save populate treeview with a dictionary
    def importData(self, my_data, root=None):  # note: good for loading a save file
        pass
        # print('IMPORT DATA:   ')
        # self.model.setRowCount(0)
        # if root is None:
        #     root = self.model.invisibleRootItem()
        # # seen = {}   # List of  QStandardItem
        # values = deque(my_data)  # it's dequeing so only show the immediate parent child relationship.
        # while values:
        #     value = values.popleft()
        #     if value['unique_id'] == 1:
        #         parent = root
        #     else:
        #         parent_id = value['parent_id']  # this is where you tell who the parent is...
        #         if parent_id not in self.seen:  # if parent got popped off earlier in the traversal, add it back in.
        #             values.append(value)
        #             continue
        #         parent = self.seen[parent_id]  # so there is a parent and a unique id and if they match thats where the child goes. and they match becuase thier just stupid intergers
        #         print('Parent: ', parent.data(0))
        #     unique_id = value['unique_id']
        #     # id_item = QStandardItem(str(unique_id))
        #     # id_item.setEditable(False)
        #     parent.appendRow([
        #         QStandardItem(value['url_name']),
        #         QStandardItem(value['value']),
        #         QStandardItem(value['xpath']),
        #         # id_item
        #     ])
        #     self.seen[unique_id] = parent.child(parent.rowCount() - 1)  # which means, when parent id == unique id.
        #     print(parent.child(parent.rowCount() - 1).data(0))
        #     print(self.seen)

    # Function to add right click menu to treeview item
    def openMenu(self, position):
            indexes = self.sender().selectedIndexes()
            mdlIdx = self.tree.indexAt(position)

            if not mdlIdx.isValid():
                return
            item = self.model.itemFromIndex(mdlIdx)
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
        self.create_row(item_one=item_one)
        # unique_id = my_data[-1]['unique_id'] + 1
        # url_name = QStandardItem('xx')
        # value = QStandardItem('xx')
        # xpath = QStandardItem('xx')
        # comboItem = QStandardItem()
        # # selecteditem = self.model.itemFromIndex(mdlIdx)
        # item_one.appendRow([url_name, value, xpath, comboItem])
        # self.tree.expandAll()
        # self.seen[unique_id] = item_one.child(item_one.rowCount() - 1)
        #
        # combobox = comboTree(self)
        # self.combodict[unique_id] = combobox
        # self.tree.setIndexWidget(comboItem.index(), combobox)
        #
        # # finding the index of the selected which is also the parent item so it can be added to my_data.
        # tree_dict = {"unique_id": unique_id, 'parent_id': None, 'url_name': 'xx', 'xpath': 'xx', 'value': 'xx', 'link': None, 'image_link': ''}
        # # index = indexes[0]
        # # val = self.model.itemFromIndex(index)
        # for k, v in self.seen.items():
        #     if v == item_one:
        #         tree_dict['parent_id'] = k
        # my_data.append(tree_dict)

    # Function to Insert sibling item above to treeview item
    def TreeItem_InsertUp(self, item_one):
        current_row = item_one.row()
        self.create_row(item_one=item_one, row=current_row)

    # Function to Insert sibling item above to treeview item
    def TreeItem_InsertDown(self, item_one):
        current_row = item_one.row() + 1
        self.create_row(item_one=item_one, row=current_row)

    # Function to Delete item
    def TreeItem_Delete(self, item_one):
        deletion_list = []
        if item_one is not None:
            for index, row in enumerate(my_data):
                if row['QItem'] == item_one:
                    deletion_list.append(row['unique_id'])
            for index, row in enumerate(my_data):
                if row['parent_id'] in deletion_list:
                    deletion_list.append(row['unique_id'])
            print(deletion_list)
            for index, row in enumerate(my_data):
                for i in deletion_list:
                    if row['unique_id'] == i:
                        print('this is fucking bullshit')

                    # unique_id = row['unique_id']
                    # x = my_data.pop(index)
                    # # print('deleted item: ', x)
                    # for idx, rw in enumerate(my_data):
                    #     if rw['parent_id'] == unique_id:
                    #         x = my_data.pop(idx)
                            # print('deleted child: ', x)

                    # print('found the item: delete item and all children!')
            # if item_one.hasChildren():
            #     for i in range(item_one.rowCount()):
            #         childitem = item_one.child(i)
            #         if childitem != None:
            #             for k, v in list(self.seen.items()):
            #                 if v == childitem:
            #                     for index, row in enumerate(my_data):
            #                         if row['unique_id'] == k:
            #                             x = my_data.pop(index)
            #                     del self.seen[k], self.combodict[k]
            #
            # for k, v in list(self.seen.items()):
            #     if v == item_one:
            #         for index, row in enumerate(my_data):
            #             if row['unique_id'] == k:
            #                 x = my_data.pop(index)
            #                 print('item deleted')
            #         del self.seen[k], self.combodict[k]

        # item_one.parent().removeRow(item_one.row())

    def transverse_tree(self):
        tree_list = []
        for i in range(self.model.rowCount()):
            item = self.model.item(i)
            level = 0
            self.GetItem(item, level, tree_list)

        # for j in tree_list:
        #     for i in my_data:
        #         if str(i['unique_id']) == str(j['unique_id']):
        #             i['operation'] = self.combodict[i['unique_id']].getComboValue()
        #             i['url_name'] = j['url_name']
        #             i['value'] = j['value']
        #             i['xpath'] = j['xpath']

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
                            else:
                                row_id = row_id
                            if j == 0:
                                for k, v in self.seen.items():
                                    if v == childrow:
                                        # tree_dict['operation'] = self.combodict[k].getComboValue()
                                        tree_dict['unique_id'] = k
                                tree_dict['parent_id'] = level
                                tree_dict['url_name'] = url_name
                                tree_dict['value'] = value
                                tree_dict['xpath'] = xpath
                                tree_list.append(tree_dict)
                            self.GetItem(childitem, level, tree_list)
                return tree_list

