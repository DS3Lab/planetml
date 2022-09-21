<script setup>
import { ref, watch, onMounted,computed } from "vue";
import SectionMain from "@/components/SectionMain.vue";
import CardBox from "@/components/CardBox.vue";
import FormField from "@/components/FormField.vue";
import BaseButton from "@/components/BaseButton.vue";
import BaseButtons from "@/components/BaseButtons.vue";
import Warmness from "@/components/Warmness.vue";
import { PrismEditor } from 'vue-prism-editor';
import 'vue-prism-editor/dist/prismeditor.min.css';
import { highlight, languages } from 'prismjs/components/prism-core';
import 'prismjs/components/prism-json';
import 'prismjs/themes/prism-tomorrow.css';
import { add_new_job, get_job_status, available_models, get_model_status } from '@/services/api';

const request_prompt = ref(`Freely type anything...`)

const job_status = ref({
    "id": "",
    "status": "",
    "processed_by": "",
    "returned_payload": { "output": [[]] }
})
const submit_params = ref({})
const selected_model = ref("")
const warmed_models = ref([])
const cold_models = ref([])

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
        request_payload.num_returns = Math.min(5, parseInt(request_payload.num_returns))
        // check if num_returns is a valid integer
        if (isNaN(request_payload.num_returns)) {
            alert("Please enter a valid integer for num_returns")
            return
        }
    } else {
        request_payload.prompt = [request_prompt.value]
        request_payload.request_type = "language-model-inference"
         // request_payload.max_tokens = parseInt(request_payload.max_tokens)
        request_payload.max_tokens = Math.min(128, parseInt(request_payload.max_tokens))
        request_payload.stop = request_payload.stop.split(';').filter(word => word.length > 0);
        request_payload.temperature = parseFloat(request_payload.temperature)
        request_payload.top_p = parseFloat(request_payload.top_p)
        request_payload.best_of = 1
        request_payload.n = parseInt(request_payload.n)
        request_payload.logprobs = parseFloat(request_payload.logprobs)
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
    }
    add_new_job(request_payload).then((response) => {
        job_status.value.id = response.data.id
        job_status.value.status = response.data.status
        setInterval(() => {
            update_job_status(job_status.value.id)
        }, 5000)
        window.open("https://toma.pages.dev/report/"+response.data.id, '_blank');
    })
}

function highlighter(code) {
    return highlight(code, languages.json);
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
        <Warmness />
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <CardBox>
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
                        <option v-for="key in warmed_models"
                            :value="key">{{key}}</option>
                        <option disabled v-for="key in cold_models"
                            :value="key">{{key}}</option>
                    </select>
                    <div v-if="selected_model!=''"
                        v-for="(value, key) in available_models[selected_model]">
                        <div>
                            <label :for="'arg-'+key" v-if="key!=='stop'"
                                class="block mb-2 text-sm font-medium text-gray-900 dark:text-gray-300">{{key}}</label>
                                <label :for="'arg-'+key" v-if="key==='stop'"
                                class="block mb-2 text-sm font-medium text-gray-900 dark:text-gray-300">{{key}}, split by ;</label>
                            <input type="text" :id="'arg-'+key"
                                v-model="submit_params[key]"
                                class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                                :placeholder="key+' ('+value+')'" required>
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
                        v-if="job_status.status === 'failed'||job_status.status === 'finished'  "> >>> Goto <a :href='"/report/" + job_status.id'>{{
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

    min-height: 48em;
    max-height: 48em;
    overflow: auto;
}

/* optional class for removing the outline */
.prism-editor__textarea:focus {
    outline: none;
}

.status_indicator {
    text-align: left;
}
</style>