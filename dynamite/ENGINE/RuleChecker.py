__author__ = 'bloe'

from dynamite.ENGINE.ScalingAction import ScalingAction

class RuleChecker(object):
    def __init__(self):
        pass

    def check(self, scaling_metrics):
        # TODO: implement check if scaling action has to be performed
        return [ScalingAction()]
