#!/bin/bash
# short.sh: a short discovery job
echo "Relax ..."
nvidia-smi
lscpu

module load cuda-toolkit/11.0
module load stashcache
# stashcp /public/biyuan/xxx ./

ls -l

# cp /staging/byuan43/python.tar.gz ./
# cp /staging/byuan43/stable-diffusion-v1-4.tar.gz ./


mkdir python
tar -xzf python.tar.gz -C python
tar -xzf stable-diffusion-v1-4.tar.gz
mv stable-diffusion-v1-4 GPT-home-private/

ls -l

export PATH=$PWD/python/bin:$PATH
# export PYTHONPATH=$PWD/packages
export HOME=$PWD

which python
which python3

cd GPT-home-private
python3 -u local_latency_inference_stable_diffussion_osg.py

rm -rf stable-diffusion-v1-4
cd ..

rm -rf python

echo "Task complete!"
