__author__ = 'bloe'

class ConfigurationHelper:

    def __init__(self):
        pass

    @staticmethod
    def dict_value_or_default(dictionary, key, default_value):
        if key in dictionary:
            return dictionary[key]
        return default_value

    @staticmethod
    def dict_value_or_fail(dictionary, key, error_message):
        if key in dictionary:
            return dictionary[key]
        raise ValueError(error_message)

    @staticmethod
    def dict_value_or_return_value(dictionary, key, function):
        if key in dictionary:
            return dictionary[key]
        return function()
