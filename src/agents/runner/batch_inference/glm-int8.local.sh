cd /root/fm/dev/GPT-home-private    # Change directory

job_id=$1

echo job_id $job_id


MODEL_TYPE="glm-130b"
CHECKPOINT_PATH="/root/fm/models/glm-130b-sat-int8-tp4"
MP_SIZE=4
SEED=1234
MAX_OUTPUT_LENGTH=128
MIN_GEN_LENGTH=0
# BaseStrategy args
TEMP=0.9
TOPK=1
TOPP=0

export CUDA_VISIBLE_DEVICES=4,5,6,7

MODEL_ARGS="--model-parallel-size ${MP_SIZE} \
            --num-layers 70 \
            --hidden-size 12288 \
            --inner-hidden-size 32768 \
            --vocab-size 150528 \
            --num-attention-heads 96 \
            --max-sequence-length 256 \
            --tokenizer-type icetk-glm-130B \
            --layernorm-order post \
            --load ${CHECKPOINT_PATH} \
            --skip-init \
            --fp16 \
            --from-quantized-checkpoint \
            --seed $SEED \
            --mode inference \
            --sampling-strategy BeamSearchStrategy \
            --quantization-bit-width 8 \
            --out-seq-length $MAX_OUTPUT_LENGTH \
            --min-gen-length $MIN_GEN_LENGTH \
            --temperature $TEMP \
            --top_k $TOPK \
            --top_p $TOPP"


torchrun --rdzv_endpoint=127.0.0.1:29401 --nproc_per_node $MP_SIZE dist_latency_glm_inference_w_httpclient.py $MODEL_ARGS