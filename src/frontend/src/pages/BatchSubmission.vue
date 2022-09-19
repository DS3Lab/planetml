<script setup>
import { ref } from "vue";
import SectionMain from "@/components/SectionMain.vue";
import CardBox from "@/components/CardBox.vue";
import FormField from "@/components/FormField.vue";
import BaseButton from "@/components/BaseButton.vue";
import BaseButtons from "@/components/BaseButtons.vue";
import { PrismEditor } from 'vue-prism-editor';
import 'vue-prism-editor/dist/prismeditor.min.css';
import { highlight, languages } from 'prismjs/components/prism-core';
import 'prismjs/components/prism-json';
import 'prismjs/themes/prism-tomorrow.css';
import { add_new_job, get_job_status } from '@/services/api';

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

function update_job_status(job_id) {
    get_job_status(job_id).then((response) => {
        job_status.value.status = response.data.status
        job_status.value.processed_by = response.data.processed_by
        job_status.value.returned_payload = response.data.returned_payload
    })
}

const expandPass = () => {
    let json_input = JSON.parse(request_json.value);
    try {
        json_input["input"] = eval(json_input["jsinput"])
        request_json.value = JSON.stringify(json_input, null, 4);
    } catch (error) {
        alert(`Error Expanding jsinput: ${error}`);
    }
};

const submitPass = () => {
    let request_payload
    request_payload = JSON.parse(request_json.value)
    add_new_job(request_payload).then((response) => {
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

</script>
    
<template>
    <SectionMain>
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <CardBox>
                <FormField label="Prompt" help="Required. Your Prompt">
                    <div class="content">
                        <prism-editor class="my-editor" v-model="request_json"
                            :highlight="highlighter" line-numbers>
                        </prism-editor>
                    </div>
                </FormField>
                <template #footer>
                    <BaseButtons>
                        <BaseButton @click="expandPass" color="info"
                            type="submit"
                            label="Evaluate Programmable Prompts" />
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