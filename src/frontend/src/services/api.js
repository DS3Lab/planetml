import axios from 'axios';

const tomaapi_endpoint = 'https://planetd.shift.ml'
// const tomaapi_endpoint = 'http://192.168.191.9:5005'

function get_site_status() {
    return axios.get(tomaapi_endpoint + '/sites')
}

function get_jobs_list() {
    return axios.get(tomaapi_endpoint + '/jobs')
}

function get_status_history() {
    return axios.get(tomaapi_endpoint + '/site_stats')
}

function get_job_status(job_id) {
    return axios.get(tomaapi_endpoint + '/job/' + job_id)
}

function upload_file_to_planetd(file) {
    const formData = new FormData();
    formData.append('file', file);
    console.log(formData);
    const headers = { 'Content-Type': 'multipart/form-data' };
    return axios.post(tomaapi_endpoint + '/file', formData, { headers })
}

function add_new_job(job_payload) {
    let request_json = {
        "type": "general",
        "payload": job_payload,
        "returned_payload": {},
        "status": "submitted",
        "source": "dalle",
        "processed_by": ""
    }
    const headers = {
        'Content-Type': 'application/json',
    }
    return axios.post(tomaapi_endpoint + '/jobs', request_json, {
        headers: headers
    })
}

function get_model_status() {
    return axios.get(tomaapi_endpoint + '/model_statuses')
}


function domain_to_name(domain) {
    if (domain === 'ethz.ch') {
        return 'ETH Zürich'
    } else if (domain === 'nlp.stanford.edu') {
        return 'Stanford University'
    } else if (domain === 'osg-htc.org') {
        return 'Open Science Grid'
    } else if (domain === 'chtc.wisc.edu') {
        return 'University of Wisconsin'
    }
}

const available_models = {
    "gpt-j-6b": {
        "best_of": 1,
        "logprobs": 1,
        "max_tokens": 32,
        "n": 1,
        "temperature": 0,
        "top_p": 1,
        "stop":".;"
    },
    "gpt-neox-20b": {
        "best_of": 1,
        "logprobs": 1,
        "max_tokens": 32,
        "n": 1,
        "temperature": 0,
        "top_p": 1,
        "stop":".;"
    },
    "stable_diffusion": {
        "num_returns": 1
    },
    "t5-11b": {
        "best_of": 1,
        "logprobs": 1,
        "max_tokens": 32,
        "n": 1,
        "temperature": 0,
        "top_p": 1,
        "stop":".;"
    },
    "t0pp": {
        "best_of": 1,
        "logprobs": 1,
        "max_tokens": 32,
        "n": 1,
        "temperature": 0,
        "top_p": 1,
        "stop":".;"
    },
    "ul2": {
        "best_of": 1,
        "logprobs": 1,
        "max_tokens": 32,
        "n": 1,
        "temperature": 0,
        "top_p": 1,
        "stop":".;"
    }
}

export {
    get_site_status,
    get_jobs_list,
    get_status_history,
    domain_to_name,
    add_new_job,
    get_job_status,
    upload_file_to_planetd,
    get_model_status,
    available_models,
}