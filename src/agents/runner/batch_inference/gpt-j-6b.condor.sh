#!/bin/bash
# short.sh: a short discovery job
echo "Working hard..."

job_id=$1

nvidia-smi
lscpu

module load cuda-toolkit/11.0
module load stashcache

mkdir python
tar -xzf python.tar.gz -C python
tar -xzf gpt-j-6b-new.tar.gz
mv gpt-j-6b-new GPT-home-private/

ls -l

export PATH=$PWD/python/bin:$PATH
# export PYTHONPATH=$PWD/packages
export HOME=$PWD

which python
which python3

cd GPT-home-private

export NCCL_DEBUG=INFO
export NCCL_IB_DISABLE=1
export NCCL_P2P_DISABLE=1

world_size=2
machine_size=1
n_gpu_per_machine=$((world_size/machine_size))

i=0
while :
do
  if [ "$i" -ge "$n_gpu_per_machine" ]; then
      break
  fi
  
  DIST_CONF="--pp-mode pipe_sync_sample_mask_token_pipe --pipeline-group-size $world_size --cuda-id $i"
  MODEL_CONF="--model-type gptj --model-name gpt-j-6b-new --num-iters 9999999999999"
  INFERENCE_CONF="--fp16  --budget 2000 --batch-size 24 --input-seq-length 512 --generate-seq-length 32 --micro-batch-size 1 --num-layers 14 --max-layers 28"
  COOR_CONF="--coordinator-server-ip 10.6.7.244 --working-directory ./ --profiling no-profiling --net-interface $netif --job_id $job_id"

  python -u dist_batch_inference_w_httpclient.py $DIST_CONF $MODEL_CONF $INFERENCE_CONF $COOR_CONF &

  ((port++))
  ((i++))

done

wait

cd ..
rm -rf python

echo "Task complete!"
