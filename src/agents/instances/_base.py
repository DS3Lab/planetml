from utils.planetml import PlanetML

class LocalCoordinator(object):
    def __init__(self, name) -> None:
        self.name = name
        self.rest_client = PlanetML()

    def watch(self, interval=60):
        raise NotImplementedError

    def dispatch(self):
        raise NotImplementedError

    def check_status(self):
        raise NotImplementedError
    
    def fetch_jobs(self):
        return self.rest_client.get_jobs()