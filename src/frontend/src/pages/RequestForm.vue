<script setup>
import { ref, watch } from "vue";
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
import { add_new_job, get_job_status, available_models } from '@/services/api';

const request_json = ref(`{
"jsinput": "['hippo', 'dog', 'cat', 'bee'].map(animal => ['beijing', 'tokyo', 'palo alto', 'zurich'].map(city => \`Painting of a \$\{animal\} riding a bicycle on the street of \$\{city\}, raining, cat in bicycle basket, trending on artstation\`)).flat()",
"model": "stable_diffusion",
"num_returns": 2
}`)

const job_status = ref({
    "id": "",
    "status": "",
    "processed_by": "",
    "returned_payload": { "output": [[]] }
})

const submit_params = ref({

})

const selected_model = ref("")

function update_job_status(job_id) {
    get_job_status(job_id).then((response) => {
        job_status.value.status = response.data.status
        job_status.value.processed_by = response.data.processed_by
        job_status.value.returned_payload = response.data.returned_payload
        if (!('output' in job_status.value.returned_payload)) {
            job_status.value.returned_payload = { "output": [[]] }
        }
    })
}

const submitPass = () => {
    if (selected_model.value == "") {
        alert("Please select a model")
        return
    }
    let request_payload = submit_params.value
    if (selected_model.value == 'stable_diffusion') {
        request_payload.input = [request_json.value]
    } else {
        request_payload.prompt = [request_json.value]
        request_payload.request_type = "language-model-inference"
        request_payload.stop = [" "]
        request_payload.echo = false
        request_payload.model = selected_model.value
    }
    add_new_job(submit_params.value).then((response) => {
        job_status.value.id = response.data.id
        job_status.value.status = response.data.status
        setInterval(() => {
            update_job_status(job_status.value.id)
        }, 5000)
    })
}

function highlighter(code) {
    return highlight(code, languages.json);
}


watch(selected_model, (newValue, oldValue) => {
    submit_params.value = available_models[newValue]
    console.log(submit_params.value)
});


</script>
    
<template>
    <SectionMain>
        <Warmness />
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <CardBox>
                <FormField label="Prompt" help="Required. Your Prompt">
                    <div class="content">
                        <prism-editor class="my-editor" v-model="request_json"
                            :highlight="highlighter" line-numbers>
                        </prism-editor>
                    </div>
                    <label for="countries"
                        class="block mb-2 text-sm font-medium text-gray-900 dark:text-gray-400">Choose
                        a model</label>
                    <select id="models"
                        class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                        v-model="selected_model">
                        <option v-for="(value, key) in available_models"
                            :value="key">{{key}}</option>
                    </select>
                    <div v-if="selected_model!=''"
                        v-for="(value, key) in available_models[selected_model]">
                        <div>
                            <label :for="'arg-'+key"
                                class="block mb-2 text-sm font-medium text-gray-900 dark:text-gray-300">{{key}}</label>
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
                </div>
            </CardBox>
        </div>
        <div v-for="img_src in job_status.returned_payload.output[0]"
            class="max-w-sm bg-white rounded-lg border border-gray-200 shadow-md dark:bg-gray-800 dark:border-gray-700">
            <a href="#">
                <img class="rounded-t-lg" :src="img_src" alt="" />
            </a>
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