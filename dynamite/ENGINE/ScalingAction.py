__author__ = 'bloe'

from dynamite.EXECUTOR.DynamiteEXECUTOR import DynamiteScalingCommand

class ScalingAction(object):

    service_name = None
    service_instance_name = None
    uuid = None

    def __init__(self, service_name):
        self.service_name = service_name
        self._command = None

    def _get_command(self):
        return self._command

    def _set_command(self, command):
        if command not in [DynamiteScalingCommand.SCALE_DOWN, DynamiteScalingCommand.SCALE_UP]:
            raise ValueError("There is no command named {}!".format(command))
        self._command = command

    command = property(_get_command, _set_command)

    def __repr__(self):
        return "ScalingAction(service_name={},service_instance_name={},uuid={})".format(
            self.service_name,
            self.service_instance_name,
            self.uuid
        )
