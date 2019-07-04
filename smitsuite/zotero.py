__author__ = 'Jochem Smit'

from pyzotero import zotero
import pickle
from treelib import Node, Tree
from treelib.exceptions import DuplicatedNodeIdError
import os
import shutil


class CollectionNode(Node):
    def __init__(self, col_dict):
        self.d = col_dict
        s = self.d['data']['name']
        for r in [r'/', "\\", '&', '%']:
            s = s.replace(r, '_')
        tag = s
        identifier = self.d['key']
        super(CollectionNode, self).__init__(tag=tag, identifier=identifier)
        self._parent = self.d['data']['parentCollection'] or 'root'


class ItemNode(Node):
    def __init__(self, item_dict):
        self.d = item_dict
        identifier = self.d['data']['key']
        self.zot_id = identifier
        try:
            tag = self.d['data']['title']
        except KeyError:
            tag = identifier
        super(ItemNode, self).__init__(tag=tag, identifier=identifier)

        self._item_type = self.d['data']['itemType']

        try:
            self._parents = self.d['data']['collections']
        except KeyError:
            self._parents = None
        try:
            self._parent_item = self.d['data']['parentItem']  # its an attachment probably
        except KeyError:
            self._parent_item = None


class ZotLib(object):
    def __init__(self, library_id, library_type, api_key):
        self.z = zotero.Zotero(library_id, library_type, api_key)
        self.t = Tree()
        self.t.create_node('root', 'root')
        self.cols = []

    def parse_cols(self):
        self.cols = []
        top_cols = self.z.collections_top()

        for col in top_cols:
            col_node = self.make_col_node(col)
            self.t.add_node(col_node, 'root')
            self.recursive_parse(col_node)

    def recursive_parse(self, top_col):
        child_cols = self.z.collections_sub(top_col.identifier)
        for child in child_cols:
            col_node = self.make_col_node(child)

            self.t.add_node(col_node, top_col.identifier)
            self.recursive_parse(col_node)

    def make_col_node(self, col_dict):
        col_node = CollectionNode(col_dict)
        col_node._items = self.z.collection_items_top(col_node.identifier)
        self.cols.append(col_node)

        return col_node

    def parse_items(self):
        for col in self.cols:
            for item in col._items:
                item_node = ItemNode(item)
                try:
                    self.t.add_node(item_node, parent=col.identifier)
                except DuplicatedNodeIdError:
                    item_node.identifier = str(id(item_node))
                if item_node._item_type not in ['attachment', 'note']:
                    item_node._children = self.z.children(item_node.zot_id)
                else:
                    item_node._children = []


class TreeToDisk(object):
    def __init__(self, tree, storage_dir, output_dir):
        self.tree = tree
        self.storage_dir = storage_dir
        self.output_dir = output_dir

    def parse(self, node_id):
        node = self.tree.get_node(node_id)

        try:
            parent = self.tree.get_node(node._parent)
            node.path = os.path.join(parent.path, node.tag)
        except AttributeError:
            node.path = 'root'

        path = os.path.join(self.output_dir, node.path)
        if not os.path.exists(path):
            os.mkdir(path)

        for child in self.tree.children(node_id):
            if isinstance(child, CollectionNode):
                self.parse(child.identifier)
            else:
                print('item', child.tag)

                if child._item_type == 'attachment':
                    filename = child.d['data']['filename']
                    key = child.zot_id

                    src_path = os.path.join(self.storage_dir, key, filename)
                    target_path = os.path.join(self.output_dir, node.path, filename)

                    print('attachment', src_path, target_path)
                    try:
                        shutil.copy(src_path, target_path)
                    except (FileNotFoundError, PermissionError) as err:
                        print(err, filename, key)

                else:
                    for item_child in child._children:
                        if item_child['data']['itemType'] == 'attachment':

                            try:
                                filename = item_child['data']['filename']
                            except KeyError:
                                continue
                            key = item_child['key']

                            src_path = os.path.join(self.storage_dir, key, filename)
                            target_path = os.path.join(self.output_dir, node.path, filename)

                            try:
                                shutil.copy(src_path, target_path)
                            except (FileNotFoundError, PermissionError) as err:
                                print(err, filename, key)

                    if not child._children:
                        name = child.tag[:100]
                        remove = ["'", "\"", ':', '*', '&', '%', '<', '>', '?', '!', '/', '|']
                        for r in remove:
                            name = name.replace(r, '')
                        filename = name + '.txt'

                        target_path = os.path.join(self.output_dir, node.path, filename)

                        with open(target_path, 'w', encoding='utf-8') as f:
                            if child._item_type == 'journalArticle':
                                f.write(child.tag + '\n')
                                f.write(child.d['data']['publicationTitle'] + '\n')
                                f.write(child.d['data']['DOI'] + '\n')
                                f.write(child.d['data']['url'] + '\n')

                            else:
                                pass


if __name__ == '__main__':
    zot = ZotLib('<ID>', 'user', '<KEY>')
    storage_dir = 'PATH TO STORAGE DIR'
    output_dir = 'PATH TO OUTPUT DIR'


    reload = True
    if reload:
        zot.parse_cols()
        zot.t.show()

        zot.parse_items()
        zot.t.show()

        with open('zot.pick', 'wb') as f:
            pickle.dump(zot, f)

    else:
        with open('zot.pick', 'rb') as f:
            zot = pickle.load(f)

        zot.t.show()

    ct = TreeToDisk(zot.t, storage_dir, output_dir)
    ct.parse('root')


print('DONE')