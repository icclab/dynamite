__author__ = 'bloe'

from unittest.mock import Mock

class FakeEtcdClient:

    _content = {}

    def __init__(self, content_as_dict):
        self._content = content_as_dict

    def _get_dict_from_path(self, path):
        path_parts = path.split("/")
        dict_or_attribute = self._content
        for path_part in path_parts:
            if path_part == "":
                continue
            dict_or_attribute = dict_or_attribute[path_part]
        return dict_or_attribute

    def get(self, path, recursive=False, sorted=False):
        dict_or_attribute = self._get_dict_from_path(path)

        result = Mock()
        result.children = []
        if isinstance(dict_or_attribute, dict):
            self._get_recursive_structure(dict_or_attribute, path, result)
        else:
            result.value = dict_or_attribute

        return result

    def _get_recursive_structure(self, structure, path, parent):
        if not isinstance(structure, dict) or len(structure) == 0:
            parent.value = structure
            return
        for key, subdict in structure.items():
                child = Mock()
                child.value = None
                child.key = path + "/" + key
                parent.children.append(child)
                self._get_recursive_structure(subdict, child.key, child)

    def read(self, key, recursive=False, sorted=False):
        return self.get(key, recursive=recursive, sorted=sorted)

    def delete(self, path):
        pass


