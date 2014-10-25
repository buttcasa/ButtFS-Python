from test_settings import CloudFSTestCase
from cloudfs.session import Session
import unittest
from cloudfs import errors


class AuthenticationTests(CloudFSTestCase):
    def test_authenticate(self):
        s = Session(self.CLOUDFS_BASE,
                self.CLOUDFS_ID,
                self.CLOUDFS_SECRET)

        s.authenticate(self.TEST_USER_EMAIL, self.TEST_USER_PASSWORD)

    def test_ping(self):
        s = Session(self.CLOUDFS_BASE,
                self.CLOUDFS_ID,
                self.CLOUDFS_SECRET)

        self.assertEqual(False, s.is_linked())
        s.authenticate(self.TEST_USER_EMAIL, self.TEST_USER_PASSWORD)
        self.assertEqual(True, s.is_linked())

    def test_wrong_id(self):
        s = Session(self.CLOUDFS_BASE,
                self.CLOUDFS_ID+'a',
                self.CLOUDFS_SECRET)

        self.assertEqual(False, s.is_linked())
        self.assertRaises(
            errors.InvalidRequest,
            s.authenticate,
            self.TEST_USER_EMAIL, self.TEST_USER_PASSWORD)


    def test_wrong_secret(self):
        s = Session(self.CLOUDFS_BASE,
                self.CLOUDFS_ID,
                self.CLOUDFS_SECRET+'a')

        self.assertEqual(False, s.is_linked())
        self.assertRaises(
            errors.InvalidRequest,
            s.authenticate,
            self.TEST_USER_EMAIL, self.TEST_USER_PASSWORD)

    def test_wrong_base(self):
        s = Session('a'+self.CLOUDFS_BASE,
                self.CLOUDFS_ID,
                self.CLOUDFS_SECRET)

        self.assertEqual(False, s.is_linked())
        self.assertRaises(
            errors.AuthenticatedError,
            s.authenticate,
            self.TEST_USER_EMAIL, self.TEST_USER_PASSWORD)


if __name__ == '__main__':

    unittest.main()