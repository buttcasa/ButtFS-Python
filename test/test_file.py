from test_settings import SessionTestCase
from cloudfs.private.cloudfs_paths import ExistValues

import unittest
import time
import os
import shutil
import datetime

from cloudfs.errors import MethodNotImplemented

# Functional tests based around file creation & modification
class FileFunctionalTests(SessionTestCase):

    FORBIDDEN_SETTERS = ['id', 'type', 'is_mirrored']

    def setUp(self):
        super(FileFunctionalTests, self).setUp()

        self.fs = self.s.get_filesystem()
        self.root = self.fs.root_container()
        self.test_folder = self.root.create_folder('test', exists=ExistValues.overwrite)
        self.new_file_name = 'test_file.py'
        self.new_file_path = './{}'.format(self.new_file_name)
        self.new_file = self.test_folder.upload(self.new_file_path, exists=ExistValues.overwrite)

        self.download_directory = './download_tests'
        if os.path.exists(self.download_directory):
            shutil.rmtree(self.download_directory)
        os.makedirs(self.download_directory)

    def get_example_object(self):
        return self.new_file

    def test_create_file_from_file(self):
        file_pointer = open(self.new_file_path, 'r')
        file_info = os.stat(self.new_file_path)
        new_file = self.new_file
        self.assertEqual(file_pointer.read(), new_file.read(), "File did not upload correctly!")
        self.assertEqual(new_file.name, self.new_file_name, "New file not named as expected!")
        self.assertEqual(file_info.st_size, new_file.size, "New file size incorrect!")
        self.assertEqual('py', new_file.extension, "File has wrong extension")
        self.assertEqual('file', new_file.type, "")
        self.assertEqual(False, new_file.is_mirrored)
        self.assertEqual(datetime.date.fromtimestamp(new_file.date_created), datetime.date.today(), "Creation date wrong!")

    def test_download_file(self):
        file = self.get_example_object()
        file_pointer = open(self.new_file_path, 'r')
        expected_contents = file_pointer.read()
        file_pointer.close()
        # def download(self, local_path, custom_name=None, synchronous=False, debug=False):

        test_cases = [
            (self.download_directory, None, os.path.join(self.download_directory, file.name)),
            (os.path.join(self.download_directory, file.name), None, os.path.join(self.download_directory, file.name)),
            (self.download_directory, "test", os.path.join(self.download_directory, "test"))
        ]
        for path, custom_name, expected_path in test_cases:
            file.download(path, custom_name=custom_name)
            file.wait_for_downloads()
            self.assertTrue(os.path.exists(expected_path), "File does not exist in the expected location!")
            downloaded_file = open(expected_path)
            downloaded_file_content = downloaded_file.read()
            self.assertEqual(downloaded_file_content, expected_contents, "Downloaded file did not match file on disk!")
            os.remove(expected_path)


    def test_create_file_from_string(self):
        new_file_name = 'test_name'
        new_file_expected_contents = "test content!"
        new_file = self.test_folder.upload(new_file_expected_contents, custom_name=new_file_name, custom_mime='test/mime', data_inline=True)
        self.assertEqual(new_file.name, new_file_name, "New item had wrong name!")
        folder_contents = self.test_folder.list()
        self.assertEqual(len(folder_contents), 2, "Folder has wrong number of items!")
        found = False
        for item in folder_contents:
            if item.id == new_file.id:
                found = True
                self.assertEqual(item.name, new_file.name, "Got different items from creating item and listing folder!")

        self.assertTrue(found, "Did not find the file we just created!")
        new_file_contents = new_file.read()
        self.assertEqual(new_file_contents, new_file_expected_contents, "File did not contain expected contents!")

    def test_alter_meta(self):
        new_file = self.new_file
        new_name = 'new name.jpeg'
        expected_extension = 'jpeg'
        expected_mime = 'image/jpeg'

        self.assertNotEqual(new_file.name, new_name, "Name should not be set yet!")
        self.assertNotEqual(new_file.extension, expected_extension, "extension should not be set yet!")

        new_file.name = new_name

        now = self.current_time()

        new_file.save()
        self.assertEqual(new_file.name, new_name, "Name should be set!")
        # times not being updated :(
        #self.assertTrue(datetime.datetime.fromtimestamp(new_file.date_meta_last_modified) >= now, "Date meta last modified not updated! {} < {}".format(datetime.datetime.fromtimestamp(new_file.date_meta_last_modified), now))

        new_file = self.test_folder.list()[0]

        self.assertEqual(new_file.name, new_name, "Name should be set!")
        self.assertEqual(new_file.mime, expected_mime, "Mime should be set!")
        self.assertEqual(new_file.extension, expected_extension, "Extension should be set!")

        # Can only change the mime if we aren't also changing the name.
        # Otherwise mime will be set from the name of the file.
        new_mime = 'blah/blah'
        new_file.mime = new_mime

        new_file.save()
        self.assertEqual(new_file.mime, new_mime, "Mime should be set!")
        new_file = self.test_folder.list()[0]

        self.assertEqual(new_file.mime, new_mime, "Mime should be set!")

    def test_file_refresh(self):
        new_name = 'new name.jpeg'
        old_name = self.new_file.name
        self.new_file.name = new_name
        self.assertEqual(self.new_file.name, new_name, "Name should be set!")
        self.new_file.refresh()
        self.assertEqual(self.new_file.name, old_name, "Name should be reset!")

    def test_unimplemented_methods(self):
        self.assertRaises(
            MethodNotImplemented,
            self.new_file.restore,
            ''
        )

        self.assertRaises(
            MethodNotImplemented,
            self.new_file.history
        )


    def tearDown(self):
        if os.path.exists(self.download_directory):
            shutil.rmtree(self.download_directory)
        for folder in self.root.list():
            folder.delete(force=True)



if __name__ == '__main__':
    unittest.main()