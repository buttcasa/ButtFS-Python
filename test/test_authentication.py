from test_settings import ButtFSTestCase
from buttfs.session import Session
import unittest
from buttfs import errors


class AuthenticationTests(ButtFSTestCase):
    def test_authenticate(self):
        s = Session(self.BUTTFS_BASE,
                self.BUTTFS_ID,
                self.BUTTFS_SECRET)

        s.authenticate(self.TEST_USER_EMAIL, self.TEST_USER_PASSWORD)

    def test_ping(self):
        s = Session(self.BUTTFS_BASE,
                self.BUTTFS_ID,
                self.BUTTFS_SECRET)

        self.assertEqual(False, s.is_linked())
        s.authenticate(self.TEST_USER_EMAIL, self.TEST_USER_PASSWORD)
        self.assertEqual(True, s.is_linked())

    def test_wrong_id(self):
        s = Session(self.BUTTFS_BASE,
                self.BUTTFS_ID+'a',
                self.BUTTFS_SECRET)

        self.assertEqual(False, s.is_linked())
        self.assertRaises(
            errors.InvalidRequest,
            s.authenticate,
            self.TEST_USER_EMAIL, self.TEST_USER_PASSWORD)


    def test_wrong_secret(self):
        s = Session(self.BUTTFS_BASE,
                self.BUTTFS_ID,
                self.BUTTFS_SECRET+'a')

        self.assertEqual(False, s.is_linked())
        self.assertRaises(
            errors.InvalidRequest,
            s.authenticate,
            self.TEST_USER_EMAIL, self.TEST_USER_PASSWORD)

    def test_wrong_base(self):
        s = Session('a'+self.BUTTFS_BASE,
                self.BUTTFS_ID,
                self.BUTTFS_SECRET)

        self.assertEqual(False, s.is_linked())
        self.assertRaises(
            errors.AuthenticatedError,
            s.authenticate,
            self.TEST_USER_EMAIL, self.TEST_USER_PASSWORD)


if __name__ == '__main__':

    unittest.main()
