import requests

res = requests.post('https://planetd.shift.ml/site_stats', json={
  "site_identifier": 'ethz.ch',
  "scheduler_type": 'slurm',
  "total_tflops": 1000.0,
  "avail_tflops": 1000.0,
  "total_gpus": 20,
  "avail_gpus": 20,
  "resources": 20,
  "note": "string"
})