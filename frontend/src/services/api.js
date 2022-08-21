import axios from 'axios';

const tomaapi_endpoint = 'http://localhost:5000/'

function get_site_status() {
    return axios.get(tomaapi_endpoint + 'sites')
}

export {
    get_site_status
}