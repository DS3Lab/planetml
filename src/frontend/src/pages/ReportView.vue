<template>
    <div class="min-h-full">
        <main>
            <!-- Page header -->
            <div
                class="mx-auto max-w-3xl px-4 sm:px-6 md:flex md:items-center md:justify-between md:space-x-5 lg:max-w-7xl lg:px-8">
                <div class="flex items-center space-x-5">
                    <div>
                        <h1 class="text-2xl font-bold text-gray-900 ta-center">
                            Job Report</h1>
                        <p class="text-sm font-medium text-gray-500">ID
                            <a href="#" class="text-gray-900">{{job_id}}</a> on
                            <time
                                datetime="2020-08-25">{{job_data.created_at}}</time>
                        </p>
                    </div>
                </div>
            </div>

            <div
                class="mx-auto mt-8 grid max-w-3xl grid-cols-1 gap-6 sm:px-6 lg:max-w-7xl lg:grid-flow-col-dense lg:grid-cols-3">
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
                                            {{job_data.status}}</dd>
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
                            <div>
                                <a :href="'https://planetd.shift.ml/job/'+job_id"
                                    class="block bg-gray-50 shadow px-4 py-4 text-center text-sm font-medium text-gray-500 hover:text-gray-700 sm:rounded-b-lg">Read
                                    full output</a>
                            </div>
                        </div>
                    </section>
                    <div v-if="job_data.status === 'finished'">
                        <div
                            class="py-4 sm:grid sm:grid-cols-3 sm:gap-4 sm:py-5 sm:px-6">
                            <dt class="text-sm font-medium text-gray-500">Output
                            </dt>
                            <dd
                                class="mt-1 text-sm text-gray-900 sm:col-span-2 sm:mt-0">
                                <pre>{{ returned_payload }}</pre>
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
                </div>

                <section aria-labelledby="timeline-title"
                    class="lg:col-span-1 lg:col-start-3">
                    <div class="bg-white px-4 py-5 sm:rounded-lg sm:px-6">
                        <h2 id="timeline-title"
                            class="text-lg font-medium text-gray-900">Progress
                        </h2>

                        <!-- Activity Feed -->
                        <div class="mt-6 flow-root">
                            <div
                                class="w-full bg-gray-200 rounded-full dark:bg-gray-700">
                                <div class="bg-blue-600 text-xs font-medium text-blue-100 text-center p-0.5 leading-none rounded-full"
                                    :style="'width: '+(100*progress.finished/progress.total)+'%'">
                                    {{progress.finished}}/{{progress.total}}
                                </div>
                            </div>
                        </div>
                    </div>
                </section>
            </div>
        </main>
    </div>
</template>
  
<script setup>
import { onMounted } from 'vue';
import { get_job_status } from '../services/api'
import { ref } from 'vue'
import VueJsonPretty from 'vue-json-pretty';
import 'vue-json-pretty/lib/styles.css';
import { useRoute } from 'vue-router';
import { highlight, languages } from 'prismjs/components/prism-core';

let job_id = ref("")
let job_data = ref({})
let progress = ref({})
let returned_payload = ref({})
let outputs = ref([])
let rendered_finished = false // only render finished job once

function update_job_status() {
    if (rendered_finished == true) { // this means that the job has finished, and we rendered it already
        return
    }
    get_job_status(job_id.value).then((response) => {
        if (response.data.status == "finished") {
            rendered_finished = true
        }
        if (response.data.status == "running") {
            progress.value = response.data.returned_payload.progress
            console.log(progress)
        }
        job_data.value = response.data
        if ('result' in job_data.value.returned_payload) {
            returned_payload.value = job_data.value.returned_payload['result'].map(function (res) {
                return res['result']['choices'][0]['text']
            })[0]
        }
        outputs.value = []
        let nimg = 0
        //for (const trial_id in response.data.returned_payload.output){
        let trial_id = 0
        console.log(response.data.returned_payload)
        if ('output' in job_data.value.returned_payload) {
            for (const prompt_id in job_data.value.returned_payload.output[trial_id]) {
                nimg = nimg + 1;
                outputs.value.push(job_data.value.returned_payload.output[trial_id][prompt_id])
                if (nimg > 500) {
                    break
                }
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