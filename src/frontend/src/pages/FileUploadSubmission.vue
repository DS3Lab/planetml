<script setup>
import { ref } from "vue";
import SectionMain from "@/components/SectionMain.vue";
import CardBox from "@/components/CardBox.vue";
import FormField from "@/components/FormField.vue";
import BaseButton from "@/components/BaseButton.vue";
import BaseButtons from "@/components/BaseButtons.vue";
import { add_new_job, get_job_status, upload_file_to_planetd } from '@/services/api';

const file_uploader = ref(null)
const selected_file = ref(null)

function upload_file() {
    selected_file.value = file_uploader.value.files[0];
}

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
        if (!('output' in job_status.value.returned_payload)) {
            job_status.value.returned_payload = { "output": [[]] }
        }
    })
}

const submitPass = () => {
    let request_payload
    upload_file_to_planetd(selected_file.value).then((response) => {
        request_payload = {
            "url": response.data.filename,
        }
        add_new_job(request_payload).then((response) => {
            job_status.value.id = response.data.id
            job_status.value.status = response.data.status
            setInterval(() => {
                update_job_status(job_status.value.id)
            }, 5000)
        })
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

                        <div class="flex justify-center items-center w-full">
                            <label for="dropzone-file"
                                class="flex flex-col justify-center items-center w-full h-64 bg-gray-50 rounded-lg border-2 border-gray-300 border-dashed cursor-pointer dark:hover:bg-bray-800 dark:bg-gray-700 hover:bg-gray-100 dark:border-gray-600 dark:hover:border-gray-500 dark:hover:bg-gray-600">
                                <div
                                    class="flex flex-col justify-center items-center pt-5 pb-6">
                                    <svg aria-hidden="true"
                                        class="mb-3 w-10 h-10 text-gray-400"
                                        fill="none" stroke="currentColor"
                                        viewBox="0 0 24 24"
                                        xmlns="http://www.w3.org/2000/svg">
                                        <path stroke-linecap="round"
                                            stroke-linejoin="round"
                                            stroke-width="2"
                                            d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12">
                                        </path>
                                    </svg>
                                    <p
                                        class="mb-2 text-sm text-gray-500 dark:text-gray-400">
                                        <span class="font-semibold">Click to
                                            upload</span>
                                    </p>
                                    <p
                                        class="text-xs text-gray-500 dark:text-gray-400">
                                        Your file must be in <code>jsonl</code>
                                        format.
                                    </p>
                                    <p v-if="selected_file"
                                        class="text-xs text-gray-500 dark:text-gray-400">
                                        Selected file: {{selected_file.name}}
                                    </p>
                                </div>
                                <input id="dropzone-file" @change="upload_file"
                                    type="file" class="hidden"
                                    ref="file_uploader" />
                            </label>
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