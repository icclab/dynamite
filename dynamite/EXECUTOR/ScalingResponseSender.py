__author__ = 'bloe'

import logging

class ScalingResponseSender:

    _process_queue = None

    def __init__(self, process_queue):
        self._process_queue = process_queue

    def connect(self):
        pass

    def send_response(self, scaling_response):
        self._logger.info("Sending scaling response %s to queue", repr(scaling_response))
        scaling_response_string = scaling_response.to_json_string()
        self._process_queue.put(scaling_response_string)

    def close(self):
        self._logger.debug("Closing connection to queue")
        self._process_queue.close()

    def _get_logger(self):
        return logging.getLogger(__name__)

    _logger = property(_get_logger)
