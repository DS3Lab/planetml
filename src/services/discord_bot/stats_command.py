import requests
from dateutil import parser
from table2ascii import table2ascii
import time
from datetime import datetime
def get_cluster_status(args):
    x = requests.get('https://planetd.shift.ml/site_stats')

    records = {}
    for site in x.json():
        site_identifier = site["site_identifier"]
        avail_gpus = site["avail_gpus"]
        total_gpus = site["total_gpus"]
        avail_tflops = site["avail_tflops"]
        total_tflops = site["total_tflops"]
        created_at = parser.parse(site["created_at"])

        if site_identifier not in records:
            records[site_identifier] = (
                created_at, avail_gpus, total_gpus, avail_tflops, total_tflops)
        else:
            if created_at >= records[site_identifier][0]:
                records[site_identifier] = (
                    created_at, avail_gpus, total_gpus, avail_tflops, total_tflops)

    header = ("SITE", "Total GPUs/TFLOPS", "Avail GPUs/TFLOPS")
    body = []
    sum_total_gpus = 0
    sum_total_tflops = 0
    sum_avail_gpus = 0
    sum_avail_tflops = 0
    min_time = None
    max_time = None
    for site_identifier in records:
        (created_at, avail_gpus, total_gpus, avail_tflops,
            total_tflops) = records[site_identifier]
        body.append(
            (site_identifier, f"{int(total_gpus)}/{int(total_tflops)}", f"{int(avail_gpus)}/{int(avail_tflops)}"))
        sum_total_gpus = sum_total_gpus + total_gpus
        sum_total_tflops = sum_total_tflops + total_tflops
        sum_avail_gpus = sum_avail_gpus + avail_gpus
        sum_avail_tflops = sum_avail_tflops + avail_tflops

        if min_time is None:
            min_time = created_at
            max_time = created_at

        min_time = min(min_time, created_at)
        max_time = max(max_time, created_at)

    footer = ("SUM", f"{int(sum_total_gpus)}/{int(sum_total_tflops)}",
                f"{int(sum_avail_gpus)}/{int(sum_avail_tflops)}")

    responds = table2ascii(
        header=header,
        body=body,
        footer=footer,
    )

    responds = f"```Research Computer\n{responds}\n\nmin_time={min_time.utcnow()} UTC\nmax_time={max_time.utcnow()} UTC\n\n{args}```"
    return responds

def get_model_status(args):
    x = requests.get('http://192.168.191.9:5005/model_statuses')

    header = ("Model Name", "Warmness", "Exp. Response Time (s)", "Last Heartbeat")
    body = []
    for model in x.json():
        if model['warmness'] == 1:
            warmness = 'VRAM'
        elif model['warmness'] == 0:
            warmness = 'Disk'
        elif model['warmness'] == 0.5:
            warmness = 'Booting'
        heartbeat_time = parser.parse(model['last_heartbeat']).strftime("%Y-%m-%d %H:%M:%S")
        comparator = "<" if model['warmness'] == 1 else ">"

        body.append(
            (model['name'], warmness, f"{comparator} {model['expected_runtime']}", str(heartbeat_time))
        )

    footer = ("","","For the first query","")

    responds = table2ascii(
        header=header,
        body=body,
        footer=footer,
    )
    current_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    responds = f"```Research Computer\nCurrent UTC: {current_time}\n{responds}\n\n{args}```"
    return responds