<script setup>
import { onMounted } from 'vue';
import { get_job_status } from '../services/api'
import Vue3EasyDataTable from 'vue3-easy-data-table'
import { ref } from 'vue'
import VueJsonPretty from 'vue-json-pretty';
import 'vue-json-pretty/lib/styles.css';
import CardBoxWidget from "@/components/CardBoxWidget.vue";
import { useRoute } from 'vue-router';
import { PrismEditor } from 'vue-prism-editor';
import { highlight, languages } from 'prismjs/components/prism-core';

let items = ref([])
let is_loaded = ref(false)
let running_jobs = ref(0)
let failed_jobs = ref(0)
let pending_jobs = ref(0)
let finished_jobs = ref(0)
let jobstat = ref("")
let job_status = ref("")
let job_id = ref("")
let request_json = ref("")
let created_at = ref("")
let source = ref("")
let type = ref("")
let download = ref("")
let output = ref("")

let outputs = ref([])

let rendered_finished = false // only render finished job once

const headers = [
    { text: "ID", value: "id" },
    { text: "Source", value: "source" },
    { text: "Type", value: "type", sortable: true },
    { text: "Status", value: "status", sortable: true }
];

function update_job_status() {

    if (rendered_finished == true){ // this means that the job has finished, and we rendered it already
        return
    }

    get_job_status(job_id.value).then((response) => {

        if(response.data.status == "finished"){
            rendered_finished = true
        }

        job_status.value = response.data.status
        request_json.value = JSON.stringify(response.data.payload, null, 4)
        created_at.value = response.data.created_at
        source.value = response.data.source
        type.value = response.data.type
        download.value = `https://planetd.shift.ml/job/${job_id.value}`

        console.log(response.data)

        outputs.value = []

        let nimg = 0
        //for (const trial_id in response.data.returned_payload.output){
        let trial_id = 0
            for (const prompt_id in response.data.returned_payload.output[trial_id]){
                nimg = nimg + 1;
                outputs.value.push(response.data.returned_payload.output[trial_id][prompt_id])
                if(nimg > 500){
                    break
                }
            }
        //}
        console.log(outputs.value)

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
    <div class="">

        Job ID: {{ job_id }}
        Status: {{ job_status }}

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <CardBox>
                <div class="content">
                    <prism-editor class="my-editor-small" v-model="request_json"
                        :highlight="highlighter" line-numbers>
                    </prism-editor>
                </div>
            </CardBox>
            <CardBox>
                <div>
                    Created at: {{ created_at }} <br/>
                    Source: {{ source }} <br/>
                    Type: {{ type }} <br/>     
                    Full Response: <a target='_blank' :href='download' >Download here</a>
                </div>
            </CardBox>
        </div>

        <div v-if="job_status == 'finished'">
            <h2>Output Snippets (First 500 Results)</h2>

            <div>
                <img v-for="o of outputs"
                    style="float:left; padding:5px" width="200" height="200" :src='o' /> 
            </div>

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
