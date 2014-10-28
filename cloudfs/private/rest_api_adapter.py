import requests
import datetime
import base64
import hmac
import json
import hashlib
import threading
from copy import deepcopy

from utils import request_to_string, response_to_string, utf8_quote_plus, make_utf8
from ..errors import error_from_response, session_not_linked_error, CloudFSError, missing_argument, invalid_argument
from cloudfs_paths import rest_endpoints, ExistValues, VersionConflictValue, RestoreValue
from cached_object import CachedObject

debug = False

class CloudFSRESTAdapter(CachedObject):
    def __init__(self, url_root, client_id, secret,  auth_token=''):
        super(CloudFSRESTAdapter, self).__init__()
        self.bc_conn = CloudFSConnection(url_root, client_id, secret,  auth_token)
        self.linked = False
        self.debug_count = 0

    #a nop, the real work is done in _initialize_self
    def _refresh_request(self, debug=False):
        if debug:
            self.rest_interface.debug_requests(1)
        return {},{}

    def _initialize_self(self, request_info, x_headers):
        try:
            self.ping()
            self.linked = True
        except CloudFSError:
            self.linked = False

    def wait_for_downloads(self, timeout=None):
        """Wait for any threaded downloads that have not completed

        :param timeout: Float number of seconds to wait or None to wait until downloads are done. Defaults to None.
        :return: True if all downloads are done, False otherwise.
        """
        return self.bc_conn.join_threads(timeout)

    def get_copy(self):
        """Returns a copy of the rest interface

        get_copy exists to centralize invalidation of a session.
        Current behavior is to allow 'children' of the session to continue
        refreshing their information as time goes on. However, we can change
        behavior in the future.

        :returns:   A CloudFSRESTAdapter that is authenticated to the same account as self.

        """
        return deepcopy(self)

    def debug_requests(self, count):
        """Print information for future requests.
        Warning: These print statements do not censor personal information or authentication data.
        Do not transmit in the clear under any circumstances!

        :param count:       Number of requests to print

        :returns:           None

        """
        self.debug_count += count

    def get_last_request_log(self):
        """Get string of last request. Useful for logging requests.
        Warning: These string do not censor personal information or authentication data.
        Do not transmit in the clear under any circumstances!

        Will return an empty string when no request has been made.
        :return: String of last request and response.
        """

        return self.bc_conn.last_request_log

    def is_linked(self):
        """Return if this CloudFSRESTAdapter can currently make requests.
        Does not use up an API request.

        :returns:       True if this is authenticated to the server. False otherwise.

        """
        if self.bc_conn.auth_token != '':
            self._prepare_to_read()

        return self.linked

    def unlink(self):
        """Clear current authentication information associated with this CloudFSRESTAdapter

        :returns:       None

        """
        self.bc_conn.auth_token = ''
        self.linked = False

    def get_latest_header_info(self):
        """Return the latest version if the information encoded in response headers.
        Currently, this is some storage quota information (number of bytes stored, current limit).
        It's reflected in the Account object of the SDK.

        :returns:   Dictionary with information encoded in the headers.

        """
        return self.bc_conn.header_information

    def _make_request(self, request_name, path=None, data={}, params={}, headers={}, response_processor=None, files=None, oauth_request=False, background=False):
        """Makes a request after merging standard request parameters with user-supplied data

        :param request_name:        Index into the rest_endpoints table in cloudfs_paths.py.
        :param path:                Path in the CloudFS Filesystem. Optional.
        :param data:                Post data in encoded in dictionary. Optional.
        :param params:              URL Parameters in dictionary. Optional.
        :params headers:            Headers in dictionary. Optional.
        :param response_processor:  Function to process response value. Optional.
        :param files:               Files to post. Optional.
        :param oauth_request:       Flag to indicate if this is an 'oauth' request (does not follow strict oauth flow, see CloudFS docs). Optional.
        :param background:          Flag to indicate if this request should return before completing the entire body

        :returns:   Dictionary of JSON request or string of response body. True or False for oauth_request.
        :raises ValueError:             request_name is not found in rest_endpoints.
        :raises SessionNotLinked:       CloudFSRESTAdapter is not authenticated.
        :raises AuthenticatedError:     Based on CloudFS returns an error.

        """
        try:
            request_data = rest_endpoints[request_name]
        except ValueError:
            raise ValueError('Could not find friendly rest endpoint named "{}".'.format(request_name))

        # need to re-create to avoid modifying rest_endpoints or default values
        merged_data = {}
        merged_params = {}

        merged_data.update(request_data['data'])
        merged_data.update(data)
        merged_params.update(request_data['params'])
        merged_params.update(params)

        url = request_data['url']
        if url.find('{path}') > 0:
            url = url.format(path=str(path))

        # track this here
        if self.debug_count > 0:
            self.bc_conn.debug_next_request()
            self.debug_count -= 1

        if oauth_request:
            return self.bc_conn.oauth_request(url, merged_data, merged_params, request_data['method'])
        else:
            return self.bc_conn.request(url, merged_data, merged_params, files, request_data['method'], response_processor, headers, background)

    def authenticate(self, username, password):
        """Authenticate to CloudFS using the provided user details.

        REST Documentation: https://www.bitcasa.com/cloudfs-api-docs/api/Oauth2%20Password%20Credentials%20Grant.html

        :param username:        Username of the user.
        :param password:        Password of the user.

        :returns: True if successful and False otherwise.

        """
        data = {
            'username':username,
            'password':password
        }
        self._make_request('get oauth token', data=data, oauth_request=True)

    def ping(self):
        """Check that authentication is still valid

        REST Documentation: https://www.bitcasa.com/cloudfs-api-docs/api/Ping.html

        :returns:   Empty string if successful, exception if not.
        :raises:    SessionNotLinked if the CloudFSRESTAdapter is not authenticated.

        """
        return self._make_request('ping')

    def list_folder(self, path):
        """List the contents of the folder.

        REST Documentation: https://www.bitcasa.com/cloudfs-api-docs/api/List%20Folder.html

        :param path:    Path to folder to list.

        :returns:   Dictionary representation of JSON response.
        :raises SessionNotLinked:       CloudFSRESTAdapter is not authenticated.
        :raises AuthenticatedError:     Based on CloudFS Error Code.

        """
        return self._make_request('list folder', path)

    def user_profile(self):
        """Returns the profile of the currently authenticated user.

        REST Documentation: https://www.bitcasa.com/cloudfs-api-docs/api/Get%20Profile.html

        :returns:   Dictionary encoding of the user profile information.
        :raises SessionNotLinked:       CloudFSRESTAdapter is not authenticated.
        :raises AuthenticatedError:     Based on CloudFS Error Code.

        """
        return self._make_request('get user profile')

    def change_user_profile(self, data):
        """Update the user profile.
        Currently mostly non-functional.

        :param data:    Dictionary of settings to change

        :returns:   Dictionary with a key indicating success.
        :raises SessionNotLinked:       CloudFSRESTAdapter is not authenticated.
        :raises AuthenticatedError:     Based on CloudFS Error Code.

        """
        return self._make_request('change user profile', data=data)

    def create_folder(self, path, name, exists=ExistValues.overwrite):
        """Create a folder.

        REST Documentation: https://www.bitcasa.com/cloudfs-api-docs/api/Create%20Folder.html

        :param path:    Parent folder for the new folder.
        :param name:    Name of the new folder.
        :parm exists:   Behavior if folder name already exists. Default Value overwrite

        :returns:   Dictionary encoded information about the new folder.
        :raises SessionNotLinked:       CloudFSRESTAdapter is not authenticated.
        :raises AuthenticatedError:     Based on CloudFS Error Code.

        """
        data = {
            'name':name,
            'exists':exists
        }
        return self._make_request('create folder', path, data=data)

    def delete_folder(self, path, commit=False, force=False):
        """Delete a folder.

        REST Documentation: https://www.bitcasa.com/cloudfs-api-docs/api/Delete%20Folder.html

        :param path:        Path to folder that will be deleted.
        :param commit:      If true, will permanently remove the folder. Will move to trash otherwise. Defaults to False.
        :param force:       If true, will delete folder even if it contains Items. Defaults to False.

        :returns:   Dictionary with keys for success and the deleted folders last version.
        :raises SessionNotLinked:       CloudFSRESTAdapter is not authenticated.
        :raises AuthenticatedError:     Based on CloudFS Error Code.

        """
        params = {
            'commit':str(commit),
            'force':str(force),
        }

        return self._make_request('delete folder', path, params=params)

    def delete_file(self, path, commit=False):
        """Delete a file.

        REST Documentation: https://www.bitcasa.com/cloudfs-api-docs/api/Delete%20File.html

        :param path:        Path to file to delete.
        :param commit:      If true, will permanently remove the file. Will move to trash otherwise. Defaults to False.

        :returns:   Dictionary with keys for success and the deleted files last version.
        :raises SessionNotLinked:       CloudFSRESTAdapter is not authenticated.
        :raises AuthenticatedError:     Based on CloudFS Error Code.

        """
        params = {
            'commit':str(commit),
        }

        return self._make_request('delete file', path, params=params)

    def _common_file_operation(self, verb, path, destination, destination_name, exists=None):
        data = {
            'to': destination,
            'name': destination_name
        }
        if exists:
            if ExistValues.legal_value(exists):
                data['exists'] = exists
            else:
                ExistValues.raise_exception(exists)

        return self._make_request(verb, path, data=data)

    def move_file(self, path, destination, destination_name, exists=None):
        """Move a file to another location.

        REST Documentation: https://www.bitcasa.com/cloudfs-api-docs/api/Move%20File.html

        :param path:                Location of the item to move.
        :param destination:         Path to destination folder.
        :param destination_name:    Name of new item to create in the destination folder.
        :param exists:              How to handle if an item of the same name exists in the destination folder. Defaults to rename.

        :returns:   Details of the new item in a dictionary.
        :raises SessionNotLinked:       CloudFSRESTAdapter is not authenticated.
        :raises AuthenticatedError:     Based on CloudFS Error Code.

        """
        return self._common_file_operation('move file', path, destination, destination_name, exists)

    def move_folder(self, path, destination, destination_name, exists=None):
        """Move folder to another location.

        REST Documentation: https://www.bitcasa.com/cloudfs-api-docs/api/Move%20Folder.html

        :param path:                Location of the item to move.
        :param destination:         Path to destination folder.
        :param destination_name:    Name of new item to create in the destination folder.
        :param exists:              How to handle if an item of the same name exists in the destination folder. Defaults to rename.

        :returns:   Details of the new item in a dictionary.
        :raises SessionNotLinked:       CloudFSRESTAdapter is not authenticated.
        :raises AuthenticatedError:     Based on CloudFS Error Code.

        """
        return self._common_file_operation('move folder', path, destination, destination_name, exists)

    def copy_file(self, path, destination, destination_name, exists=None):
        """Create a copy of this file at another location.

        REST Documentation: https://www.bitcasa.com/cloudfs-api-docs/api/Copy%20File.html

        :param path:                Location of the item to move.
        :param destination:         Path to destination folder.
        :param destination_name:    Name of new item to create in the destination folder.
        :param exists:              How to handle if an item of the same name exists in the destination folder. Defaults to rename.

        :returns:   Details of the new item in a dictionary.
        :raises SessionNotLinked:       CloudFSRESTAdapter is not authenticated.
        :raises AuthenticatedError:     Based on CloudFS Error Code.

        """
        return self._common_file_operation('copy file', path, destination, destination_name, exists)

    def copy_folder(self, path, destination, destination_name, exists=None):
        """Create a copy of this folder at another location.

        REST Documentation: https://www.bitcasa.com/cloudfs-api-docs/api/Copy%20Folder.html

        :param path:                Location of the item to move.
        :param destination:         Path to destination folder.
        :param destination_name:    Name of new item to create in the destination folder.
        :param exists:              How to handle if an item of the same name exists in the destination folder. Defaults to rename.

        :returns:   Details of the new item in a dictionary.
        :raises SessionNotLinked:       CloudFSRESTAdapter is not authenticated.
        :raises AuthenticatedError:     Based on CloudFS Error Code.

        """
        return self._common_file_operation('copy folder', path, destination, destination_name, exists)

    def _alter_meta(self, verb, path, data, whitelist, conflict):
        def remove(x):
            if x not in whitelist:
                del data[x]
        map(remove, data.keys())
        if conflict:
            if not VersionConflictValue.legal_value(conflict):
                VersionConflictValue.raise_exception(conflict)
            data['version-conflict'] = conflict
        if 'version' not in data:
            raise missing_argument('data.version')

        return self._make_request(verb, path, data=data)

    def file_alter_meta(self, path, data, conflict=None):
        """Alter the meta data of a file.

        REST Documentation: https://www.bitcasa.com/cloudfs-api-docs/api/Alter%20File%20Meta.html

        :param path:        Path of file to alter.
        :param data:        Dictionary of value keys and their new values.
        :param conflict:    Behavior if the file has been updated since retrieving it from Cloudfs.

        :returns:   Dictionary with new file details stored under the 'meta' key.
        :raises SessionNotLinked:       CloudFSRESTAdapter is not authenticated.
        :raises AuthenticatedError:     Based on CloudFS Error Code.

        """
        whitelist = ['name', 'date_created', 'date_meta_last_modified', 'application_data', 'mime', 'version']
        return self._alter_meta('alter file meta', path, data, whitelist, conflict)

    def folder_alter_meta(self, path, data, conflict=None):
        """Alter the meta data of a folder.

        REST Documentation: https://www.bitcasa.com/cloudfs-api-docs/api/Alter%20Folder%20Meta.html

        :param path:        Path of folder to alter.
        :param data:        Dictionary of value keys and their new values.
        :param conflict:    Behavior if the folder has been updated since retrieving it from Cloudfs.

        :returns:   Dictionary with new folder details stored under the 'meta' key.
        :raises SessionNotLinked:       CloudFSRESTAdapter is not authenticated.
        :raises AuthenticatedError:     Based on CloudFS Error Code.

        """
        whitelist = ['name', 'date_created', 'date_meta_last_modified', 'application_data', 'version']
        return self._alter_meta('alter folder meta', path, data, whitelist, conflict)

    def file_get_meta(self, path):
        """Get the meta data for a single file.

        REST Documentation: https://www.bitcasa.com/cloudfs-api-docs/api/Get%20File%20Meta.html

        :param path:    Path to file.

        :returns:   Dictionary with file details.
        :raises SessionNotLinked:       CloudFSRESTAdapter is not authenticated.
        :raises AuthenticatedError:     Based on CloudFS Error Code.

        """
        return self._make_request('get file meta', path)

    def folder_get_meta(self, path):
        """Get the meta data for a single folder.

        REST Documentation: https://www.bitcasa.com/cloudfs-api-docs/api/Get%20Folder%20Meta.html

        :param path:    Path to file.

        :returns:   Dictionary with folder details.
        :raises SessionNotLinked:       CloudFSRESTAdapter is not authenticated.
        :raises AuthenticatedError:     Based on CloudFS Error Code.

        """
        return self._make_request('get folder meta', path)

    def upload(self, path, file, exists=None, reuse_fallback=None, reuse_attributes=None):
        """Upload a file to Cloudfs.

        REST Documentation: https://www.bitcasa.com/cloudfs-api-docs/api/Upload%20File.html

        :param path:                Folder to upload this file to.
        :param file:                File information. Formatted like POSTing files in Requests.
        :param exists:              Determines behavior if a file of the same name exists. Default behavior is fail.
        :param reuse_fallback:      Not implemented.
        :param reuse_attributes:    Not implemented.

        :returns:                       Dictionary of new file details.
        :raises SessionNotLinked:       CloudFSRESTAdapter is not authenticated.
        :raises AuthenticatedError:     Based on CloudFS Error Code.

        """
        data = {}
        if exists:
            data['exists'] = exists
        if reuse_fallback or reuse_attributes:
            if not reuse_fallback:
                raise missing_argument('reuse-fallback')
            if not reuse_attributes:
                raise missing_argument('reuse-attributes')
            #data['reuse-fallback'] = reuse_fallback
            #data['reuse-attributes'] = reuse_attributes

        return self._make_request('upload file', path, data=data, files=file)

    def download(self, path, save_data_function, range=None, background=False):
        """Download a file.
        If background is set to true, the rest adapter will do its best to allow the download to finish. This means that __del__ will block more-or-less forever.
        See the finish_downloads method on session to deal with this.

        REST Documentation: https://www.bitcasa.com/cloudfs-api-docs/api/Download%20File.html

        :param path:                Path to file to download.
        :param save_data_function:  Function will be called with the response as an argument in order to process the requests' content. Used to save file in the background.
        :param range:               List or tuple with two values containing the range of the request. Second value may be an empty string, but must exist and not be none. Defaults to entire file.
        :param background:          If true, request will return immediately and save_data_function will run in a thread. Defaults to False.

        :returns:                       Empty string.
        :raises SessionNotLinked:       CloudFSRESTAdapter is not authenticated.
        :raises AuthenticatedError:     Based on CloudFS Error Code.
        :raises InvalidArgument:        Based on CloudFS Error Code.

        """
        headers = {}
        if range:
            if not hasattr(range, '__iter__') or len(range) != 2:
                raise invalid_argument('range argument', 'list type of length 2', range)
            headers['Range'] = 'bytes={}-{}'.format(range[0], range[1])
        return self._make_request('download file', path, response_processor=save_data_function, headers=headers, background=background)

    def list_trash(self, path):
        """List the contents of a folder in trash.

        REST Documentation: https://www.bitcasa.com/cloudfs-api-docs/api/Browse%20Trash.html

        :param path:        Path to folder to list.

        :returns:                       Dictionary representation of items in folder.
        :raises SessionNotLinked:       CloudFSRESTAdapter is not authenticated.
        :raises AuthenticatedError:     Based on CloudFS Error Code.
        """
        return self._make_request('list trash', path)

    def delete_trash_item(self, path):
        """Permanently remove an item from the users' filesystem.

        Warning: After calling this interface, there is _no way_ to retrieve the item deleted.

        REST Documentation: https://www.bitcasa.com/cloudfs-api-docs/api/Delete%20Trash%20Item.html

        :param path:        Path to item to delete.
        :return:            None
        :raises SessionNotLinked:       CloudFSRESTAdapter is not authenticated.
        :raises AuthenticatedError:     Based on CloudFS Error Code.
        """
        return self._make_request('delete trash item', path)

    def restore_trash_item(self, path, restore_method=RestoreValue.fail, method_argument=None):
        """Move an item from trash to the mail filesystem.

        Behavior for this call depends on the method selected.
        fail: Will attempt to move the item to its previous location.
        rescue: Will attempt to move the item to a different location, supplied in method_argument.
        recreate: Will attempt to create a new folder at the filesystem root with the name

        REST Documentation: https://www.bitcasa.com/cloudfs-api-docs/api/Recover%20Trash%20Item.html

        :param path:            Path to item to delete.
        :param restore_method:  Determines method used to restore item.
        :param method_argument: Expected contents determined by value of restore_method
        :return:
        :raises SessionNotLinked:       CloudFSRESTAdapter is not authenticated.
        :raises AuthenticatedError:     Based on CloudFS Error Code.
        """
        if not RestoreValue.legal_value(restore_method):
            raise RestoreValue.raise_exception(restore_method)
        data = {'restore': restore_method}
        if restore_method == RestoreValue.rescue:
            if hasattr(method_argument, 'path'):
                method_argument = method_argument.path()
            data['rescue-path'] = method_argument
        elif restore_method == RestoreValue.recreate:
            data['recreate-path'] = method_argument

        return self._make_request('recover trash item', path, data=data)


