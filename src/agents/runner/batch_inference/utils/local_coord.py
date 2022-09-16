import requests

coordinator_host = "https://coordinator.shift.ml/eth"

def update_status(job_id, new_status, returned_payload=None):
    return requests.post(coordinator_host+f"/update_status/{job_id}", json={
        "status": new_status,
        "returned_payload": returned_payload
    })

if __name__=="__main__":
    res = update_status("d3170e85-ef77-4eb6-aed9-15eb9db933a8", "running", {"test_payload":"test"})
    print(res)