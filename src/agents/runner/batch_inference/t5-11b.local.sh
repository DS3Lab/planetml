# conda activate fm_worker
cd /root/fm/dev/GPT-home-private

job_id=$1
echo "start with $job_id"

CONF="--model-name t5-11b --working-directory /root/fm/working_dir --cuda-id 2 --job_id $job_id"

python -u local_latency_inference_nlp_w_httpclient.py $CONF