import json
import requests
from typing import Dict
from dstool.class_utils import singleton
import random
import os
from datetime import datetime

@singleton
class PlanetML():
    def __init__(self, endpoint="http://localhost:5005") -> None:
        self.endpoint = endpoint
        self.last_job_update = {}

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
        self.last_job_update[job_id] = datetime.utcnow()
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
    
    def update_model_status(self, model, payload):
        warmed_runtime = {
            'stable_diffusion': 30,
            'gpt-j-6b': 30,
            't5-11b': 60,
            't0pp': 60,
            'ul2': 240,
            'gpt-neox-20b': 60
        }
        cold_runtime = {
            'stable_diffusion': 120,
            'gpt-j-6b': 120,
            't5-11b': 240,
            't0pp': 240,
            'ul2': 480,
            'gpt-neox-20b': 240
        }
        res = requests.patch(self.endpoint+f"/model_statuses/{model}", json={
            "name": model,
            "warmness": payload['warmness'],
            "expected_runtime": warmed_runtime[model] if payload['warmness'] == 1 else cold_runtime[model],
            "last_heartbeat": str(payload['last_heartbeat']),
        })
    
    def check_job_timeout(self):
        current_utc_time = datetime.utcnow()
        failed_jobs = []
        for job_id in self.last_job_update:
            if (current_utc_time - self.last_job_update[job_id]).total_seconds() > 300:
                self.update_job_status(job_id, status="failed")
                failed_jobs.append(job_id)
        return failed_jobs