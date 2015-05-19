__author__ = 'brnr'


class IllegalArgumentError(ValueError):
    pass


class ServiceFileNotFoundError(Exception):
    pass


class DuplicateServiceFileError(Exception):
    pass


class ServiceAnnouncerFileNotFoundError(Exception):
    pass


class OverlappingPortRangeError(Exception):
    pass


class ServiceDependencyNotExistError(Exception):
    pass