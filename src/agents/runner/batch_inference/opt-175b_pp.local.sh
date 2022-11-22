cd /root/fm/new/GPT-home-private    # Change directory

netif='eth0'
echo setting network interface to $netif

job_id=$1

echo job_id $job_id

export NCCL_SOCKET_IFNAME=$netif
export GLOO_SOCKET_IFNAME=$netif

export NCCL_DEBUG=INFO
export NCCL_IB_DISABLE=1
export NCCL_P2P_DISABLE=1

world_size=8
machine_size=1
n_gpu_per_machine=$((world_size/machine_size))

i=0
while :
do
  if [ "$i" -ge "$n_gpu_per_machine" ]; then
      break
  fi

  DIST_CONF="--pp-mode pipe_sync_sample_mask_token_pipe --pipeline-group-size $world_size --cuda-id $i"
  MODEL_CONF="--model-type opt --model-name /root/fm/new/models/opt-175b-new --num-iters 9999999999999"
  INFERENCE_CONF="--fp16 --budget 20400 --batch-size 1 --input-seq-length 1024 --generate-seq-length 256 --micro-batch-size 1 --num-layers 12 --max-layers 96"
  COOR_CONF="--coordinator-server-ip 10.6.7.244 --working-directory /root/fm/new/working_dir --profiling no-profiling --net-interface $netif --job_id $job_id"

  python3 -u dist_batch_and_latency_inference_w_httpclient.py $DIST_CONF $MODEL_CONF $INFERENCE_CONF $COOR_CONF > /root/fm/new/exe_log/nohup.log.$i 2>&1 &

  ((port++))
  ((i++))

done

wait

