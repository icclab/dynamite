__author__ = 'bloe'

from multiprocessing import Process, Queue
from dynamite.ENGINE.ScalingActionSender import ScalingActionSender
from dynamite.EXECUTOR.DynamiteScalingRequest import DynamiteScalingRequest

class TestProc(Process):
    def __init__(self, sender):
        super(TestProc, self).__init__()
        self._sender = sender

    def run(self):
        for number in range(100):
            action = DynamiteScalingRequest()
            action.command = "Command number {}".format(number)
            self._sender.send_action(action)


if __name__ == '__main__':
    q = Queue()
    sender = ScalingActionSender(q)
    proc = TestProc(sender)
    proc.start()

    while True:
        print(q.get())

    proc.join()