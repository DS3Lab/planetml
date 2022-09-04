import os
import json
from filelock import SoftFileLock
from loguru import logger

class LocalCoordinatorClient:
    def __init__(self, working_directory: str, model_name: str) -> None:
        self.working_directory = working_directory
        self.model_name = model_name
        self.dir_path = os.path.join(self.working_directory, self.model_name)
        lock_path = os.path.join(self.dir_path, self.model_name+'.lock')
        self.model_lock = SoftFileLock(lock_path, timeout=10)

    def notify_inference_heartbeat(self):
        pass
    
    def notify_inference_join(self):
        pass

    def load_input_job_from_dfs(self):
        for filename in os.listdir(self.dir_path):
            # print(filename)
            if filename.startswith('input_'):
                doc_path = os.path.join(self.dir_path, filename)
                with self.model_lock:
                    with open(doc_path, 'r') as infile:
                        doc = json.load(infile)
                    # assert model_name == doc['task_api']['model_name']
                print(f"++++++++++++++load_input_job_from_dfs <{doc['_id']}>++++++++++++")
                return doc
        return None

    def save_output_job_to_dfs(self, result_doc):
        # print("++++++++++++++save_output_job_to_dfs++++++++++++")
        output_filename = 'output_' + result_doc['_id'] + '.json'
        output_path = os.path.join(self.dir_path, output_filename)
        with self.model_lock:
            with open(output_path, 'w') as outfile:
                json.dump(result_doc, outfile)
        input_filename = 'input_' + result_doc['_id'] + '.json'
        input_path = os.path.join(self.dir_path, input_filename)
        assert os.path.exists(input_path)
        os.remove(input_path)