class CloudFSConnection(object):
    def __init__(self, url_root, client_id, secret,  auth_token=''):
        super(CloudFSConnection, self).__init__()
        self.url_root = url_root.strip('/')
        self.client_id = client_id
        self.secret = secret
        self.auth_token = auth_token
        self.header_information = {}
        self.debug_one_request = False
        self.threads = []
        self.threads_joined = False
        self.last_request_log = ''

    def __del__(self):
        if not self.threads_joined:
            self.join_threads()

    def debug_next_request(self):
        self.debug_one_request = True

    def join_threads(self, thread_timeout=None):
        all_threads_joined = True
        for thread in self.threads:
            thread.join(thread_timeout)
            all_threads_joined = all_threads_joined and not thread.isAlive()

        self.threads_joined = True

        return all_threads_joined

    def oauth_request(self, path, data={}, params={}, method='GET'):
        result = self._request(path, method, data=data, params=params, oauth=True)
        if 'access_token' in result:
            self.auth_token = result['access_token']
            return True

        return False

    def request(self, path, data={}, params={}, files=None, method='GET', response_processor=None, headers={}, background=False):
        default_headers = {'Authorization':'Bearer {}'.format(self.auth_token)}
        if self.auth_token != '':
            default_headers.update(headers)
            result = self._request(path, method, data, default_headers, params, files, response_processor, background=background)

            if 'result' in result:
                return result['result']
            else:
                return result
        else:
            raise session_not_linked_error()

    def _get_base_headers(self, oauth=False):
        headers = {}
        if oauth:
            headers['Content-Type'] = 'application/x-www-form-urlencoded; charset="utf-8"'
        headers['Date'] = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')

        return headers

    # where the magic happens
    def _sign_request(self, method, path, query, headers):

        interesting_headers = ['content-type', 'date']

        def encode_dictionary(d, sep, filter=None):
            dict_to_encode = {}
            sort_keys = {}
            order = []
            encoded_options = []

            if filter != None:
                for key in d.keys():
                    if key.lower() in filter:
                        dict_to_encode[key] = d[key]
            else:
                dict_to_encode = d

            for key in dict_to_encode.keys():
                sort_key = '{}/{}'.format(key.lower(), str(dict_to_encode[key]).lower())
                sort_keys[sort_key] = key

            sorted_keys = sorted(sort_keys.keys())
            for key in sorted_keys:
                order.append(sort_keys[key])

            for key in order:
                encoded_options.append('{encoded_key}{sep}{encoded_value}'.format(
                    encoded_key=utf8_quote_plus(key),
                    sep=sep,
                    encoded_value=utf8_quote_plus(dict_to_encode[key])
                ))

            return '&'.join(encoded_options)

        sig_hmac = hmac.new(make_utf8(self.secret), digestmod=hashlib.sha1)

        digest = '{method}&{path}&{query}&{headers}'.format(
            method=method,
            path=path,
            query=encode_dictionary(query, '='),
            headers=encode_dictionary(headers, ':', interesting_headers)
        )

        sig_hmac.update(digest)

        signature = base64.encodestring(sig_hmac.digest()).strip()

        headers['Authorization'] = 'BCS {}:{}'.format(self.client_id, signature)

        return headers

    def _save_x_headers(self, headers):
        header_data = {}
        headers_to_parse = [
            # format:
            # outer dict key, header name, inner dict key
            ['storage', 'X-BCS-Account-Storage-Limit', 'limit'],
            ['storage', 'X-BCS-Account-Storage-Usage', 'usage'],
        ]

        for header_info in headers_to_parse:
            if header_info[1] in headers:
                if header_info[0] not in header_data:
                    header_data[header_info[0]] = {}

                header_data[header_info[0]][header_info[2]] = headers[header_info[1]]

                if headers[header_info[1]] == 'None':
                    header_data[header_info[0]][header_info[2]] = None

        self.header_information = header_data

    # must use string or unicode values, as urllib has
    # unpredictable behavior when dealing with objects
    def _filter_arg_dictonary(self, dict):
        filtered_dict = {}
        for k, v in dict.iteritems():
            filtered_key = k
            filtered_value = v

            if type(k) is not str and type(k) is not unicode:
                filtered_key = str(k            )
            if type(v) is not str and type(v) is not unicode:
                filtered_value = str(v)
            filtered_dict[filtered_key] = filtered_value

        return filtered_dict

    # TODO: add streaming requests for downloads!
    def _request(self, path, method, data={}, headers={}, params={}, files=None, response_processor=None, oauth=False, background=False):
        single_debug = self.debug_one_request
        self.debug_one_request = False

        data = self._filter_arg_dictonary(data)
        params = self._filter_arg_dictonary(params)
        method = method.upper()
        headers.update(self._get_base_headers(oauth))
        if oauth:
            headers = self._sign_request(method, path, data, headers)
        url = 'https://{}{}'.format(self.url_root, path)

        base_request = requests.Request(method, url, headers, data=data, params=params, files=files)
        prepared_request = base_request.prepare()

        response = requests.Session().send(prepared_request, stream=background)


        self.last_request_log = 'Request:\n{}Response:\n{}'.format(request_to_string(prepared_request), response_to_string(response))
        if debug or single_debug:
            print self.last_request_log

        if response.status_code == 200:
            self._save_x_headers(response.headers)

            if response_processor:
                # clear out old threads if possible
                if background:
                    thread = threading.Thread(target=response_processor, args=(response,))
                    # yolo!
                    thread.start()
                    self.threads.append(thread)
                    # not sure how to clean this up properly.
                else:
                    response_processor(response)

            if 'application/json' in response.headers['Content-Type']:
                return json.loads(response.content)
            else:
                return response.content
        else:
            raise error_from_response(prepared_request, response)