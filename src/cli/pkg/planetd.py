import requests
from dstool.class_utils import singleton

@singleton
class PlanetML():
    def __init__(self) -> None:
        self.endpoint = 'https://planetd.shift.ml'
    
    def get_site_status(self):
        r = requests.get(self.endpoint+"/sites")
        return r.json()
    
    def prettify_site_status(self):
        sites = self.get_site_status()
        status = [{
            "site_name": site['name'],
            "GPUs": f"{site['avail_gpus']}/{site['total_gpus']}",
        } for site in sites]
        return status