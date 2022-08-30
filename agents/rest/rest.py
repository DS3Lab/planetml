import requests
endpoint = "http://127.0.0.1:5000"

def update_job_status(job_id, 
            processed_by: str,
            status: str, 
            type: str = 'general',
            source: str = 'dataperf'
        ):
    """
    Update a job status
    """
    url = f"{endpoint}/jobs/{job_id}"
    data = {
        "id": job_id,
        "processed_by": processed_by,
        "status": status,
        "type": type,
        "source": source,
    }
    res = requests.patch(url, json=data)
    return res
