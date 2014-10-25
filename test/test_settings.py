if __package__ is None:
    import os
    from os import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import datetime
from cloudfs.session import Session
from cloudfs.errors import OperationNotAllowed, MethodNotImplemented


class CloudFSTestCase(unittest.TestCase):
    # fill in with the details from your cloudfs account
    # Application Client ID
    CLOUDFS_ID = 'WFZLqxhV5Qz1KzUg9s-xMNlUPd804zygxouCG2pLWVg'
    # Application Secret
    CLOUDFS_SECRET = 'i_vz5d_GHADe9dHEKyMVTyqxrgU0UQDYOxgXuc1EisSulFzVs9he3CzFzygZh-84EhJyhk2l7T5nR6GnSMHLvQ'
    # Application API Server
    CLOUDFS_BASE = 'mmst1awe4a.cloudfs.io'

    # user settings
    TEST_USER_EMAIL = 'test@test.com'
    TEST_USER_PASSWORD = '111111'

    # not needed for setting up your account

    UNIMPLEMENTED_SETTERS = []
    FORBIDDEN_SETTERS = []

    def get_example_object(self):
        return None

    def test_unimplemented_setters(self):
        def set_attr_helper(property):
            setattr(self.get_example_object(), property, None)

        for method in self.UNIMPLEMENTED_SETTERS:
            self.assertRaises(
                MethodNotImplemented,
                set_attr_helper,
                method
            )

    def test_forbidden_setters(self):
        def set_attr_helper(property):
            setattr(self.get_example_object(), property, None)

        for method in self.FORBIDDEN_SETTERS:
            self.assertRaises(
                OperationNotAllowed,
                set_attr_helper,
                method
            )

    def current_time(self):
        now = datetime.datetime.now()
        return now - datetime.timedelta(microseconds=now.microsecond)

class SessionTestCase(CloudFSTestCase):
    def setUp(self):
        self.s = Session(self.CLOUDFS_BASE,
                self.CLOUDFS_ID,
                self.CLOUDFS_SECRET)

        self.s.authenticate(self.TEST_USER_EMAIL, self.TEST_USER_PASSWORD)
        self.assertEqual(True, self.s.is_linked(), "Authentication failed.")