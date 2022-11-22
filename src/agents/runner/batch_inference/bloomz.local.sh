cd /root/fm/dev/GPT-home-private    # Change directory

job_id=$1

echo job_id $job_id

python3 dist_latency_alpa_inference_w_httpclient.py --job-id $job_id --model-name bloomz