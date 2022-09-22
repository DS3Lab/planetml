<script setup>
import { ref, watch, onMounted, Teleport } from "vue";
import SectionMain from "@/components/SectionMain.vue";
import CardBox from "@/components/CardBox.vue";
import FormField from "@/components/FormField.vue";
import BaseButton from "@/components/BaseButton.vue";
import BaseButtons from "@/components/BaseButtons.vue";
import Warmness from "@/components/Warmness.vue";
import ReportViewDialog from "@/components/ReportViewModal.vue";
import { PrismEditor } from 'vue-prism-editor';
import 'vue-prism-editor/dist/prismeditor.min.css';
import { highlight, languages } from 'prismjs/components/prism-core';
import 'prismjs/components/prism-json';
import 'prismjs/themes/prism-tomorrow.css';
import { add_new_job, get_job_status, available_models, get_model_status, default_args } from '@/services/api';

const request_prompt = ref(`Freely type anything...`)

const job_status = ref({
    "id": "",
    "status": "",
    "processed_by": "",
    "returned_payload": { "output": [[]] }
})
const submit_params = ref({})
const selected_model = ref("")
const current_job = ref("")
const warmed_models = ref([])
const cold_models = ref([])
const open_warmness = ref(false)
const open_jobmodal = ref(false)
function update_job_status(job_id) {
    get_job_status(job_id).then((response) => {
        job_status.value.status = response.data.status
        job_status.value.processed_by = response.data.processed_by
        job_status.value.returned_payload = response.data.returned_payload
    })
}

const submitPass = () => {
    if (selected_model.value == "") {
        alert("Please select a model")
        return
    }
    // a deep copy
    let request_payload = JSON.parse(JSON.stringify(submit_params.value))
    request_payload.model = selected_model.value
    if (selected_model.value == 'stable_diffusion') {
        request_payload.input = [request_prompt.value]
        request_payload.num_returns = parseInt(request_payload.num_returns)
        // check if num_returns is a valid integer
        if (isNaN(request_payload.num_returns)) {
            alert("Please enter a valid integer for num_returns")
            return
        }
        // alert if num_returns is larger than 5
        if (request_payload.num_returns > 5) {
            alert("num_returns is limited to < 5")
            return
        }
    } else {
        request_payload.prompt = [request_prompt.value]
        request_payload.request_type = "language-model-inference"
        // request_payload.max_tokens = parseInt(request_payload.max_tokens)
        request_payload.max_tokens = parseInt(request_payload.max_tokens)
        request_payload.stop = [];
        request_payload.temperature = parseFloat(request_payload.temperature)
        request_payload.top_p = parseFloat(request_payload.top_p)
        request_payload.best_of = 1
        request_payload.n = parseInt(request_payload.n)
        request_payload.logprobs = 1
        request_payload.echo = false
        // check if max_tokens is a valid integer
        if (isNaN(request_payload.max_tokens)) {
            alert("Please enter a valid integer for max_tokens")
            return
        }
        // check if temperature is a valid float
        if (isNaN(request_payload.temperature)) {
            alert("Please enter a valid float for temperature")
            return
        }
        // check if top_p is a valid float
        if (isNaN(request_payload.top_p)) {
            alert("Please enter a valid float for top_p")
            return
        }
        // check if best_of is a valid integer
        if (isNaN(request_payload.best_of)) {
            alert("Please enter a valid integer for best_of")
            return
        }
        // check if n is a valid integer
        if (isNaN(request_payload.n)) {
            alert("Please enter a valid integer for n")
            return
        }
        // check if logprobs is a valid float
        if (isNaN(request_payload.logprobs)) {
            alert("Please enter a valid float for logprobs")
            return
        }
        // alert if max_tokens is larger than 128
        if (request_payload.max_tokens > 128) {
            alert("max_tokens is limited to < 128")
            return
        }
        // alert if temperature is larger than 1
        if (request_payload.temperature > 1) {
            alert("temperature is limited to <= 1")
            return
        }
        // alert if top_p is larger than 1
        if (request_payload.top_p > 1) {
            alert("top_p is limited to <= 1)")
            return
        }
        // alert if prompt is longer than 512
        if (request_payload.prompt[0].split(/\s+/).length > 512) {
            alert("prompt length is limited to < 512 words")
            return
        }
        // alert if n is larger than 5
        if (request_payload.n > 5) {
            alert("n is limited to < 5")
            return
        }
    }
    add_new_job(request_payload).then((response) => {
        job_status.value.id = response.data.id
        job_status.value.status = response.data.status
        setInterval(() => {
            update_job_status(job_status.value.id)
        }, 5000)
        current_job.value = response.data.id
        open_jobmodal.value = true
        // window.open("https://toma.pages.dev/report/" + response.data.id, '_blank');
    })
}

function highlighter(code) {
    return highlight(code, languages.json);
}

function go_report(job_id) {
    window.open("https://toma.pages.dev/report/" + job_id, '_blank');
}

watch(selected_model, (newValue, oldValue) => {
    submit_params.value = available_models[newValue]
});

onMounted(() => {
    get_model_status().then((response) => {
        for (let model in response.data) {
            if (response.data[model].warmness == 1) {
                warmed_models.value.push(response.data[model]['name'])
            }
        }
        cold_models.value = Object.keys(available_models).filter(model => !warmed_models.value.includes(model))
    })

})
</script>
    
