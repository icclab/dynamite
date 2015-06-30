__author__ = 'bloe'

class WriteEvent:

    time = None
    resource = None

    def __init__(self):
        self.time = None
        self._value = None
        self.resource = None

    def get_formatted_time(self):
        iso_format_string = self.time.isoformat()
        return iso_format_string[0:23] + "Z"

    def _get_value(self):
        return self._value

    def _set_value(self, numeric_value):
        if self.resource.metric_value_template is None:
            self._value = numeric_value
        else:
            template = self.resource.metric_value_template
            templated_value = template.replace("%value%", str(numeric_value))
            self._value = templated_value

    value = property(_get_value, _set_value)
