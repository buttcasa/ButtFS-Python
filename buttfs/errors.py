import json
import inspect
from private.utils import request_to_string, response_to_string

class ButtFSError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

class SessionNotLinked(ButtFSError):
    def __init__(self):
        self.message = 'Session is not linked.'

class OperationNotAllowed(ButtFSError):
    def __init__(self, op_name):
        self.message = '{} is not possible in Buttfs. If you cannot work around this limitation, please contact ButtFS support.'.format(op_name)

class InvalidArgument(ButtFSError):
    def __init__(self, arg, expected, actual):
        self.message = 'Value for "{}" argument is not allowed. Expected {}, but argument had/was {}({}).'.format(
                arg, expected, actual, type(actual)
            )

class MissingArgument(ButtFSError):
    def __init__(self, arg_name):
        self.message = 'This call requires a {} argument.'.format(arg_name)

class MethodNotImplemented(ButtFSError):
    def __init__(self, object, method_name):
        self.message = 'The \"{}\" method of the {} is not currently implemented. To find out the future plans for this method contact ButtFS support.'.format(method_name, type(object))

def session_not_linked_error():
    return SessionNotLinked()

def operation_not_allowed(op_name):
    return OperationNotAllowed(op_name)

def invalid_argument(argument, expected, actual):
    return InvalidArgument(argument, expected, actual)

def missing_argument(arg_name):
    return MissingArgument(arg_name)

def method_not_implemented(object, method_name):
    return MethodNotImplemented(object, method_name)

class AuthenticatedError(ButtFSError):
    INTERNAL_CODE = None

    def __init__(self, request, response, message = '', code=None):
        self.response = response
        self.request = request
        self.message = message

        # support errors that can return several codes for the same problem
        if code and type(self.INTERNAL_CODE) is tuple:
            if code in self.INTERNAL_CODE:
                # sorted
                self.INTERNAL_CODE = code
            else:
                raise ValueError("Tried to create a {} using error code {}, which is not in the range of {}!".format(type(self), code, self.INTERNAL_CODE))


    def json(self):
        try:
            return json.loads(self.response.content)
        except:
            return self.response.content

    def code(self):
        return self.INTERNAL_CODE

    def status(self):
        return self.response.status_code

    def __str__(self):
        return '\nRequest:\n{}\nResponse:\n{}'.format(request_to_string(self.request), response_to_string(self.response))


class UnknownError(AuthenticatedError):
    def __str__(self):
        super_str = super(UnknownError, self).__str__()
        return "ButtFS returned an error with an unexpected error code! Please forward this exceptions' text to ButtFS support:\n" + super_str

class InvalidRequest(AuthenticatedError):
    # No code for malformed request
    INTERNAL_CODE = None

class GenericPanicError(AuthenticatedError):
    # generic error for when something goes wrong on ButtFS's end
    INTERNAL_CODE = 9999

# API Errors

class APIError(AuthenticatedError):
    INTERNAL_CODE = 9000

class APICallLimitReached(APIError):
    INTERNAL_CODE = 9006

# filesystem errors
# 5 errors
# 3 raised / exist

class FilesystemError(AuthenticatedError):
    # does not exist, but defines the domain
    INTERNAL_CODE = 8000

class InvalidVersion(FilesystemError):
    INTERNAL_CODE = 8001

class VersionMismatchIgnored(FilesystemError):
    INTERNAL_CODE = 8002

class OrigionalPathNoLongerExists(FilesystemError):
    INTERNAL_CODE = 8004

class FilesystemIsOverTheLimit(FilesystemError):
    INTERNAL_CODE = 8007

class FilesystemWouldBeOverTheLimit(FilesystemError):
    INTERNAL_CODE = 8008

# share errors
# 4 errors
# none raised / exist under other names

class ShareError(AuthenticatedError):
    INTERNAL_CODE = 6000

class PathRequired(ShareError):
    INTERNAL_CODE = 6001

class PathDoesNotExist(ShareError):
    INTERNAL_CODE = 6002

class ShareWouldExceedQuota(ShareError):
    INTERNAL_CODE = 6003

class ShareDoesNotExist(ShareError):
    INTERNAL_CODE = 6004

# file errors
# 14 errors
# 9 raised / all exist

class FileError(AuthenticatedError):
    # does not exist, but defines the domain
    INTERNAL_CODE = 3000

class FileNotFound(FileError):
    INTERNAL_CODE = 3001

class InvalidName(FileError):
    INTERNAL_CODE = 3008

class InvalidDateCreated(FileError):
    INTERNAL_CODE = 3011

class InvalidDateMetaLastModified(FileError):
    INTERNAL_CODE = 3012

class InvalidDateContentLastModified(FileError):
    INTERNAL_CODE = 3013

class SizeMustBePositive(FileError):
    INTERNAL_CODE = 3015

class NameRequired(FileError):
    INTERNAL_CODE = 3018

class ToPathRequired(FileError):
    INTERNAL_CODE = 3020

class VersionMissingOrIncorrect(FileError):
    INTERNAL_CODE = 3021

# File exceptions that are never raised from the server

class InvalidOperation(FileError):
    INTERNAL_CODE = 3007

class InvalidExists(FileError):
    INTERNAL_CODE = 3009