<template>
    <SectionMain>
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Teleport to="body">
                <div v-if="open_warmness" class="p-6 bg-white rounded-lg border border-gray-200 shadow-md dark:bg-gray-800 dark:border-gray-700 warmness_modal">
                        <Warmness></Warmness>
                        <button class="focus:outline-none text-white bg-red-700 hover:bg-red-800 focus:ring-4 focus:ring-red-300 font-medium rounded-lg text-sm px-5 py-2.5 mr-2 mb-2 dark:bg-red-600 dark:hover:bg-red-700 dark:focus:ring-red-900 close_button" @click="open_warmness = false">Close</button>
                </div>
                <div v-if="open_jobmodal" class="job_modal">
                    <ReportViewDialog :job_id="current_job"></ReportViewDialog>
                    <button class="focus:outline-none text-white bg-green-700 hover:bg-green-800 focus:ring-4 focus:ring-green-300 font-medium rounded-lg text-sm px-5 py-2.5 mr-2 mb-2 dark:bg-green-600 dark:hover:bg-green-700 dark:focus:ring-green-800 newtab_button" @click="go_report(current_job)">Open in
                        New Tab</button>
                    <button class="focus:outline-none text-white bg-red-700 hover:bg-red-800 focus:ring-4 focus:ring-red-300 font-medium rounded-lg text-sm px-5 py-2.5 mr-2 mb-2 dark:bg-red-600 dark:hover:bg-red-700 dark:focus:ring-red-900 close_button" @click="open_jobmodal = false">Close</button>
                    
                </div>
            </Teleport>
            <CardBox>
                <button type="button"
                    class="focus:outline-none text-white bg-green-700 hover:bg-green-800 focus:ring-4 focus:ring-green-300 font-medium rounded-lg text-sm px-5 py-2.5 mr-2 mb-2 dark:bg-green-600 dark:hover:bg-green-700 dark:focus:ring-green-800"
                    @click="open_warmness = true">Warmness</button>
                <FormField label="Prompt" help="Required. Your Prompt">
                    <div class="content">
                        <prism-editor class="my-editor" v-model="request_prompt"
                            :highlight="highlighter" line-numbers>
                        </prism-editor>
                    </div>
                    <label for="countries"
                        class="block mb-2 text-sm font-medium text-gray-900 dark:text-gray-400">Choose
                        a model</label>
                    <select id="models"
                        class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                        v-model="selected_model">
                        <option v-for="key in warmed_models" :value="key">
                            {{key}}</option>
                        <option disabled v-for="key in cold_models"
                            :value="key">{{key}}</option>
                    </select>
                    <div v-if="selected_model!=''"
                        v-for="(value, key) in available_models[selected_model]">
                        <div>
                            <label :for="'arg-'+key" v-if="key!=='stop'"
                                class="block mb-2 text-sm font-medium text-gray-900 dark:text-gray-300">{{key}}</label>
                            <label :for="'arg-'+key" v-if="key==='stop'"
                                class="block mb-2 text-sm font-medium text-gray-900 dark:text-gray-300">{{key}},
                                split by ;</label>
                            <input type="text" :id="'arg-'+key"
                                v-model="submit_params[key]"
                                class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                                :placeholder="key+' ('+default_args[key]+')'" required>
                        </div>
                    </div>
                </FormField>

                <template #footer>
                    <BaseButtons>
                        <BaseButton @click="submitPass" color="info"
                            type="submit" label="Submit" />
                    </BaseButtons>
                </template>
            </CardBox>
            <CardBox>
                <div>
                    <p class="status_indicator" v-if="job_status.id !== ''"> >>>
                        Your job is submitted,
                        with the id <a :href='"/report/" + job_status.id'>{{
                        job_status.id }}</a></p>
                    <p class="status_indicator"
                        v-if="job_status.status === 'running'"> >>> Your job is
                        running</p>
                    <p class="status_indicator"
                        v-if="job_status.status === 'finished'"> >>> Your job is
                        finished </p>
                    <p class="status_indicator"
                        v-if="job_status.status === 'finished'"> >>> Your job
                        returned {{ job_status.returned_payload }}
                    </p>
                    <p class="status_indicator"
                        v-if="job_status.status === 'failed'"> >>> Your job
                        returned {{ job_status.returned_payload }}
                    </p>
                    <p class="status_indicator"
                        v-if="job_status.status === 'failed'||job_status.status === 'finished'  ">
                        >>> Goto <a :href='"/report/" + job_status.id'>{{
                        job_status.id }}</a> for more detail
                    </p>
                </div>
            </CardBox>
        </div>
    </SectionMain>
</template>
    
<style scoped>
/* required class */
.my-editor {
    /* we dont use `language-` classes anymore so thats why we need to add background and text color manually */
    background: #2d2d2d;
    color: #ccc;

    /* you must provide font-family font-size line-height. Example: */
    font-family: Fira code, Fira Mono, Consolas, Menlo, Courier, monospace;
    font-size: 14px;
    line-height: 1.5;
    padding: 5px;

    min-height: 14em;
    max-height: 14em;
    overflow: auto;
}

/* optional class for removing the outline */
.prism-editor__textarea:focus {
    outline: none;
}

.status_indicator {
    text-align: left;
}

.warmness_modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5);
    z-index: 999;
}

.job_modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0);
    z-index: 999;
    display: flex;
    justify-content: center;
    align-items: center;
}
.close_button {
    position: absolute;
    top: 0;
    right: 0;
    padding: 10px;
}

.newtab_button {
    position: absolute;
    top: 0;
    right: 5em;
    padding: 10px;
}
</style>