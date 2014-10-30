from private.filesystem_common import *
from errors import method_not_implemented
from private.buttfs_paths import ExistValues, RestoreValue
from container import Folder

from item import Item

class Filesystem(object):

    exists = ExistValues()

    def __init__(self, rest_interface):
            self.rest_interface = rest_interface

    def list(self, item, debug=False):
        """List contents of item if the item is a folder.

        :param item:    Folder to list the contents of.
        :param debug:   If true, will print the the request and response to stdout.

        :returns:   Dictionary representation of JSON response.
        :raises SessionNotLinked:       ButtFSRESTAdapter is not authenticated.
        :raises AuthenticatedError:     Based on ButtFS Error Code.
        """
        path = item
        in_trash = False
        if isinstance(item, Item):
            path = item.url()
            in_trash = item.in_trash
        if debug:
            self.rest_interface.debug_requests(1)
        return list_items_from_path(self.rest_interface, path, in_trash)

    def root_container(self):
        """
        :return: A Folder representing the root of this users filesystem.
        """
        return Folder.root_folder(self.rest_interface.get_copy())

    def list_trash(self, debug=False):
        """List the items in the trash.

        :param debug:   If true, will print the the request and response to stdout.
        :return:
        """
        if debug:
            self.rest_interface.debug_requests(1)
        result = self.rest_interface.list_trash(self.root_container().path())
        return create_items_from_json(self.rest_interface, result, None, True)

    def move(self, items, destination, exists=ExistValues.reuse, debug=False):
        """Move list of items to destination.

        :param items:       List of items to move.
        :param destination: Path or Folder to move the items to.
        :param exists:      How to handle if an item of the same name exists in the destination folder. Defaults to rename.
        :param debug:       If true, will print the the request and response to stdout.

        :returns:   Details of the new item(s) in a dictionary.
        :raises SessionNotLinked:       ButtFSRESTAdapter is not authenticated.
        :raises AuthenticatedError:     Based on ButtFS Error Code.
        """
        if debug:
            self.rest_interface.debug_requests(1)
        return move_items(self.rest_interface, items, destination, exists)

    def copy(self, items, destination, exists=ExistValues.reuse, debug=False):
        """Copy items to destination.

        :param items:       List of items to copy.
        :param destination: Path or Folder to copy the items to.
        :param exists:      How to handle if an item of the same name exists in the destination folder. Defaults to rename.
        :param debug:       If true, will print the the request and response to stdout.

        :returns:   Details of the new item(s) in a dictionary.
        :raises SessionNotLinked:       ButtFSRESTAdapter is not authenticated.
        :raises AuthenticatedError:     Based on ButtFS Error Code.
        """
        if debug:
            self.rest_interface.debug_requests(1)
        return copy_items(self.rest_interface, items, destination, exists)

    def restore(self, items, method=RestoreValue.fail, method_argument=None, debug=False):
        """Restore item(s) from trash.
        REST documentation: https://www.bitcasa.com/cloudfs-api-docs/api/Recover%20Trash%20Item.html

        :param items:           Items or paths to restore.
        :param restore_method:  Determines method used to restore item.
        :param method_argument: Expected contents determined by value of restore_method
        :param debug:       If true, will print the the request and response to stdout.
        :return:    Items at new location.
        """
        results = []
        for item in items:
            path = item
            if isinstance(item, Item):
                path = item.path()
            results.append(self.rest_interface.restore_trash_item(path, method, method_argument))

        return results

    def file_history(self, item, debug=False):
        """NOT IMPLEMENTED: Get previous versions of item.
        REST documentation: https://www.bitcasa.com/cloudfs-api-docs/api/List%20History.html

        :param item:    Item to find previous versions.
        :param debug:   If true, will print the the request and response to stdout.
        :return:    List of previous versions of the item.
        """
        raise method_not_implemented(self, 'file_history')
