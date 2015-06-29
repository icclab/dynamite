__author__ = 'bloe'

from threading import Thread

# This class simulates a process by executing the run method in a seperate thread
# Sometimes starting processes in tests is not possible due to pickling errors (e.g because mocks are not pickable)

class ProcessSimulator(Thread):
    def __init__(self, process):
        Thread.__init__(self)
        self._process = process

    def run(self):
        self._process.run()

    def stop(self):
        self._process.stop()
