import axios from 'axios';

const tomaapi_endpoint = 'https://planetd.shift.ml/'

function get_site_status() {
    return axios.get(tomaapi_endpoint + 'sites')
}

export {
    get_site_status
}