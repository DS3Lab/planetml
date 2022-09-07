<script setup>
import { onMounted } from 'vue';
import { get_job_status } from '../services/api'
import { ref } from 'vue'
import VueJsonPretty from 'vue-json-pretty';
import 'vue-json-pretty/lib/styles.css';
import { useRoute } from 'vue-router';
import { highlight, languages } from 'prismjs/components/prism-core';
import { PaperClipIcon } from '@heroicons/vue/20/solid'

let job_status = ref("")
let job_id = ref("")
let request_json = ref("")
let created_at = ref("")
let source = ref("")
let type = ref("")
let download = ref("")
let output = ref("")
let returned_payload = ref("{}")
let outputs = ref([])

let rendered_finished = false // only render finished job once

const headers = [
    { text: "ID", value: "id" },
    { text: "Source", value: "source" },
    { text: "Type", value: "type", sortable: true },
    { text: "Status", value: "status", sortable: true }
];

function update_job_status() {

    if (rendered_finished == true) { // this means that the job has finished, and we rendered it already
        return
    }

    get_job_status(job_id.value).then((response) => {

        if (response.data.status == "finished") {
            rendered_finished = true
            
        }
        console.log(returned_payload)
        job_status.value = response.data.status
        request_json.value = JSON.stringify(response.data.payload, null, 4)
        created_at.value = response.data.created_at
        source.value = response.data.source
        type.value = response.data.type
        returned_payload.value = response.data.returned_payload['result'].map(function(res){
            return res['result']
        })
        download.value = `https://planetd.shift.ml/job/${job_id.value}`

        outputs.value = []

        let nimg = 0
        //for (const trial_id in response.data.returned_payload.output){
        let trial_id = 0
        for (const prompt_id in response.data.returned_payload.output[trial_id]) {
            nimg = nimg + 1;
            outputs.value.push(response.data.returned_payload.output[trial_id][prompt_id])
            if (nimg > 500) {
                break
            }
        }
    });

}

onMounted(() => {
    job_id.value = useRoute().params.jobid;
    update_job_status()
    setInterval(() => {
        update_job_status()
    }, 10000)
})

function highlighter(code) {
    return highlight(code, languages.json);
}

</script>

<template>
    <div class="overflow-hidden bg-white shadow sm:rounded-lg">
        <div class="px-4 py-5 sm:px-6">
            <h3 class="text-lg font-medium leading-6 text-gray-900">Your Job
                Report</h3>
        </div>
        <div class="border-t border-gray-200 px-4 py-5 sm:p-0">
            <dl class="sm:divide-y sm:divide-gray-200">
                <div
                    class="py-4 sm:grid sm:grid-cols-3 sm:gap-4 sm:py-5 sm:px-6">
                    <dt class="text-sm font-medium text-gray-500">Job ID</dt>
                    <dd
                        class="mt-1 text-sm text-gray-900 sm:col-span-2 sm:mt-0">
                        {{job_id}}</dd>
                </div>
                <div
                    class="py-4 sm:grid sm:grid-cols-3 sm:gap-4 sm:py-5 sm:px-6">
                    <dt class="text-sm font-medium text-gray-500">Status</dt>
                    <dd
                        class="mt-1 text-sm text-gray-900 sm:col-span-2 sm:mt-0">
                        {{job_status}}</dd>
                </div>
                <div
                    class="py-4 sm:grid sm:grid-cols-3 sm:gap-4 sm:py-5 sm:px-6">
                    <dt class="text-sm font-medium text-gray-500">Created at
                    </dt>
                    <dd
                        class="mt-1 text-sm text-gray-900 sm:col-span-2 sm:mt-0">
                        {{ created_at }}</dd>
                </div>
                <div
                    class="py-4 sm:grid sm:grid-cols-3 sm:gap-4 sm:py-5 sm:px-6">
                    <dt class="text-sm font-medium text-gray-500">Source</dt>
                    <dd
                        class="mt-1 text-sm text-gray-900 sm:col-span-2 sm:mt-0">
                        {{source}}</dd>
                </div>
                <div
                    class="py-4 sm:grid sm:grid-cols-3 sm:gap-4 sm:py-5 sm:px-6">
                    <dt class="text-sm font-medium text-gray-500">Type</dt>
                    <dd
                        class="mt-1 text-sm text-gray-900 sm:col-span-2 sm:mt-0">
                        {{type}}</dd>
                </div>
                <div
                    class="py-4 sm:grid sm:grid-cols-3 sm:gap-4 sm:py-5 sm:px-6">
                    <dt class="text-sm font-medium text-gray-500">Input</dt>
                    <dd
                        class="mt-1 text-sm text-gray-900 sm:col-span-2 sm:mt-0">
                        <!--<vue-json-pretty :data="request_json.trim()" />-->
                        {{ request_json }}
                    </dd>
                </div>
                <div v-if="job_status === 'finished'">
                    <div
                    class="py-4 sm:grid sm:grid-cols-3 sm:gap-4 sm:py-5 sm:px-6">
                        <dt class="text-sm font-medium text-gray-500">Output</dt>
                        <dd
                            class="mt-1 text-sm text-gray-900 sm:col-span-2 sm:mt-0">
                            {{ returned_payload }}
                        </dd>
                    </div>
                    <div
                        class="py-4 sm:grid sm:grid-cols-3 sm:gap-4 sm:py-5 sm:px-6">
                        <dt class="text-sm font-medium text-gray-500">Images
                        </dt>
                        <img v-for="o of outputs"
                            style="float:left; padding:5px" width="200"
                            height="200" :src='o' />
                    </div>
                </div>


                <div
                    class="py-4 sm:grid sm:grid-cols-3 sm:gap-4 sm:py-5 sm:px-6">
                    <dt class="text-sm font-medium text-gray-500">Attachments
                    </dt>
                    <dd
                        class="mt-1 text-sm text-gray-900 sm:col-span-2 sm:mt-0">
                        <ul role="list"
                            class="divide-y divide-gray-200 rounded-md border border-gray-200">
                            <li
                                class="flex items-center justify-between py-3 pl-3 pr-4 text-sm">
                                <div class="flex w-0 flex-1 items-center">
                                    <PaperClipIcon
                                        class="h-5 w-5 flex-shrink-0 text-gray-400"
                                        aria-hidden="true" />
                                    <span
                                        class="ml-2 w-0 flex-1 truncate">raw_output.json</span>
                                </div>
                                <div class="ml-4 flex-shrink-0">
                                    <a :href="'https://planetd.shift.ml/job/'+job_id"
                                        class="font-medium text-indigo-600 hover:text-indigo-500">Download</a>
                                </div>
                            </li>
                        </ul>
                    </dd>
                </div>
            </dl>
        </div>
    </div>
</template>

<style scoped>
span.header {
    justify-content: center;
}

span .job_status {
    text-transform: capitalize;
}

/* required class */
.my-editor-small {
    /* we dont use `language-` classes anymore so thats why we need to add background and text color manually */
    background: #000000;
    color: #ccc;

    /* you must provide font-family font-size line-height. Example: */
    font-family: Fira code, Fira Mono, Consolas, Menlo, Courier, monospace;
    font-size: 14px;
    line-height: 1.5;
    padding: 5px;

    max-height: 48em;
    overflow: auto;
}

/* optional class for removing the outline */
.prism-editor__textarea:focus {
    outline: none;
}
</style>
