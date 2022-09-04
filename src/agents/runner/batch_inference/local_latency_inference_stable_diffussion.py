import time
import base64
import argparse
from io import BytesIO
from datetime import datetime
import os
import torch
from torch import autocast
from loguru import logger
from diffusers import StableDiffusionPipeline, LMSDiscreteScheduler

from utils.dist_args_utils import *
from utils.coordinator_client import LocalCoordinatorClient
from utils.s3 import upload_file
from utils.local_coord import update_status

def main():
    
    parser = argparse.ArgumentParser(description='Inference Runner with coordinator.')
    parser.add_argument('--job_id', type=str, default='test', metavar='S',help='Job ID')
    
    add_global_coordinator_arguments(parser)
    add_lsf_coordinator_arguments(parser)
    args = parser.parse_args()
    print_arguments(args)
    update_status(args.job_id, "running")

    lsf_coordinator_client = LocalCoordinatorClient(
        "/nfs/iiscratch-zhang.inf.ethz.ch/export/zhang/export/fm/new/working_dir/",
        'stable_diffusion'
    )
    output_dir = os.path.join(
        "/nfs/iiscratch-zhang.inf.ethz.ch/export/zhang/export/fm/new/working_dir/", 
        'stable_diffusion'
    )
    # lsf_coordinator_client.notify_inference_join()
    logger.info("Loading Stable Diffusion model...")
    lms = LMSDiscreteScheduler(
        beta_start=0.00085,
        beta_end=0.012,
        beta_schedule="scaled_linear"
    )

    pipe = StableDiffusionPipeline.from_pretrained(
        "CompVis/stable-diffusion-v1-4",
        scheduler=lms,
        use_auth_token=True,
        torch_dtype=torch.float16,
        revision="fp16"
    ).to("cuda:0")

    logger.info("Stable Diffusion model loaded.")

    return_msg = lsf_coordinator_client.load_input_job_from_dfs(args.job_id)
    if return_msg is not None:
        logger.info(f"Received a new job. {return_msg}")

        job_request = return_msg

        num_return_sequences = job_request['num_returns']
        text = [job_request['input']]
        results = job_request.copy()
        with torch.no_grad():
            with autocast("cuda"):
                img_results = []
                for i in range(num_return_sequences):
                    image = pipe(text)["sample"][0]
                    image.save(os.path.join(output_dir, "test.png"))
                    succ, img_id = upload_file(os.path.join(output_dir, "test.png"))
                    if succ:
                        img_results.append("https://planetd.shift.ml/files/"+img_id)
                    else:
                        logger.error("Upload image failed")
                results["output"] = img_results
                lsf_coordinator_client.save_output_job_to_dfs(results)
                update_status(
                    args.job_id,
                    "finished",
                    returned_payload=results
                )
if __name__ == '__main__':
    main()