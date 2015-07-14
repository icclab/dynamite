__author__ = 'bloe'

import logging

from dynamite.EXECUTOR.DynamiteScalingRequest import DynamiteScalingRequest
from queue import Empty

class ScalingRequestReceiver:

    _process_queue = None

    def __init__(self, process_queue):
        self._process_queue = process_queue

    def connect(self):
        pass

    def receive(self):
        try:
            received_scaling_request_string = self._process_queue.get(block=False)

            scaling_request = DynamiteScalingRequest.from_json_string(
                received_scaling_request_string,
                message_processed_callback=lambda: None
            )
            self._logger.debug("Received scaling request:{:s}".format(received_scaling_request_string))
            return scaling_request
        except Empty:
            self._logger.debug("No request received.")
            return None

    def close(self):
        self._logger.debug("Closing connection to queue")
        self._process_queue.close()

    def _get_logger(self):
        return logging.getLogger(__name__)

    _logger = property(_get_logger)