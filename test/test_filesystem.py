from test_settings import SessionTestCase
import unittest

from buttfs.errors import MethodNotImplemented


class FilesystemTests(SessionTestCase):
    def test_list_root(self):
        f = self.s.get_filesystem()
        expected = []
        self.assertEqual(f.list('/'), expected, "Root not empty!")
        self.assertEqual(f.list(f.root_container()), expected, "Root not empty!")
        self.assertEqual(f.root_container().list(), expected, "Root not empty!")

    def test_move_folders(self):
        f = self.s.get_filesystem()
        root = f.root_container()

        test_folder = root.create_folder('test')
        test_folder2 = root.create_folder('test 2')

        move_folder_name = 'move!'

        move_folder = test_folder.create_folder(move_folder_name)

        f.move([move_folder], test_folder2)

        test_folder2_contents = test_folder2.list()
        test_folder_contents = test_folder.list()
        self.assertEqual(len(test_folder2_contents), 1, "Wrong number of contents for target folder!")
        self.assertEqual(len(test_folder_contents), 0, "Wrong number of contents for source folder!")
        self.assertEqual(test_folder2_contents[0].name, move_folder.name, "Wrong name for moved folder!")

    def test_copy_folders(self):
        f = self.s.get_filesystem()
        root = f.root_container()

        test_folder = root.create_folder('test')
        test_folder2 = root.create_folder('test 2')

        copy_folder_name = 'copied!'

        copy_folder = test_folder.create_folder(copy_folder_name)

        f.copy([copy_folder], test_folder2)

        test_folder2_contents = test_folder2.list()
        test_folder_contents = test_folder.list()
        self.assertEqual(len(test_folder2_contents), 1, "Wrong number of contents for target folder!")
        self.assertEqual(len(test_folder_contents), 1, "Wrong number of contents for source folder!")
        self.assertEqual(test_folder2_contents[0].name, copy_folder.name, "Wrong name for copied folder!")
        self.assertEqual(test_folder_contents[0].name, copy_folder.name, "Wrong name for original folder!")

    def test_restore_items(self):
        f = self.s.get_filesystem()
        root = f.root_container()

        test_folder = root.create_folder('test')
        test_folder2 = root.create_folder('test 2')

        test_folder.delete()
        test_folder2.delete()
        self.assertEqual(len(f.list_trash()), 2, 'Wrong number of items in trash!')
        self.assertEqual(len(root.list()), 0, 'Wrong number of items in root!')

        result = f.restore([test_folder, str(test_folder2.path())])
        self.assertEqual(len(result), 2, 'Result did not contain what was expected: {}'.format(result))
        self.assertEqual(len(f.list_trash()), 0, 'Wrong number of items in trash!')
        self.assertEqual(len(root.list()), 2, 'Folders were not restored!')

    def test_unimplemented_methods(self):
        f = self.s.get_filesystem()

        self.assertRaises(
            MethodNotImplemented,
            f.file_history,
            ''
        )

    def tearDown(self):
        f = self.s.get_filesystem()
        root = f.root_container()
        for folder in root.list():
            folder.delete(force=True, commit=True)

if __name__ == '__main__':
    unittest.main()
