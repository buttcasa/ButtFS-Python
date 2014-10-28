from test_settings import SessionTestCase
import unittest
import datetime
import time

class FolderTests(SessionTestCase):

    FORBIDDEN_SETTERS = ['id', 'type', 'is_mirrored']

    def setUp(self):
        super(FolderTests, self).setUp()

        self.fs = self.s.get_filesystem()
        self.root = self.fs.root_container()
        self.test_folder = self.root.create_folder('test')

    def get_example_object(self):
        return self.test_folder

    def test_create_folder(self):
        items = self.root.list()
        self.assertEqual(len(items), 1, "Wrong count of items in root!")
        items[0].delete()
        self.assertEqual('folder', items[0].type, "")
        self.assertEqual(False, items[0].is_mirrored)
        self.assertEqual(datetime.date.fromtimestamp(items[0].date_created), datetime.date.today(), "Creation date wrong!")
        items = self.root.list()
        self.assertEqual(len(items), 0, "Wrong count of items in root!")

    def test_create_nested_folders(self):
        items = self.root.list()
        self.assertEqual(len(items), 1, "Wrong count of items in root!")
        new_folder = items[0].create_folder('test2')
        test_items =  items[0].list()
        self.assertEqual(len(test_items), 1, "Wrong count of items in /test!")
        self.assertEqual(test_items[0], new_folder, "Got different items from creating and listing folder!")
        new_folder.delete()
        test_items =  items[0].list()
        self.assertEqual(len(test_items), 0, "Wrong count of items in /test!")
        items[0].delete()
        items = self.root.list()
        self.assertEqual(len(items), 0, "Wrong count of items in root!")

    def test_create_unicode_name(self):
        unicode_snowman = u'\u2603'
        snowman = self.root.create_folder(unicode_snowman)
        self.assertEqual(snowman.name, unicode_snowman, "Unicode name not properly preserved!")

    def test_alter_meta(self):
        folder = self.get_example_object()
        new_name = 'shazam!'
        folder.name = new_name
        #now = self.current_time()
        folder.save()
        self.assertEqual(folder.name, new_name, "New name was not set!")
        # times not currently updated :'(
        #self.assertTrue(datetime.datetime.fromtimestamp(folder.date_meta_last_modified) >= now, "Meta last modified not updated!")
        #self.assertTrue(datetime.datetime.fromtimestamp(folder.date_content_last_modified) < now, "Content last modified early!")
        folder = self.root.list()[0]
        self.assertEqual(folder.name, new_name, "New name was not set on server!")
        #self.assertTrue(datetime.datetime.fromtimestamp(folder.date_content_last_modified) >= now, "Content last modified not updated!")

    def test_folder_refresh(self):
        folder = self.get_example_object()
        old_name = folder.name
        new_name = 'shazam!'
        folder.name = new_name
        self.assertEqual(folder.name, new_name, "New name was not set!")
        folder.refresh()
        self.assertEqual(folder.name, old_name, "Name should be reset!")


    def tearDown(self):
        for folder in self.root.list():
            folder.delete(force=True, commit=True)



if __name__ == '__main__':
    unittest.main()