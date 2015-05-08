__author__ = 'brnr'


class FLEET_STATE_STRUCT(object):
    INACTIVE = "inactive"
    LOADED = "loaded"
    LAUNCHED = "launched"


class FleetService(object):
    name = None
    details = None
    state = None

    def __init__(self, name, details_json, state=FLEET_STATE_STRUCT.INACTIVE):
        self.name = name
        self.details = details_json
        self.state = state

    def __str__(self):
        pass