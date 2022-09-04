from utils.planetml import PlanetML

class LocalCoordinator(object):
    def __init__(self, name) -> None:
        self.name = name
        self.rest_client = PlanetML()

    def dispatch(self, job):
        raise NotImplementedError

    def check_status(self):
        raise NotImplementedError