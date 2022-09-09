from typing import Dict
import requests
from dstool.class_utils import singleton
from tempfile import TemporaryFile
import json
@singleton
class PlanetML():
    def __init__(self, endpoint="http://localhost:5005") -> None:
        self.endpoint = endpoint

    def get_jobs(self):
        return requests.get(self.endpoint+"/jobs/submitted").json()

    def update_job_status(self,
                          job_id: str,
                          processed_by: str="",
                          status: str="",
                          source: str="",
                          type: str="",
                          returned_payload: Dict=None):
        data = {
            "id": job_id,
            "status": status,
            "type": type,
            "source": source,
        }
        if processed_by:
            data['processed_by'] = processed_by
        if status:
            data['status'] = status
        if source:
            data['source'] = source
        if type:
            data["type"] = type
        if returned_payload:
            data['returned_payload'] = returned_payload
        else:
            data['returned_payload'] = {}
        res = requests.patch(self.endpoint+f"/jobs/{job_id}", json=data)
        return res
    
    def write_json_to_s3(self, data):
        fp = TemporaryFile()
        json.dumps(data, fp)
        # upload to endpoint
        res = requests.post(f'{self.endpoint}/file', data=fp)
        # Closing automatically deletes the tempfile
        fp.close()
        return res.json()