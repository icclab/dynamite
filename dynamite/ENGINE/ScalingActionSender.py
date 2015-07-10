__author__ = 'bloe'

import logging

class ScalingActionSender(object):

    _process_queue = None

    def __init__(self, process_queue):
        self._logger = logging.getLogger(__name__)
        self._process_queue = process_queue

    def send_action(self, scaling_request):
        self._logger.info("Sending scaling request %s to inter-process queue", repr(scaling_request))
        scaling_request_string = scaling_request.to_json_string()
        self._process_queue.put(scaling_request_string)

    def close(self):
        self._process_queue.close()

