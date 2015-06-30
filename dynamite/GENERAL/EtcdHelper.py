__author__ = 'bloe'

class EtcdHelper:

    def __init__(self):
        pass

    @staticmethod
    def build_etcd_path(path_parts):
        if len(path_parts) < 1:
            raise ValueError("To build an etcd path you have to define at least one part of the path!")
        if len(path_parts) == 1:
            return path_parts[0]
        else:
            path = path_parts[0]
            path_parts = path_parts[1:]
            for path_part in path_parts:
                if path_part is None or path_part == "":
                    continue
                if not path.endswith("/"):
                    path += "/"
                path += path_part

            if path.endswith("/"):
                path = path[0:-1]

            return path
