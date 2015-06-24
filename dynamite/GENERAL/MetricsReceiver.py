__author__ = 'bloe'

class MetricsReceiver(object):
    def __init__(self, communication_queue):
        self._communication_queue = communication_queue

    def receive_metrics(self):
        metrics_message = self._communication_queue.get()
        return metrics_message

    def __str__(self):
        return "MetricsReceiver(queue={})".format(self._communication_queue)
