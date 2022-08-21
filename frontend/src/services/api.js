import axios from 'axios';

const tomaapi_endpoint = 'https://planetd.shift.ml/'
// const tomaapi_endpoint = 'http://localhost:5000/'

function get_site_status() {
    return axios.get(tomaapi_endpoint + 'sites')
}

function get_jobs_list() {
    return axios.get(tomaapi_endpoint + 'jobs')
}

export {
    get_site_status,
    get_jobs_list
}