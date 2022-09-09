import json
import requests
from typing import Dict
from dstool.class_utils import singleton
import random
import os

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
        if processed_by!='':
            data['processed_by'] = processed_by
        if status !='':
            data['status'] = status
        if source !='':
            data['source'] = source
        if type != '':
            data["type"] = type
        if returned_payload:
            data['returned_payload'] = returned_payload
        else:
            data['returned_payload'] = {}
        res = requests.patch(self.endpoint+f"/jobs/{job_id}", json=data)
        return res.json()

    def write_json_to_s3(self, data):
        tmp_file_id = random.randint(0, 100000000)
        with open(f"{tmp_file_id}.json", "w+") as fp:
            json.dump(data, fp)
        with open(f'{tmp_file_id}.json', 'rb') as fp:
            files = {'file': fp}
            # upload to endpoint
            res = requests.post(f'{self.endpoint}/file', files=files)
            # Closing automatically deletes the tempfile
        # delete the file
        os.remove(f"{tmp_file_id}.json")
        return res.json()