import axios from 'axios';

const tomaapi_endpoint = 'https://planetd.shift.ml'
// const tomaapi_endpoint = 'http://localhost:5000/'

function get_site_status() {
    return axios.get(tomaapi_endpoint + '/sites')
}

function get_jobs_list() {
    return axios.get(tomaapi_endpoint + '/jobs')
}

function get_status_history() {
    return axios.get(tomaapi_endpoint + '/site_stats')
}

function add_new_job(job_payload) {
    return axios.post(tomaapi_endpoint + '/jobs', {
        "type": "general",
        "payload": job_payload,
        "returned_payload": {},
        "status": "submitted",
        "source": "dalle",
        "processed_by": ""
        }
    )
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

export {
    get_site_status,
    get_jobs_list,
    get_status_history,
    domain_to_name,
    add_new_job
}