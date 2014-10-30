import StringIO

from item import Item
from os.path import exists, isdir, split, join
from errors import method_not_implemented, operation_not_allowed, invalid_argument
from private.buttfs_paths import VersionConflictValue, RestoreValue

class File(Item):
    def __init__(self, rest_interface):
        super(File, self).__init__(rest_interface)
        self.parent = None
        self.offset = 0

    def _refresh_request(self, debug=False):
        if debug:
            self.rest_interface.debug_requests(1)
        return self.rest_interface.file_get_meta(self.path()), {}

    @staticmethod
    def _get_download_callback(fp, close=True):
        # preserve env
        def callback(response):
            for chunk in response.iter_content(chunk_size=128):
                if chunk:
                    fp.write(chunk)
                    fp.flush()
            fp.seek(0)
            if close:
                fp.close()

        return callback

    def delete(self, commit=False, force=False, debug=False):
        """Delete the file.

        REST Documentation: https://www.bitcasa.com/cloudfs-api-docs/api/Delete%20File.html

        :param path:    Path to file to delete.
        :param commit:  If true, will permanently remove the file. Will move to trash otherwise. Defaults to False.
        :param debug:   If true, will print the the request and response to stdout.

        :returns:   Dictionary with keys for success and the deleted files last version.
        :raises SessionNotLinked:       ButtFSRESTAdapter is not authenticated.
        :raises AuthenticatedError:     Based on ButtFS Error Code.
        """
        if debug:
            self.rest_interface.debug_requests(1)
        if self.in_trash:
            if commit:
                return self.rest_interface.delete_trash_item(self.path())
            else:
                # nop
                # we're already in the trash, does not make sense to make a delete call if commit is not true.
                return {}
        else:
            result = self.rest_interface.delete_file(self.path(), commit)
            if result['success'] and commit == False:
                self.in_trash = True
            return result

    def save(self, if_conflict=VersionConflictValue.fail, debug=False):
        """Save changes to the file.
        See notes on individual setters for quirks.

        REST Documentation: https://www.bitcasa.com/cloudfs-api-docs/api/Alter%20File%20Meta.html

        :param if_conflict:    Behavior if the file has been updated since retrieving it from Buttfs.
        :param debug:          If true, will print the the request and response to stdout.

        :returns:  Updated file object
        :raises SessionNotLinked:       ButtFSRESTAdapter is not authenticated.
        :raises AuthenticatedError:     Based on ButtFS Error Code.
        """
        if debug:
            self.rest_interface.debug_requests(1)
        changes = {'version':self.data['version']}
        for changed_key in self.changed_meta:
            changes[changed_key] = self.data[changed_key]

        self.changed_meta.clear()
        response =  self.rest_interface.file_alter_meta(self.path(), changes, if_conflict)
        self._initialize_self(response, {})
        return self

    def wait_for_downloads(self, timeout=None):
        """ Wait for any threaded downloads started by this file.
        Warning: By default, this will be called without a timeout on deletion, preventing
        program close for some time. This can be avoided by calling this at least once with
        any timeout.

        :param timeout: Floating point number of seconds to wait. If none, waits indefinitely. Optional.
        :return: True if all downloads are complete. False otherwise.
        """
        return self.rest_interface.wait_for_downloads(timeout)

    def download(self, local_path, custom_name=None, synchronous=False, debug=False):
        """Download the file to the local filesystem.
        Does not replicate any metadata.
        If downloads are started with synchronous=True ButtFS SDK will attempt to block until all downloads are complete on destruction. This may block your
        program from exiting. To avoid this, call wait_for_downloads at least once with any arguments (i.e. call with a timeout of 0 to halt downloads immediately)

        REST Documentation: https://www.bitcasa.com/cloudfs-api-docs/api/Download%20File.html

        :param local_path:  Path on local filesystem. Can end with a file name, which will be created or overwritten. Will not create any folders.
        :param custom_name: Can use a separate argument to specify local file name. If file name is included in both local_path and this, local_path takes priority. Optional.
        :param synchronous: If true, download will return immediately and download in separate thread.
        :param debug:       If true, will print the the request and response to stdout.
        :return: None
        :raises SessionNotLinked:       ButtFSRESTAdapter is not authenticated.
        :raises AuthenticatedError:     Based on ButtFS Error Code.
        :raises InvalidArgument:        Based on ButtFS Error Code.
        """
        if debug:
            self.rest_interface.debug_requests(1)

        folder_path = None
        file_name = custom_name
        local_path_except = invalid_argument('local_path', 'Full path of a folder or file that exists. Alternatively, a non-existent file in an existing hierarchy of folders', local_path)

        if exists(local_path):
            if isdir(local_path):
                # use our name / custom name in directory
                folder_path = local_path
            else:
                # use whole users' path
                folder_path, file_name = split(local_path)
                if not file_name:
                    raise local_path_except
        else:
            folders, file = split(local_path)
            if exists(folders):
                file_name = file
                folder_path = folders
            else:
                raise local_path_except

        if not file_name:
            file_name = self.name


        full_path = join(folder_path, file_name)
        fp = open(full_path, 'wb')

        self.rest_interface.download(self.path(), self._get_download_callback(fp, True), background=(not synchronous))

    # file interface
    def read(self, size=None, debug=False):
        """File-like interface to read file. Reads size bytes from last offset.
        Reads file synchronously - does not start threads.
        Warning: Each read() call generates on request to ButtFS.

        REST Documentation: https://www.bitcasa.com/cloudfs-api-docs/api/Download%20File.html

        :param size:    Number of bytes to read. If None, will read entire file. Defaults to None.
        :param debug:   If true, will print the the request and response to stdout.
        :return:    File contents.
        """
        if debug:
            self.rest_interface.debug_requests(1)
        range = None
        fp = StringIO.StringIO()
        if size:
            range = [self.tell(), self.tell() + size]

        self.rest_interface.download(self.path(), self._get_download_callback(fp, False), range=range)

        return fp.read()

    def readline(self, size=None):
        raise method_not_implemented(self, 'readline')

    def readlines(self, sizehint=None):
        raise method_not_implemented(self, 'readlines')

    def seek(self, offset, whence=0):
        """Seek to the given offset in the file.

        :param offset:  Number of bytes to seek.
        :param whence:  Seek be
        :return:        resulting offset
        """
        if whence == 0:
            self.offset = offset
        if whence == 1:
            self.offset += offset
        if whence == 2:
            self.offset = self.data['length'] - offset

        if offset > self.size:
            offset = self.size
        if offset < 0:
            offset = 0

        return offset

    def tell(self):
        """
        :return: Current offset of file-like interface.
        """
        return self.offset

    def truncate(self, size=0):
        raise method_not_implemented(self, 'truncate')

    # Soon
    def write(self):
        raise method_not_implemented(self, 'write')

    def writelines(self):
        raise method_not_implemented(self, 'writelines')

    @property
    def extension(self):
        """
        :return: Extension of file.
        """
        return self.data['extension']

    @extension.setter
    def extension(self, new_extension):
        raise operation_not_allowed("Setting extension directly instead of name")

    @property
    def mime(self):
        """
        :return: Mime type of file.
        """
        return self.data['mime']

    @mime.setter
    def mime(self, new_mime):
        self.changed_meta.add('mime')
        self.data['mime'] = new_mime

    @property
    def size(self):
        return self.data['size']

    @size.setter
    def size(self, new_size):
         raise operation_not_allowed("Setting the size of an Item")

    def __str__(self):
        trash = 'trash' if self.in_trash else ''
        return "File[{}{}]:{}({} - {}) {} bytes".format(trash, str(self.path()), self.name.encode('utf-8'), self.extension.encode('utf-8'), self.mime.encode('utf-8'), self.size)
