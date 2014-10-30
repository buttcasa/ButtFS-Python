# Used to store the rest_endpoints dictionary.
# It could go somewhere else, but this is an easy storage method.
# We could also offer this as a JSON object in a file to support
# other implementations.

class Values(object):

    allowed = []
    _name = ''

    @classmethod
    def legal_value(cls, value):
        return value in cls.allowed

    @classmethod
    def raise_exception(cls, value):
        from ..errors import invalid_argument
        raise invalid_argument(cls._name, cls.allowed, value)

class ExistValues(Values):
    overwrite = 'overwrite'
    fail = 'fail'
    rename = 'rename'
    reuse = 'reuse'
    _name = 'exists'

    allowed = [overwrite,
               fail,
               rename,
               reuse]


class VersionConflictValue(Values):
    fail = 'fail'
    ignore = 'ignore'
    _name = 'version conflict'

    allowed = [fail, ignore]


class RestoreValue(Values):
    fail = 'fail'
    rescue = 'rescue'
    recreate = 'recreate'

    allowed = [fail, rescue, recreate]


rest_endpoints = {
    # layout:
    # '<friendly name>': {
    #   'params': <dictionary of required parameters>
    #   'url': <url used, with {path} entry if necessary
    #   'data': <required post parameters>
    #   'method': <method string for request>

    # Note: paths are assumed to include a leading / to represent the root.
    # REST Documentation: https://www.bitcasa.com/cloudfs-api-docs/api/Ping.html
    'ping':{
        'params': {},
        'url':    '/v2/ping',
        'data':   {},
        'method': 'GET'
    },
    # REST Documentation: https://www.bitcasa.com/cloudfs-api-docs/api/Oauth2%20Password%20Credentials%20Grant.html
    'get oauth token':{
        'params': {},
        'url':    '/v2/oauth2/token',
        'data':   {'grant_type':'password'},
        'method': 'POST'
    },
    # REST Documentation: https://www.bitcasa.com/cloudfs-api-docs/api/Get%20Profile.html
    'get user profile':{
        'params': {},
        'url':    '/v2/user/profile/',
        'data':   {},
        'method': 'GET'
    },
    # REST Documentation: None :p
    'change user profile':{
        'params': {},
        'url':    '/v2/user/profile/',
        'data':   {},
        'method': 'POST'
    },
    # REST Documentation: https://www.bitcasa.com/cloudfs-api-docs/api/List%20Folder.html
    'list folder':{
        'params': {},
        'url':    '/v2/folders{path}',
        'data':   {},
        'method': 'GET'
    },
    # REST Documentation: https://www.bitcasa.com/cloudfs-api-docs/api/Create%20Folder.html
    'create folder':{
        'params': {'operation':'create'},
        'url':    '/v2/folders{path}',
        'data':   {},
        'method': 'POST'
    },
    # REST Documentation: https://www.bitcasa.com/cloudfs-api-docs/api/Delete%20Folder.html
    'delete folder':{
        'params': {'commit':'false', 'force':'false'},
        'url':    '/v2/folders{path}',
        'data':   {},
        'method': 'DELETE'
    },
    # REST Documentation: https://www.bitcasa.com/cloudfs-api-docs/api/Delete%20File.html
    'delete file':{
        'params': {'commit':'false'},
        'url':    '/v2/files{path}',
        'data':   {},
        'method': 'DELETE'
    },
    # REST Documentation: https://www.bitcasa.com/cloudfs-api-docs/api/Move%20File.html
    'move file':{
        'params': {'operation':'move'},
        'url':    '/v2/files{path}',
        'data':   {'to':'','exists':ExistValues.rename},
        'method': 'POST'
    },
    # REST Documentation: https://www.bitcasa.com/cloudfs-api-docs/api/Move%20Folder.html
    'move folder':{
        'params': {'operation':'move'},
        'url':    '/v2/folders{path}',
        'data':   {'to':'','exists':ExistValues.rename},
        'method': 'POST'
    },
    # REST Documentation: https://www.bitcasa.com/cloudfs-api-docs/api/Copy%20File.html
    'copy file':{
        'params': {'operation':'copy'},
        'url':    '/v2/files{path}',
        'data':   {'to':'','exists':ExistValues.rename},
        'method': 'POST'
    },
    # REST Documentation: https://www.bitcasa.com/cloudfs-api-docs/api/Copy%20Folder.html
    'copy folder':{
        'params': {'operation':'copy'},
        'url':    '/v2/folders{path}',
        'data':   {'to':'','exists':ExistValues.rename},
        'method': 'POST'
    },
    # REST Documentation: https://www.bitcasa.com/cloudfs-api-docs/api/Alter%20File%20Meta.html
    'alter file meta':{
        'params': {},
        'url':    '/v2/files{path}/meta',
        'data':   {'version-conflict': VersionConflictValue.fail},
        'method': 'POST'
    },
    # REST Documentation: https://www.bitcasa.com/cloudfs-api-docs/api/Alter%20Folder%20Meta.html
    'alter folder meta':{
        'params': {},
        'url':    '/v2/folders{path}/meta',
        'data':   {'version-conflict': VersionConflictValue.fail},
        'method': 'POST'
    },
    # REST Documentation: https://www.bitcasa.com/cloudfs-api-docs/api/Get%20File%20Meta.html
    'get file meta':{
        'params': {},
        'url':    '/v2/files{path}/meta',
        'data':   {},
        'method': 'GET'
    },
    # REST Documentation: https://www.bitcasa.com/cloudfs-api-docs/api/Get%20Folder%20Meta.html
    'get folder meta':{
        'params': {},
        'url':    '/v2/folders{path}/meta',
        'data':   {},
        'method': 'GET'
    },
    # REST Documentation: https://www.bitcasa.com/cloudfs-api-docs/api/Upload%20File.html
    'upload file':{
        'params': {},
        'url':    '/v2/files{path}/',
        'data':   {'exists':ExistValues.fail},
        'method': 'POST'
    },
    # REST Documentation: https://www.bitcasa.com/cloudfs-api-docs/api/Download%20File.html
    'download file':{
        'params': {},
        'url':    '/v2/files{path}',
        'data':   {},
        'method': 'GET'
    },
    # REST Documentation: https://www.bitcasa.com/cloudfs-api-docs/api/Browse%20Trash.html
    'list trash':{
        'params': {},
        'url':    '/v2/trash{path}',
        'data':   {},
        'method': 'GET'
    },
    # REST Documentation: https://www.bitcasa.com/cloudfs-api-docs/api/Delete%20Trash%20Item.html
    'delete trash item':{
        'params': {},
        'url':    '/v2/trash{path}',
        'data':   {},
        'method': 'DELETE'
    },
    # REST Documentation: https://www.bitcasa.com/cloudfs-api-docs/api/Recover%20Trash%20Item.html
    'recover trash item':{
        'params': {},
        'url':    '/v2/trash{path}',
        'data':   {'restore': RestoreValue.fail},
        'method': 'POST'
    }

}