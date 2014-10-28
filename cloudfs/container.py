import os

from item import Item
from path import Path
from private.filesystem_common import list_items_from_path, create_items_from_json
from private.cloudfs_paths import VersionConflictValue, ExistValues


class Container(Item):
    """
    The Container class exists as a basis for the Share item, which does not exist yet (0.5).
    """
    def __init__(self, rest_interface):
        super(Container, self).__init__(rest_interface)
        self._full_path = Path.path_from_string('/')

    def list(self, debug=False):
        """List the contents of this container.

        REST Documentation: https://www.bitcasa.com/cloudfs-api-docs/api/List%20Folder.html

        :param debug: If true, will print the the request and response to stdout.
        :return: Array of Items in container.
        """
        if debug:
            self.rest_interface.debug_requests(1)
        return list_items_from_path(self.rest_interface, self.path(), self.in_trash)

    def __str__(self):
        return 'container:' + self.path()

class Folder(Container):
    @staticmethod
    def root_folder(rest_interface):
        f = Folder(rest_interface)
        f.data = {
            'name':'ROOT',
            'id':'',
            'type':'folder',
            'is_mirrored': False,
            'date_content_last_modified':0,
            'date_created':0,
            'date_meta_last_modified':0,
            'application_data':{}
            }

        return f

    def __init__(self, rest_interface):
        super(Folder, self).__init__(rest_interface)

    def _refresh_request(self, debug=False):
        if debug:
            self.rest_interface.debug_requests(1)
        return self.rest_interface.folder_get_meta(self.path()), {}

    def upload(self, source, custom_name=None, custom_mime=None, exists=ExistValues.fail, data_inline=False, debug=False):
        """Upload a file or a string to CloudFS.

        REST Documentation: https://www.bitcasa.com/cloudfs-api-docs/api/Upload%20File.html

        :param source:          Source of file data. String or path to a file.
        :param custom_name:     Name of file in CloudFS. If left blank, will use name of file in path.
        :param custom_mime:     Mine for new file. If left blank, mime will be detected.
        :param exists:          Behavior if the given name exists on CloudFS. Defaults to fail.
        :param data_inline:     Flag to indicate if the source is a string or a filename.
        :param debug:           If true, will print the the request and response to stdout.

        :returns:   New file object.
        :raises SessionNotLinked:       CloudFSRESTAdapter is not authenticated.
        :raises AuthenticatedError:     Based on CloudFS Error Code.
        """
        if debug:
            self.rest_interface.debug_requests(1)
        if not custom_name:
            custom_name = os.path.basename(source)

        file_data = source
        if not data_inline:
            file_data = open(file_data, 'rb')

        files = {'file':[custom_name, file_data]}

        if custom_mime:
            files['file'].append(custom_mime)

        upload_response = self.rest_interface.upload(self.path(), files, exists)
        return create_items_from_json(self.rest_interface, upload_response, self.path(), self.in_trash)[0]

    def create_folder(self, container_or_name, exists=ExistValues.fail, debug=False):
        """Create a new folder in this folder.

        REST Documentation: https://www.bitcasa.com/cloudfs-api-docs/api/Create%20Folder.html

        :param container_or_name:   Container or String name. If arg is a Container, will use that Containers name.
        :param debug:               If true, will print the the request and response to stdout.

        :returns:       New folder object.
        :raises SessionNotLinked:       CloudFSRESTAdapter is not authenticated.
        :raises AuthenticatedError:     Based on CloudFS Error Code.
        """
        if debug:
            self.rest_interface.debug_requests(1)

        if isinstance(container_or_name, Item):
            container_or_name = container_or_name.name

        new_folder_response = self.rest_interface.create_folder(self.path(), container_or_name, exists)
        return create_items_from_json(self.rest_interface, new_folder_response, self.path(), self.in_trash)[0]


    def save(self, if_conflict=VersionConflictValue.fail, debug=False):
        """Save changes to folder metadata.
        See notes on individual setters for quirks.

        REST Documentation: https://www.bitcasa.com/cloudfs-api-docs/api/Alter%20Folder%20Meta.html

        :param if_conflict: Behavior if the local folder information is out of date.
        :param debug:       If true, will print the the request and response to stdout.

        :returns:   Updated folder object.
        :raises SessionNotLinked:       CloudFSRESTAdapter is not authenticated.
        :raises AuthenticatedError:     Based on CloudFS Error Code.
        """
        if debug:
            self.rest_interface.debug_requests(1)
        changes = {'version':self.data['version']}
        for changed_key in self.changed_meta:
            changes[changed_key] = self.data[changed_key]

        self.changed_meta.clear()

        response = self.rest_interface.folder_alter_meta(self.path(), changes, if_conflict)
        self._initialize_self(response, {})
        return self

    def delete(self, commit=False, force=False, debug=False):
        """Delete folder.
        Folder will only be removed from trash if commit is True. This is the case for folders in or out of the trash, so folders
        that are in the trash already will treat delete(commit=False) calls as a no-op.

        REST Documentation: https://www.bitcasa.com/cloudfs-api-docs/api/Delete%20Folder.html

        :param commit:  If true, will permanently remove file instead of moving it to trash. Defaults to False.
        :param force:   If true, will delete folder even if it contains items. Defaults to False.
        :param debug:   If true, will print the the request and response to stdout.

        :returns:   Dictionary with keys for success and the deleted folders last version.
        :raises SessionNotLinked:       CloudFSRESTAdapter is not authenticated.
        :raises AuthenticatedError:     Based on CloudFS Error Code.
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
            result =  self.rest_interface.delete_folder(self.path(), commit, force)
            if result['success'] and commit == False:
                self.in_trash = True
            return result

    def __str__(self):
        trash = 'trash' if self.in_trash else ''
        return "Folder[{}{}]:{}".format(trash, str(self.path()), self.name.encode('utf-8'))