from test_settings import ButtFSTestCase
from buttfs.path import Path
from buttfs.item import Item
import unittest


class PathTests(ButtFSTestCase):
    def test_path_string_root(self):
        p = Path.path_from_string("/")
        self.assertEqual(len(p), 1, "Path with only root was not length 1.")

    def test_path_generic(self):
        p = Path.path_from_string('/a/b/c')
        self.assertEqual(len(p), 4, "Path with root and three items not length 4.")
        self.assertEqual(p[3], 'c', "4th item in path not c.")
        self.assertEqual(str(p), '/a/b/c', "Path string incorrect.")

    def test_path_constructors(self):
        a = Item(None)._create_from_json({'id':'a', 'name':'a'}, None)
        b = Item(None)._create_from_json({'id':'b', 'name':'b'}, a)
        c = Item(None)._create_from_json({'id':'c', 'name':'c'}, b)
        paths = [ # equivalent constructors
            ('path_from_string', Path.path_from_string('/a/b/c')),
            ('path_from_string_list', Path.path_from_string_list(['/','a','b','c'])),
            ('path_from_item_list', Path.path_from_item_list([a, b, c], add_root=True))
        ]
        for name, p in paths:
            self.assertEqual(len(p), 4, "{}:Path with root and three items not length 4.".format(name))
            self.assertEqual(p[3], 'c', "{}:4th item in path not c.".format(name))
            self.assertEqual(str(p), '/a/b/c', "{}:Path string incorrect.".format(name))

    def test_path_append(self):
        p = Path.path_from_string('/a/b/c')
        p.append('d')
        self.assertEqual(len(p), 5, "Path length not at 5.")
        self.assertEqual(p[4], 'd', "5th item in path not d.")
        self.assertEqual(str(p), '/a/b/c/d', "Path string incorrect.")
        p.append(Item(None)._create_from_json({'id':'e', 'name':'e'}, None))
        self.assertEqual(len(p), 6, "Path length not at 6.")
        self.assertEqual(p[5], 'e', "5th item in path not d.")
        self.assertEqual(str(p), '/a/b/c/d/e', "Path string incorrect.")

if __name__ == '__main__':
    unittest.main()
