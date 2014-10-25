import collections

from ..errors import invalid_argument

def list_items_from_path(rest_interface, path):
    response = rest_interface.list_folder(path)
    path = path if str(path) != '/' else None

    # only use actual response
    return create_items_from_json(rest_interface, response, path)

def move_items(rest_interface, items, destination, exists):
    from ..file import File
    from ..container import Folder
    from ..item import Item
    if isinstance(destination, Item):
        destination = destination.path()
    operations = {
        File:lambda file: rest_interface.move_file(file.path(), destination, file.name, exists),
        Folder:lambda file: rest_interface.move_folder(file.path(), destination, file.name, exists)
    }

    return _process_items_by_type(items, operations)

def copy_items(rest_interface, items, destination, exists):
    from ..file import File
    from ..container import Folder
    from ..item import Item
    if isinstance(destination, Item):
        destination = destination.path()

    operations = {
        File:lambda file: rest_interface.copy_file(file.path(), destination, file.name, exists),
        Folder:lambda file: rest_interface.copy_folder(file.path(), destination, file.name, exists)
    }

    return _process_items_by_type(items, operations)

def _process_items_by_type(items, operation_dictionary):
    if type(items) is not list and type(items) is not tuple:
        items = [items]
    for item in items:
        if type(item) in operation_dictionary:
            op = operation_dictionary[type(item)]
            op(item)
        else:
            raise invalid_argument(
                'item in list',
                '{}'.format([operation_dictionary.keys()]),
                str(type(item)))


def create_items_from_json(rest_interface, data, parent_path):
    from ..file import File
    from ..container import Folder
    if 'results' in data:
        data = data['results']

    if 'items' in data:
        data = data['items']

    items = []

    parent_item = None # root
    if parent_path and str(parent_path) != '/':

        if not parent_item:
            parent_item = parent_path

    def create_item(item_json, parent):
        new_item = None
        if item_json['type'] == 'folder':
            new_item = Folder(rest_interface.get_copy())._create_from_json(item_json, parent)
        if item_json['type'] == 'file':
            new_item = File(rest_interface.get_copy())._create_from_json(item_json, parent)

        items.append(new_item)


    # single item from upload / etc
    if isinstance(data, collections.Mapping):
        create_item(data, parent_item)
    else:
        # directory listing
        for item in data:
            create_item(item, parent_item)


    return items
