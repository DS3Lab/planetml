import requests
from dstool.class_utils import singleton


@singleton
class PlanetML():
    def __init__(self, endpoint="https://planetd.shift.ml") -> None:
        self.endpoint = endpoint

    def get_jobs(self):
        return requests.get(self.endpoint+"/jobs").json()

    def update_job_status(self,
                          job_id: str,
                          processed_by: str,
                          status: str,
                          source: str,
                          type: str
                          ):
        data = {
            "id": job_id,
            "processed_by": processed_by,
            "status": status,
            "type": type,
            "source": source,
        }
        res = requests.patch(self.endpoint+f"/jobs/{job_id}", json=data)
        return res