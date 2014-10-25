from private.rest_api_adapter import CloudFSRESTAdapter

from user import User
from account import Account
from filesystem import Filesystem
from errors import session_not_linked_error

class Session(object):
    def __init__(self, endpoint, client_id, client_secret):
        self.rest_interface = CloudFSRESTAdapter(endpoint, client_id, client_secret)
        self.endpoint = endpoint
        self.client_id = client_id
        self.client_secret = client_secret

    # are we associated with an account?
    def is_linked(self, debug=False):
        """ Can this session make requests?
        :param debug:   If true, will print the the request and response to stdout.
        :return:        True if this session is currently authenticated, false otherwise.
        """
        if debug:
            self.rest_interface.debug_requests(1)
        return self.rest_interface.is_linked()

    # set any account credentials to nil
    def unlink(self):
        """ Discard current authentication.
        :return: None
        """
        self.rest_interface.unlink()

    # link this session to an account
    def authenticate(self, username, password, debug=False):
        """ Attempt to log into the given users' filesystem.
        :param username:    Username of the user.
        :param password:    Password of the user.
        :param debug:       If true, will print the the request and response to stdout.
        :return:            True if successful, False otherwise.
        """
        if debug:
            self.rest_interface.debug_requests(1)
        return self.rest_interface.authenticate(username, password)

    def get_user(self, debug=False):
        """Get an object describing the current user.
        :param debug:   If true, will print the the request and response to stdout.
        :return:        User object representing the current user.
        """
        if debug:
            self.rest_interface.debug_requests(1)

        return User(self.rest_interface.get_copy(),
                    self.rest_interface.user_profile())


    def get_account(self, debug=False):
        """Get an object describing the current users account.
        :param debug:   If true, will print the the request and response to stdout.
        :return:        Account object representing the current user account.
        """
        return Account(self.rest_interface.get_copy(),
                       self.rest_interface.user_profile())


    def get_filesystem(self):
        """
        :return: Filesystem object linked to this session.
        """
        return Filesystem(self.rest_interface.get_copy())