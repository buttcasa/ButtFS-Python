import unittest

from test_settings import ButtFSTestCase
from buttfs.session import Session
from buttfs import errors

class AccountTest(ButtFSTestCase):

    FORBIDDEN_SETTERS = ['id', 'usage', 'state_string', 'state_id',
                           'plan_id', 'over_storage_limit', 'usage',
                           'limit', 'plan']

    def setUp(self):
        self.s = Session(self.BUTTFS_BASE,
                self.BUTTFS_ID,
                self.BUTTFS_SECRET)

        self.assertRaises(
            errors.ButtFSError,
            self.s.get_account
        )

        self.s.authenticate(self.TEST_USER_EMAIL, self.TEST_USER_PASSWORD)
        self.assertEqual(True, self.s.is_linked(), "Authentication failed.")

    def get_example_object(self):
        return self.s.get_account()

    def test_account(self):
        acct = self.get_example_object()
        # basic field check
        self.assertTrue(acct.usage >= 0, 'Usage expected to be above 0!')
        self.assertEqual(acct.limit, None, 'Quota expected to be at "free" levels!')
        self.assertEqual(acct.plan, u'ButtFS End User', 'Account should be ButtFS End User Apparently!')
        self.assertTrue(acct.id is not '', 'Empty account id.')
        self.assertEqual(acct.usage < acct.limit, acct.over_storage_limit, 'Over storage limit flag does not reflect storage numbers!')
        self.assertEqual(acct.state_string, 'Active', 'Account is active!')
        self.assertTrue(acct.session_locale != '', 'Session locale not set!')
        self.assertTrue(acct.locale != '', 'Account locale not set!')

    def test_set_locale_account(self):
        acct = self.get_example_object()
        old_locale = acct.locale
        new_locale = 'en' if old_locale == 'de' else 'de'
        acct.locale = new_locale
        self.assertEqual(acct.locale, new_locale, 'Could not change account locale!')
        acct.locale = old_locale
        self.assertEqual(acct.locale, old_locale, 'Could not change account locale!')

    def test_set_locale_session(self):
        acct = self.get_example_object()
        old_locale = acct.session_locale
        new_locale = 'en' if old_locale == 'de' else 'de'
        acct.session_locale = new_locale
        self.assertEqual(acct.session_locale, new_locale, 'Could not change session locale!')
        acct.session_locale = old_locale
        self.assertEqual(acct.session_locale, old_locale, 'Could not change session locale!')

if __name__ == '__main__':
    unittest.main()
