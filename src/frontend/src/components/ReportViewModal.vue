<template>
    <div class="min-h-full">
            <!-- Page header -->
            <div
                class="mx-auto mt-8 grid max-w-3xl grid-cols-1 gap-6 sm:px-6 lg:max-w-7xl lg:grid-flow-col-dense lg:grid-cols-3 job-report-dialog">
                <div class="space-y-6 lg:col-span-2 lg:col-start-1">
                    <!-- Description list-->
                    <section aria-labelledby="applicant-information-title">
                        <div class="bg-white sm:rounded-lg">
                            <div class="px-4 py-5 sm:px-6">
                                <h2 id="applicant-information-title"
                                    class="text-lg font-medium leading-6 text-gray-900">
                                    Job Information</h2>
                                <p class="mt-1 max-w-2xl text-sm text-gray-500">
                                    All Information about the Job</p>
                            </div>
                            <div
                                class="border-t border-gray-200 px-4 py-5 sm:px-6">
                                <dl
                                    class="grid grid-cols-1 gap-x-4 gap-y-8 sm:grid-cols-2">
                                    <div class="sm:col-span-1">
                                        <dt
                                            class="text-sm font-medium text-gray-500">
                                            ID</dt>
                                        <dd class="mt-1 text-sm text-gray-900">
                                            {{job_id}}</dd>
                                    </div>
                                    <div class="sm:col-span-1">
                                        <dt
                                            class="text-sm font-medium text-gray-500">
                                            Status</dt>
                                        <dd class="mt-1 text-sm text-gray-900">
                                            <span
                                                v-if="job_data.status == 'submitted' || job_data.status=='queued'"
                                                class="job_status bg-yellow-100 text-yellow-800 text-xs font-medium
                    inline-flex items-center px-2.5 py-0.5 rounded
                    dark:bg-yellow-200 dark:text-yellow-800">
                                                <svg xmlns="http://www.w3.org/2000/svg"
                                                    fill="none"
                                                    viewBox="0 0 32 32"
                                                    stroke-width="1.5"
                                                    stroke="currentColor"
                                                    class="w-6 h-6">
                                                    <path stroke-linecap="round"
                                                        stroke-linejoin="round"
                                                        d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
                                                </svg>
                                                {{ job_data.status }}
                                            </span>
                                            <span
                                                v-if="job_data.status == 'finished'"
                                                class="job_status bg-green-100 text-green-800 text-xs font-medium inline-flex items-center px-2.5 py-0.5 rounded dark:bg-green-200 dark:text-green-800">
                                                <svg xmlns="http://www.w3.org/2000/svg"
                                                    fill="none"
                                                    viewBox="0 0 32 32"
                                                    stroke-width="1.5"
                                                    stroke="currentColor"
                                                    class="w-6 h-6">
                                                    <path stroke-linecap="round"
                                                        stroke-linejoin="round"
                                                        d="M10.125 2.25h-4.5c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125v-9M10.125 2.25h.375a9 9 0 019 9v.375M10.125 2.25A3.375 3.375 0 0113.5 5.625v1.5c0 .621.504 1.125 1.125 1.125h1.5a3.375 3.375 0 013.375 3.375M9 15l2.25 2.25L15 12" />
                                                </svg>
                                                {{ job_data.status }}
                                            </span>
                                            <span
                                                v-if="job_data.status == 'running'"
                                                class="job_status bg-blue-100 text-blue-800 text-xs font-medium inline-flex items-center px-2.5 py-0.5 rounded dark:bg-blue-200 dark:text-blue-800">
                                                <svg xmlns="http://www.w3.org/2000/svg"
                                                    fill="none"
                                                    viewBox="0 0 32 32"
                                                    stroke-width="1.5"
                                                    stroke="currentColor"
                                                    class="w-6 h-6">
                                                    <path stroke-linecap="round"
                                                        stroke-linejoin="round"
                                                        d="M5.25 5.653c0-.856.917-1.398 1.667-.986l11.54 6.348a1.125 1.125 0 010 1.971l-11.54 6.347a1.125 1.125 0 01-1.667-.985V5.653z" />
                                                </svg>
                                                {{ job_data.status }}
                                            </span>
                                            <span
                                                v-if="job_data.status == 'failed'"
                                                class="job_status bg-red-100 text-red-800 text-xs font-medium inline-flex items-center px-2.5 py-0.5 rounded dark:bg-red-200 dark:text-red-800">
                                                <svg xmlns="http://www.w3.org/2000/svg"
                                                    fill="none"
                                                    viewBox="0 0 32 32"
                                                    stroke-width="1.5"
                                                    stroke="currentColor"
                                                    class="w-6 h-6">
                                                    <path stroke-linecap="round"
                                                        stroke-linejoin="round"
                                                        d="M5.25 5.653c0-.856.917-1.398 1.667-.986l11.54 6.348a1.125 1.125 0 010 1.971l-11.54 6.347a1.125 1.125 0 01-1.667-.985V5.653z" />
                                                </svg>
                                                {{ job_data.status }}
                                            </span>
                                        </dd>
                                    </div>
                                    <div class="sm:col-span-1">
                                        <dt
                                            class="text-sm font-medium text-gray-500">
                                            CreatedAt</dt>
                                        <dd class="mt-1 text-sm text-gray-900">
                                            {{job_data.created_at}}</dd>
                                    </div>
                                    <div class="sm:col-span-1">
                                        <dt
                                            class="text-sm font-medium text-gray-500">
                                            Source</dt>
                                        <dd class="mt-1 text-sm text-gray-900">
                                            {{job_data.source}}</dd>
                                    </div>
                                    <div class="sm:col-span-1">
                                        <dt
                                            class="text-sm font-medium text-gray-500">
                                            Type</dt>
                                        <dd class="mt-1 text-sm text-gray-900">
                                            {{job_data.type}}</dd>
                                    </div>
                                    <div class="sm:col-span-1">
                                        <dt
                                            class="text-sm font-medium text-gray-500">
                                            Processed By</dt>
                                        <dd class="mt-1 text-sm text-gray-900">
                                            {{job_data.processed_by}}</dd>
                                    </div>
                                    <div v-if="job_data.subjobs"
                                        class="sm:col-span-1">
                                        <dt
                                            class="text-sm font-medium text-gray-500">
                                            Subjobs</dt>

                                        <dd v-for="job in job_data.subjobs"
                                            class="mt-1 text-sm text-gray-900">
                                            <a
                                                :href="'/report/'+job">{{job}}</a>
                                        </dd>
                                    </div>
                                    <div class="sm:col-span-2">
                                        <dt
                                            class="text-sm font-medium text-gray-500">
                                            Input</dt>
                                        <dd class="mt-1 text-sm text-gray-900">
                                            <vue-json-pretty
                                                :data="job_data.payload" />
                                        </dd>
                                    </div>
                                </dl>
                            </div>
                        </div>
                        <div v-if="job_data.status === 'finished'">
                            <div
                                class="py-4 sm:grid sm:grid-cols-3 sm:gap-4 sm:py-5 sm:px-6">
                                <dt class="text-sm font-medium text-gray-500">
                                    Output
                                    File
                                </dt>
                                <dd
                                    class="mt-1 text-sm text-gray-900 sm:col-span-2 sm:mt-0">
                                    <a
                                        :href="job_data.returned_payload.filename">{{
                                        job_data.returned_payload.filename
                                        }}</a>
                                </dd>
                            </div>
                            <div>
                                <a :href="job_data.returned_payload.filename"
                                    class="block bg-gray-50 shadow px-4 py-4 text-center text-sm font-medium text-gray-500 hover:text-gray-700 sm:rounded-b-lg">Read
                                    full output</a>
                            </div>
                            <div v-if="outputs.length>0"
                                class="py-4 sm:grid sm:grid-cols-3 sm:gap-4 sm:py-5 sm:px-6">
                                <dt class="text-sm font-medium text-gray-500">
                                    Images
                                </dt>
                                <img v-for="o of outputs"
                                    style="float:left; padding:5px" width="200"
                                    height="200" :src='o' />
                            </div>
                            <div v-if="text_outputs.length>0"
                                class="py-4 sm:grid sm:grid-cols-3 sm:gap-4 sm:py-5 sm:px-6">
                                <dt class="text-sm font-medium text-gray-500">
                                    Returned Text
                                </dt>
                                <span v-for="o of text_outputs">{{o}}</span>
                            </div>
                        </div>
                        <div v-if="job_data.status === 'failed'">
                            <div
                                class="py-4 sm:grid sm:grid-cols-3 sm:gap-4 sm:py-5 sm:px-6">
                                <dt class="text-sm font-medium text-gray-500">
                                    Error
                                </dt>
                                <dd
                                    class="mt-1 text-sm text-gray-900 sm:col-span-2 sm:mt-0">
                                    {{job_data.returned_payload }}
                                </dd>
                            </div>
                        </div>
                    </section>
                </div>
            </div>
    </div>
