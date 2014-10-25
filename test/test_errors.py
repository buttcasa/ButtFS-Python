from test_settings import SessionTestCase
from cloudfs import errors
import unittest


class FolderErrorTests(SessionTestCase):
    # There are some errors that are defined. but are never returned
    # by the REST interface.
    #
    # ReadOnly errors (2004-2009, 2036-2038)
    # Failed to read Filesystem (2010-2013)
    # Name Conflict Errors (2014-2018)
    # Failures to Save / Broadcast changes (2019-2025)
    # Delete Infinite Drive (2026) - FolderNotFound (2003) returned instead
    # Exists parameter invalid (2033)
    # Path does not exist (2039)
    # PermissionDenied (2040, 2041)
    # Invalid Operation (2043) - Marked as Broadcast update on server side??
    # Invalid Depth (2045) - Marked as InvalidManifestError on server??
    # VersionDoesNotExist (2046) - InvalidManifestTypeError on server
    # Invalid Name (2048) - InvalidFilenameLengthError on server. Illegal names raise 2047
    # Tree Required (2049) - InvalidFilenameDotError on server.
    # Invalid Verbose (2050) - InvalidFilenameCharError on server.

    def setUp(self):
        super(FolderErrorTests, self).setUp()

        self.fs = self.s.get_filesystem()
        self.root = self.fs.root_container()
        self.root.create_folder('test')

    def test_error_DirectoryNotEmpty(self):
        items = self.root.list()
        items[0].create_folder('test2')

        self.assertRaises(
            errors.DirectoryNotEmpty,
            items[0].delete)

    def test_error_FolderNotFound(self):
        self.assertRaises(
            errors.FolderNotFound,
            self.root.delete)

    def test_error_list_FolderDoesNotExist(self):
        self.assertRaises(
            errors.FolderDoesNotExist,
            self.fs.list,
            '/notapath')

    def test_error_MissingToParameter(self):
        self.assertRaises(
            errors.MissingToParameter,
            self.fs.move,
            self.root.list(), '', self.fs.exists.fail)

    def test_error_MissingPathParameter(self):
        # TODO: generate this error manually
        #self.fs.move(None, self.root, self.fs.exists.fail)
        pass

    def test_error_NameConflictInOperation(self):
        self.assertRaises(
            errors.NameConflictInOperation,
            self.root.create_folder,
            'test')
        pass

    def test_error_VersionMissingOrIncorrect(self):
        # alter meta on a folder with wrong version
        pass

    def test_error_NameRequred(self):
        # create a folder w/o a name
        # create with an invalid name
        pass

    def tearDown(self):
        for folder in self.root.list():
            folder.delete(force=True)


class FileErrorTests(SessionTestCase):
    # There are some errors that are defined. but are never returned
    # by the REST interface.
    #
    # Invalid operation error (3007)
    # Invalid Exists (3009)
    # Extension Too Long (3010)
    # MIME too long (3014)
    # Size required error (3019)
    #

    def setUp(self):
        super(FileErrorTests, self).setUp()

        self.fs = self.s.get_filesystem()
        self.root = self.fs.root_container()
        self.root.create_folder('test')

    def test_error_FileNotFound(self):
        # alter_meta on a file that doesn't exist
        pass

    def test_error_InvalidName(self):
        # upload a file with a . in front of the name
        # upload a file containing '/','\\','<','>',':','\"','|','?','*'
        # may not work, as this is python code
        pass

    def test_error_InvalidDates(self):
        # improperly format:
        # date_created
        # date_meta_last_modified
        # date_content_last_modified
        pass

    def test_error_SizeMustBePositive(self):
        # set size to -1
        pass

    def test_error_NameRequired(self):
        # set name to ''
        pass

    def test_error_ToPathRequired(self):
        # copy or move a file without a 'to' argument
        pass

    def test_error_VersionMissingOrIncorrect(self):
        # alter_meta on a file with the wrong version #
        pass

    def tearDown(self):
        for folder in self.root.list():
            folder.delete(force=True)

class ShareErrorTests(SessionTestCase):
    # None of the numbers in the documentation are associated with share errors
    # they are instead associated with Block Errors
    pass

class FilesystemErrorTests(SessionTestCase):
    # None of the numbers in the documentation are associated with any errors
    # 8002 is raised when altering_meta and version-conflict is set to 'ignore'
    pass

if __name__ == '__main__':
    unittest.main()