class ExtensionTooLong(FileError):
    INTERNAL_CODE = 3010

class MIMETooLong(FileError):
    INTERNAL_CODE = 3014

class SizeRequired(FileError):
    INTERNAL_CODE = 3019

# folder errors
# 42 errors
# 7 raised / all exist

# classes of errors:
# Does not exist
# invalid argument
# Permissions error
# read only errors
# Failed Operation
# conflict in args

# meta exception
class FolderError(AuthenticatedError):
    # does not exist, but defines the domain
    INTERNAL_CODE = 2000

class FolderDoesNotExist(FolderError):
    INTERNAL_CODE = 2002

class FolderNotFound(FolderError):
    INTERNAL_CODE = 2003

class MissingPathParameter(FolderError):
    INTERNAL_CODE = 2034

class NameConflictInOperation(FolderError):
    INTERNAL_CODE = 2042

class VersionMissingOrIncorrect(FolderError):
    INTERNAL_CODE = 2044

class NameRequred(FolderError):
    INTERNAL_CODE = 2047

class DirectoryNotEmpty(FolderError):
    INTERNAL_CODE = 2052

# Folder exceptions not currently raised

class UploadToReadOnlyDestinationFailed(FolderError):
    INTERNAL_CODE = 2004

class MoveToReadOnlyDestinationFailed(FolderError):
    INTERNAL_CODE = 2005

class CopyToReadOnlyDestinationFailed(FolderError):
    INTERNAL_CODE = 2006

class RenameOnReadOnlyLocationFailed(FolderError):
    INTERNAL_CODE = 2007

class DeleteOnReadOnlyLocationFailed(FolderError):
    INTERNAL_CODE = 2008

class CreateFolderOnReadOnlyLocationFailed(FolderError):
    INTERNAL_CODE = 2009

class FailedToReadFilesystem(FolderError):
    INTERNAL_CODE = (2010, 2011, 2012, 2013)

class NameConflictCreatingFolder(FolderError):
    INTERNAL_CODE = 2014

class NameConflictOnUpload(FolderError):
    INTERNAL_CODE = 2015

class NameConflictOnRename(FolderError):
    INTERNAL_CODE = 2016

class NameConflictOnMove(FolderError):
    INTERNAL_CODE = 2017

class NameConflictOnCopy(FolderError):
    INTERNAL_CODE = 2018

class FailedToSaveChanges(FolderError):
    INTERNAL_CODE = (2019, 2020, 2021, 2024, 2025)

class FailedToBroadcastUpdate(FolderError):
    INTERNAL_CODE = (2022, 2023)

class CannotDeleteTheInfiniteDrive(FolderError):
    INTERNAL_CODE = 2026

class MissingToParameter(FolderError):
    INTERNAL_CODE = 2028

class ExistsParameterInvalid(FolderError):
    INTERNAL_CODE = 2033

class SpecifiedLocationIsReadOnly(FolderError):
    INTERNAL_CODE = 2036

class SpecifiedSourceIsReadOnly(FolderError):
    INTERNAL_CODE = 2037

class SpecifiedDestinationIsReadOnly(FolderError):
    INTERNAL_CODE = 2038

class PathDoesNotExist(FolderError):
    INTERNAL_CODE = 2039

class PermissionDenied(FolderError):
    INTERNAL_CODE = (2040, 2041)

class InvalidOperation(FolderError):
    INTERNAL_CODE = 2043

class InvalidDepth(FolderError):
    INTERNAL_CODE = 2045

class VersionDoesNotExist(FolderError):
    INTERNAL_CODE = 2046

class InvalidName(FolderError):
    INTERNAL_CODE = 2048

class TreeRequired(FolderError):
    INTERNAL_CODE = 2049

class InvalidVerbose(FolderError):
    INTERNAL_CODE = 2050



_error_index = {
}

exception_names = dir()
module_objects = globals()

# build dictionary of exceptions indexed by codes
for name in exception_names:
    excpt = module_objects[name]
    if inspect.isclass(excpt) and issubclass(excpt, AuthenticatedError) and hasattr(excpt, 'INTERNAL_CODE'):
        if excpt.INTERNAL_CODE == None:
            continue
        elif type(excpt.INTERNAL_CODE) is tuple:
            for code in excpt.INTERNAL_CODE:
                _error_index[code] = excpt
        elif excpt.INTERNAL_CODE % 1000 != 0:
            # non-base exceptions
            _error_index[excpt.INTERNAL_CODE] = excpt
        elif excpt.INTERNAL_CODE % 1000 == 0:
            # meta exception
            continue
        else:
            raise ValueError("Exception {} incorrectly detected as a base exception!".format(excpt))


def error_from_response(request, response):
    if response.status_code == 200:
        return None

    try:
        response_json = json.loads(response.content)
    except:
        return AuthenticatedError(request, response)

    # we can do this
    if 'error' in response_json:
        if response_json['error'] == 'invalid_request':
            return InvalidRequest(request, response)
        elif 'code' in response_json['error']:
            code = int(response_json['error']['code'])
            message = response_json['error']['message']
            try:
                error_class = _error_index[code]
            except KeyError:
                # ButtFS instead of authenticated error because we don't really know
                raise UnknownError(request, response, message)

            return error_class(request, response, message)

    return AuthenticatedError(request, response)
