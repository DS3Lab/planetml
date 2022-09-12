#!/bin/bash
# short.sh: a short discovery job
echo "Working hard..."
nvidia-smi
lscpu

module load cuda-toolkit/11.0
module load stashcp
# stashcp /public/biyuan/xxx ./

ls -l

mkdir python
tar -xzf decentralizedfm.tar.gz -C python
tar -xzf stable-diffusion-v1-4.tar.gz

ls -l

export PATH=$PWD/python/bin:$PATH
# export PYTHONPATH=$PWD/packages
export HOME=$PWD

which python
which python3

python3 -u /home/binhang.yuan/fm/new/GPT-home-private/local_latency_inference_stable_diffussion_osg.py

rm -rf python
rm -rf stable-diffusion-v1-4

echo "Science complete!"
