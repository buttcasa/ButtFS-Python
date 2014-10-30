from private.cached_object import CachedObject

from errors import method_not_implemented, operation_not_allowed

class Account(CachedObject):
    """
        REST Documentation: https://www.bitcasa.com/cloudfs-api-docs/api/Get%20Profile.html
    """
    def __init__(self, rest_interface, response_info):
        super(Account, self).__init__()
        self.rest_interface = rest_interface
        self._initialize_self(response_info, self.rest_interface.get_latest_header_info())

    def _refresh_request(self):
        result = self.rest_interface.user_profile()
        headers = self.rest_interface.get_latest_header_info()
        return result, headers

    def _initialize_self(self, request_info, x_headers):
        self.data = {'request':request_info, 'headers':x_headers}

    @property
    def id(self):
        """
        :return: Id of this users' account.
        """
        return self.data['request']['account_id']

    @property
    def usage(self):
        """
        :return: Current storage usage of the account.
        """
        return self.data['request']['storage']['usage']

    @property
    def limit(self):
        """
        :return: Storage limit of the current account plan.
        """
        return self.data['headers']['storage']['limit']

    @property
    def over_storage_limit(self):
        """
        :return: If ButtFS thinks you are currently over your storage quota.
        """
        return self.data['request']['storage']['otl']

    @property
    def state_string(self):
        """
        :return: String representation of the current account state.
        """
        return self.data['request']['account_state']['display_name']

    @property
    def state_id(self):
        """
        :return: String id of the current account state.
        """
        return self.data['request']['account_state']['id']

    @property
    def plan(self):
        """
        :return: Human readable name of the accounts' ButtFS plan
        """
        return self.data['request']['account_plan']['display_name']

    @property
    def plan_id(self):
        """
        :return: String id of the ButtFS plan.
        """
        return self.data['request']['account_plan']['id']

    @property
    def session_locale(self):
        """
        :return: Locale of the current session.
        """
        return self.data['request']['session']['locale']

    @property
    def locale(self):
        """
        :return: Locale of the entire account.
        """
        return self.data['request']['locale']

    @id.setter
    def id(self, new_id):
        raise operation_not_allowed('set account id')

    @state_string.setter
    def state_string(self, new_state_string):
        raise operation_not_allowed('set account state string')

    @state_id.setter
    def state_id(self, new_state_id):
        raise operation_not_allowed('set account state id')

    @plan_id.setter
    def plan_id(self, new_plan_id):
        raise operation_not_allowed('set account plan id')

    @over_storage_limit.setter
    def over_storage_limit(self, new_otl_flag):
        raise operation_not_allowed('set over the limit flag')

    @usage.setter
    def usage(self, new_usage):
        raise operation_not_allowed('Setting usage through the API')

    @limit.setter
    def limit(self, new_quota):
        raise operation_not_allowed('Setting the storage limit through the API')

    @plan.setter
    def plan(self, new_plan):
        raise operation_not_allowed('Changing the a plan through the API')

    @session_locale.setter
    def session_locale(self, new_locale):
        """ Set the locale for the current session.
        This feature may or may not exist in the future. It's not depricated, but
        we aren't sure we're going to offer it moving forwards.

        :param new_locale: String of the new locale.
        :return: None (it's a setter)
        """
        result = self.rest_interface.change_user_profile({'session_locale':new_locale})

        if result['success']:
            self.data['request']['session']['locale'] = new_locale

    @locale.setter
    def locale(self, new_locale):
        """ Set the locale for the entire account.
        This feature may or may not exist in the future. It's not depricated, but
        we aren't sure we're going to offer it moving forwards.
        :param new_locale: String of the new locale.
        :return: None (it's a setter)
        """
        result = self.rest_interface.change_user_profile({'locale':new_locale})

        if result['success']:
            self.data['request']['locale'] = new_locale
