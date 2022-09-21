import os
import time

def _restart():
    os.system("pkill -9 python")
    os.system("pkill -9 uvicorn")
    time.sleep(20)
    os.system("cd /root/fm/new/planetml && bash controller/start_agent.sh")
    time.sleep(20)
    
    os.system("cd /root/fm/new/planetml/src/agents/runner/batch_inference && bash opt-175b.local.sh 4cd531eb-5143-43d1-9ce8-eabef82dc8e2")

def check_time_diff():
    pass