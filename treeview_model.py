# import sys
# from collections import deque
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
                # QStandardItem()
            ])
            QtObject = parent.child(parent.rowCount() - 1)
            tree_dict['QItem'] = QtObject
            tree_dict['object_id'] = id(QtObject)

            if unique_id > 1:
                combobox = comboTree(self)
                # tree_dict['combobox'] = combobox
                self.tree.setIndexWidget(comboItem.index(), combobox)

        if tree_dict is not None:
            if tree_dict['unique_id'] > 1:
                my_data.append(tree_dict)
        self.tree.expandAll()

    def importData(self, my_data, root=None):  # note: good for loading a save file
        """Function to save populate treeview with a dictionary"""
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

        # print("Transverse Tree: ")
        # for row in funnel:
        #     print(row)

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

    # def GetItem(self, item, level, tree_list):
    #     if item is not None:
    #         if item.hasChildren():
    #             level = level + 1
    #             column_name = ' '
    #             value = ' '
    #             xpath = ' '
    #             combobox_index = ' '
    #             for i, row in enumerate(my_data[level:]):
    #                 # pseudo_tree = {'cell_id': i, **{k: v for k, v in row.items() if k != 'QItem' and k != 'combobox'}}
    #                 for j in reversed([0, 1, 2, 3]):
    #                     childitem = item.child(i, j)
    #                     if childitem is not None:
    #                         if j == 0:
    #                             column_name = childitem.data(0)
    #                             # pseudo_tree = {'cell_id': i,
    #                             #                **{k: v for k, v in row.items() if k != 'QItem' and k != 'combobox'}}
    #                         else:
    #                             column_name = column_name
    #                         if j == 1:
    #                             value = childitem.data(0)
    #                         else:
    #                             value = value
    #                         if j == 2:
    #                             xpath = childitem.data(0)
    #                         else:
    #                             xpath = xpath
    #                         if j == 3:
    #                             wombo = childitem.index()
    #                             combobox_index = self.tree.indexWidget(wombo).getComboValue()
    #                         else:
    #                             combobox_index = combobox_index
    #                         if j == 0:
    #                             # tree_dict = {k: v for k, v in row.items() if k != 'QItem' and k != 'combobox'}
    #                             tree_dict = dict()
    #                             # tree_dict['unique_id'] = row.get('unique_id', None)
    #                             # tree_dict['cell_id'] = i
    #                             # tree_dict['parent_id'] = row.get('parent_id', None)
    #                             tree_dict['column_name'] = column_name
    #                             tree_dict['value'] = value
    #                             tree_dict['comboIndex'] = combobox_index
    #                             # tree_dict['url_name'] = row.get('url_name', None)
    #                             # tree_dict['local_name'] = row.get('local_name', None)
    #                             # tree_dict['parent_name'] = row.get('parent_name', None)
    #                             # tree_dict['attributes'] = row.get('attributes', None)
    #                             tree_dict['xpath'] = xpath
    #                             tree_list.append(tree_dict)
    #                         self.GetItem(childitem, level, tree_list)
    #         # print(pseudo_tree)
    #         return tree_list
