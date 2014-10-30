from private.cached_object import CachedObject

from errors import operation_not_allowed, method_not_implemented

class User(CachedObject):
    """
    REST Documentation: https://www.bitcasa.com/cloudfs-api-docs/api/Get%20Profile.html
    """
    def __init__(self, rest_interface, account_info):
        super(User, self).__init__()
        self.rest_interface = rest_interface
        self._initialize_self(account_info, {})

    def _refresh_request(self, debug=False):
        if debug:
            self.rest_interface.debug_requests(1)
        result = self.rest_interface.user_profile()
        return result, {}

    def _initialize_self(self, request_info, x_headers):
        self.data = request_info

    @property
    def email(self):
        return self.data['email']

    @property
    def first_name(self):
        return self.data['first_name']

    @property
    def last_name(self):
        return self.data['last_name']

    @property
    def id(self):
        return self.data['id']

    @property
    def username(self):
        return self.data['username']

    # unlike file times, these are in milliseconds
    @property
    def last_login(self):
        """
        :return: Last login time. Time is in milliseconds unlike other timestamps.
        """
        return self.data['last_login']

    # unlike file times, these are in milliseconds
    @property
    def created_at(self):
        """
        :return: Creation time. Time is in milliseconds unlike other timestamps.
        """
        return self.data['created_at']

    @email.setter
    def email(self, new_email):
        raise method_not_implemented(self, 'set user email')

    @first_name.setter
    def first_name(self, new_first_name):
        raise method_not_implemented(self, 'set user first name')

    @last_name.setter
    def last_name(self, new_last_name):
        raise method_not_implemented(self, 'set user last name')

    @id.setter
    def id(self, new_id):
        raise operation_not_allowed('Changing a users id')

    @username.setter
    def username(self, new_username):
        raise operation_not_allowed('Changing a users username')

    @last_login.setter
    def last_login(self, new_last_login):
        raise operation_not_allowed('Setting a users last login time')

    @created_at.setter
    def created_at(self, new_created_at):
        raise operation_not_allowed('Setting a the time a user was created')

    def save(self):
        raise method_not_implemented('User', 'save changes')

    def __dict__(self):
        return {'email': self.email,
                'first_name': self.first_name,
                'last_name': self.last_name}

    def __str__(self):
        return "ButtFS::User{dict}".format(
            dict=self.__dict__()
        )
