from private.filesystem_common import *
from errors import method_not_implemented
from private.cloudfs_paths import ExistValues
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
        :raises SessionNotLinked:       CloudFSRESTAdapter is not authenticated.
        :raises AuthenticatedError:     Based on CloudFS Error Code.
        """
        path = item
        if isinstance(item, Item):
            path = item.url()
        if debug:
            self.rest_interface.debug_requests(1)
        return list_items_from_path(self.rest_interface, path)

    def root_container(self):
        """
        :return: A Folder representing the root of this users filesystem.
        """
        return Folder(self.rest_interface.get_copy())

    def move(self, items, destination, exists=ExistValues.reuse, debug=False):
        """Move list of items to destination.

        :param items:       List of items to move.
        :param destination: Path or Folder to move the items to.
        :param exists:      How to handle if an item of the same name exists in the destination folder. Defaults to rename.
        :param debug:       If true, will print the the request and response to stdout.

        :returns:   Details of the new item(s) in a dictionary.
        :raises SessionNotLinked:       CloudFSRESTAdapter is not authenticated.
        :raises AuthenticatedError:     Based on CloudFS Error Code.
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
        :raises SessionNotLinked:       CloudFSRESTAdapter is not authenticated.
        :raises AuthenticatedError:     Based on CloudFS Error Code.
        """
        if debug:
            self.rest_interface.debug_requests(1)
        return copy_items(self.rest_interface, items, destination, exists)

    def restore(self, items, destination, exists, debug=False):
        """NOT IMPLEMENTED: Restore item(s) from trash.
        REST documentation: https://www.bitcasa.com/cloudfs-api-docs/api/Recover%20Trash%20Item.html

        :param items:       List of items to restore from trash.
        :param destination: Destionation to restore them to.
        :param exists:      How to handle if an item of the same name exists in the destination folder. Defaults to rename.
        :param debug:       If true, will print the the request and response to stdout.
        :return:    Items at new location.
        """
        raise method_not_implemented(self, 'restore')

    def file_history(self, item, debug=False):
        """NOT IMPLEMENTED: Get previous versions of item.
        REST documentation: https://www.bitcasa.com/cloudfs-api-docs/api/List%20History.html

        :param item:    Item to find previous versions.
        :param debug:   If true, will print the the request and response to stdout.
        :return:    List of previous versions of the item.
        """
        raise method_not_implemented(self, 'file_history')