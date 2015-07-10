__author__ = 'bloe'

import logging

from dynamite.EXECUTOR.DynamiteScalingResponse import DynamiteScalingResponse

class ExecutedTaskReceiver(object):

    _process_queue = None

    def __init__(self, process_queue):
        self._logger = logging.getLogger(__name__)
        self._process_queue = process_queue

    def receive(self):
        messages = ()

        if self._process_queue.empty():
            return messages

        received_scaling_response_string = self._process_queue.get()

        scaling_response = DynamiteScalingResponse.from_json_string(
            received_scaling_response_string,
            message_processed_callback=lambda: None
        )
        self._logger.info("Received scaling response %s", repr(scaling_response))
        messages = (scaling_response,)
        return messages + self.receive()

    def close(self):
        self._process_queue.close()
