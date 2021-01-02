# import sys
from collections import deque
# from collections import defaultdict

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from functools import partial

from data_file import my_data


class comboTree(QComboBox):
    def __init__(self, parent):
        super().__init__(parent)
        self.addItems(['Item', "Multi-Item (don't use)", 'Pagination', "Follow-Link (don't use)", 'Follow-All-Links'])

    def getComboValue(self):
        return self.currentIndex()


class MyDelegate(QStyledItemDelegate):

    def sizeHint(self, option, index):
        my_fixed_height = 30
        size = super(MyDelegate, self).sizeHint(option, index)
        size.setHeight(my_fixed_height)
        return size


class view(QWidget):
    def __init__(self):
        super(view, self).__init__()
        self.tree = QTreeView(self)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.openMenu)
        layout = QVBoxLayout(self)
        layout.addWidget(self.tree)
        layout.setContentsMargins(0,0,0,0)

        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['Object Name', 'Value', 'XPath', 'Object-Type'])
        self.tree.header().setSectionResizeMode(QHeaderView.Stretch)

        self.tree.setItemDelegate(MyDelegate(self.tree))
        self.tree.header().setDefaultAlignment(Qt.AlignCenter)
        self.tree.setModel(self.model)
        self.font = QFont("Arial", 12)
        self.tree.setFont(self.font)
        self.create_row(my_data[0])

    def create_row(self, tree_dict=None, item_one=None, row=None):
        if tree_dict is None:
            combobox = comboTree(self)
            parent = item_one.parent()

            column_name = QStandardItem('Column ' + str(my_data[-1]['unique_id']))
            value = QStandardItem('xx')
            xpath = QStandardItem('xx')
            comboItem = QStandardItem()

            if row is None:  # child
                item_one.appendRow([column_name, value, xpath, comboItem])
                self.tree.setIndexWidget(comboItem.index(), combobox)
                ze_childz = item_one.child(item_one.rowCount() - 1)

                for item in my_data:
                    if item['QItem'] == item_one:
                        tree_dict = {"unique_id": my_data[-1]['unique_id'] + 1, 'parent_id': item['unique_id'],
                                     'url_name': 'xx', 'xpath': 'xx', 'value': 'xx', 'link': None, 'image_link': '',
                                     'QItem': ze_childz, 'combobox': combobox, 'object_id': id(ze_childz)}

            else:  # insert up/down
                parent.insertRow(row, [column_name, value, xpath, comboItem])
                self.tree.setIndexWidget(comboItem.index(), combobox)
                ze_brodarz = parent.child(item_one.rowCount() - 1)

                for item in my_data:
                    if item['QItem'] == parent:
                        tree_dict = {"unique_id": my_data[-1]['unique_id'] + 1, 'parent_id': item['unique_id'],
                                     'url_name': 'xx', 'xpath': 'xx', 'value': 'xx', 'link': None, 'image_link': '',
                                     'QItem': ze_brodarz, 'combobox': combobox, 'object_id': id(ze_brodarz)}

        else:  # for when element is clicked from website: tree_dict != None
            unique_id = tree_dict['unique_id']
            if unique_id == 1:
                parent = self.model.invisibleRootItem()
                column = QStandardItem(tree_dict['url_name'])
                font = QFont("Arial", 12)
                font.setBold(True)
                column.setFont(font)
            else:
                parent_id = tree_dict['parent_id']
                column = QStandardItem(tree_dict['column_name'])
                for item in my_data:
                    if item['unique_id'] == parent_id:
                        parent = item['QItem']
            comboItem = QStandardItem()
            parent.appendRow([
                column,
                QStandardItem(tree_dict['value']),
                QStandardItem(tree_dict['xpath']),
                comboItem,
            ])
            QtObject = parent.child(parent.rowCount() - 1)
            tree_dict['QItem'] = QtObject
            tree_dict['object_id'] = id(QtObject)

            if unique_id > 1:
                combobox = comboTree(self)
                if tree_dict.get('comboIndex'):
                    combobox.setCurrentIndex(tree_dict['comboIndex'])
                self.tree.setIndexWidget(comboItem.index(), combobox)

        if tree_dict is not None:
            if tree_dict['unique_id'] > 1:
                my_data.append(tree_dict)
            else:  # added this to make deserialization work.
                my_data[0] = tree_dict
        self.tree.expandAll()

    def importData(self, tree_list):
        """Function to save populate treeview with a dictionary"""
        self.model.setRowCount(0)
        values = deque(tree_list)
        while values:
            value = values.popleft()
            self.create_row(tree_dict=value)

    def openMenu(self, position):
        """Function to add right click menu to treeview item"""
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

    def TreeItem_Add(self, item_one):
        """Function to add child item to treeview item"""
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
        # self.tree.inde
        #
        # # finding the index of the selected which is also the parent item so it can be added to my_data.
        # tree_dict = {"unique_id": unique_id, 'parent_id': None, 'url_name': 'xx', 'xpath': 'xx', 'value': 'xx', 'link': None, 'image_link': ''}
        # # index = indexes[0]
        # # val = self.model.itemFromIndex(index)
        # for k, v in self.seen.items():
        #     if v == item_one:
        #         tree_dict['parent_id'] = k
        # my_data.append(tree_dict)

    def TreeItem_InsertUp(self, item_one):
        """Function to Insert sibling item above to treeview item"""
        current_row = item_one.row()
        self.create_row(item_one=item_one, row=current_row)

    def TreeItem_InsertDown(self, item_one):
        """Function to Insert sibling item above to treeview item"""
        current_row = item_one.row() + 1
        self.create_row(item_one=item_one, row=current_row)

    def TreeItem_Delete(self, item_one):
        """Function to Delete item"""
        item = self.delete_list(my_data, item_one)
        self.delete(my_data, item)
        item_one.parent().removeRow(item_one.row())

    def delete_list(self, tree, node):  # only works because parent elements come before children.
        dl = []
        for item in tree:
            if item['QItem'] == node:
                dl.append(item['unique_id'])
            if item['parent_id'] in dl:
                dl.append(item['unique_id'])
        return dl

    def delete(self, tree, nodes):
        t = [item for item in tree if item['unique_id'] not in nodes]
        del tree[:]
        tree.extend(t)

    def transverse_tree(self):
        tree_list = []
        item = self.model.item(0)
        level = 0
        funnel = self.GetCell(item, level, tree_list)  # its so strange that the list itself gets modified.
        # TODO the funnel values are returning none when there is only one row. might have to do with my_data being
        #  an outside module.
        for idx, row in enumerate(my_data[1:]):
            for i in funnel:
                if row['object_id'] == i['object_id']:
                    row['column_name'] = i.get('column_name', 'ERROR RETRIEVING THE OBJECTS FROM TREE!')
                    row['value'] = i.get('value', 'ERROR RETRIEVING THE OBJECTS FROM TREE!')
                    row['xpath'] = i.get('xpath', 'ERROR RETRIEVING THE OBJECTS FROM TREE!')
                    row['comboIndex'] = i.get('comboIndex', 'ERROR RETRIEVING THE OBJECTS FROM TREE!')
        return funnel

    def GetRow(self, item, level, tree_list):
        for i in range(item.rowCount()):
            child_row = item.child(i)
            tree_list.append((child_row, id(child_row)))
            self.GetRow(child_row, level, tree_list)
        return tree_list

    def GetCell(self, item, level, tree_list):
        tree = []
        if item is not None:
            if item.hasChildren():
                for row_idx, row in enumerate(self.GetRow(item, level, tree_list)):
                    sib = row[0].index()
                    funnel = {'column_name': sib.siblingAtColumn(0).data(0),
                              'value': self.model.itemFromIndex(sib.siblingAtColumn(1)).data(0),  # using itemindex to see if it makes a difference.
                              'xpath': sib.siblingAtColumn(2).data(0),
                              'comboIndex': self.tree.indexWidget(sib.siblingAtColumn(3)).getComboValue(),
                              'object_id': row[1]
                              }
                    tree.append(funnel)
        return tree