</template>
  
<script setup>
import { onMounted, defineProps } from 'vue';
import { get_job_status } from '../services/api'
import { ref } from 'vue'
import VueJsonPretty from 'vue-json-pretty';
import 'vue-json-pretty/lib/styles.css';
import axios from 'axios';

let job_data = ref({})
let progress = ref({})
let formatted_output = ref({})
let outputs = ref([])
let text_outputs = ref([])
let rendered_finished = false // only render finished job once
let interval_id = ref(null)
const props = defineProps({
    job_id: String
})



function get_original_outputs(addr) {
    return axios.get(addr)
}

function update_job_status() {
    if (rendered_finished == true) { // this means that the job has finished, and we rendered it already
        return
    }
    get_job_status(props.job_id).then((response) => {
        if (response.data.status == "finished") {
            rendered_finished = true
            clearInterval(interval_id.value)
        }
        if (response.data.status == "failed") {
            rendered_finished = true
            clearInterval(interval_id.value)
        }
        if (response.data.status == "running") {
            progress.value = response.data.returned_payload.progress
            console.log(progress)
        }
        job_data.value = response.data
        if ('result' in job_data.value.returned_payload) {
            formatted_output.value = job_data.value.returned_payload['result'].map(function (res) {
                return res['result']['choices'][0]['text']
            })[0]
        }
        // now process and format the outputs
        if (response.data.status == 'finished' && 'filename' in response.data.returned_payload) {
            get_original_outputs(job_data.value.returned_payload.filename).then((response) => {
                outputs.value = []
                response = response.data
                console.log(response)
                if ('output' in response) {
                    let trial_id = 0
                    let nimg = 0
                    for (const prompt_id in response.output[trial_id]) {
                        nimg = nimg + 1;
                        outputs.value.push(response.output[trial_id][prompt_id])
                        if (nimg > 500) {
                            break
                        }
                    }
                } else if ('request' in response) {
                    if (response['request']['request_type'] === 'language-model-inference') {
                        let return_id = 0
                        let input_id = 0
                        for (const returned_id in response['result']['choices']) {
                            text_outputs.value.push(response['result']['choices'][returned_id]['text'])
                            if (return_id > 500) {
                                break
                            }
                        }
                    }
                }
                else if (response['result'][0]['request']['request_type'] === 'language-model-inference') {
                    let return_id = 0
                    let input_id = 0
                    for (const returned_id in response['result'][input_id]['result']['choices']) {
                        text_outputs.value.push(response['result'][0]['result']['choices'][returned_id]['text'])
                        if (return_id > 500) {
                            break
                        }
                    }
                }
            })
        }
    });
}
onMounted(() => {
    update_job_status()
    interval_id.value = setInterval(() => {
        update_job_status()
    }, 10000)

})
</script>
<style scoped>
.job-report-dialog {
    background-color: white;
    border-radius: 0.5rem;
    box-shadow: 0 0 1rem 0 rgba(0, 0, 0, 0.1);
    border-color: black;
    border-width: 2px;
}
</style>