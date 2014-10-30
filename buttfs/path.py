import copy


class Path(object):
    @staticmethod
    def path_from_string(path_string):
        """Create a path from a string. Separator character is a '/'
        Intended for use when parsing string representations stored somewhere.
        :param path_string: String to create path with.
        :return: Path object
        """

        paths = path_string.strip('/').split('/')
        if path_string[0] == '/':
            paths.insert(0, '/')
        return Path.path_from_string_list(paths)

    @staticmethod
    def path_from_string_list(string_list):
        """Create path from a list of strings.
        Mostly used by path_from_string
        :param string_list: Strings to create path with.
        :return: Path object
        """
        return Path(string_list)

    @staticmethod
    def path_from_item_list(items, add_root=False):
        """Create a path from a list of items.
        Makes no checks about if the resulting path is valid. Use at your own risk. :)
        :param items: List of items to make into a path.
        :return:
        """
        paths = [item.id for item in items]
        paths.insert(0, '/')
        return Path.path_from_string_list(paths)

    def __init__(self, paths):
        self.paths = filter(len, paths)

    def __getitem__(self, item):
        if type(item) is slice:
            # return fully functional path when it's a slice
            return Path.path_from_string_list(self.paths[item])
        else:
            # just return a string in this case
            return self.paths[item]

    def __str__(self):
        if self.paths[0] == '/':
            return '/' + '/'.join(self.paths[1:])
        else:
            return '/'.join(self.paths)

    def __repr__(self):
        return self.__str__()

    def __len__(self):
        return len(self.paths)

    def copy(self):
        """
        :return: A copy of the path.
        """
        return copy.deepcopy(self)

    def append(self, new_path):
        """
        :param new_path: Item or string id of item.
        :return: None
        """
        id = new_path
        if hasattr(new_path, 'id'):
            id = new_path.id
        self.paths.append(id)
