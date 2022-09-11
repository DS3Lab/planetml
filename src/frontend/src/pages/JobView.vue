
<template>
    <div class="jobview">
        <div v-if="!is_loaded" id="defaultModal" tabindex="-1" aria-hidden="true"
            class="overflow-y-auto overflow-x-hidden fixed top-0 right-0 left-0 z-50 w-full md:inset-0 h-modal md:h-full">
            <div
                class="relative p-4 w-full max-w-2xl h-full md:h-auto overlay-loading-dialog">
                <!-- Modal content -->
                <div
                    class="relative bg-white rounded-lg shadow dark:bg-gray-700">
                    <!-- Modal header -->
                    <div
                        class="flex justify-between items-start p-4 rounded-t border-b dark:border-gray-600">
                        <h3
                            class="text-xl font-semibold text-gray-900 dark:text-white">
                            Loading Jobs Data...
                        </h3>
                    </div>
                    <!-- Modal body -->
                    <div class="p-6 space-y-6 text-center">
                        <svg class="inline mr-2 w-8 h-8 text-gray-200 animate-spin dark:text-gray-600 fill-blue-600"
                            viewBox="0 0 100 101" fill="none"
                            xmlns="http://www.w3.org/2000/svg">
                            <path
                                d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z"
                                fill="currentColor" />
                            <path
                                d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z"
                                fill="currentFill" />
                        </svg>
                        <p
                            class="text-base leading-relaxed text-gray-500 dark:text-gray-400">
                            I am trying to load the data for you. Please wait.
                            If this takes too long, please refresh the page.
                        </p>

                    </div>
                </div>
            </div>
        </div>
        <div class="grid grid-cols-1 gap-3 lg:grid-cols-4 mb-3"
            v-if="is_loaded">
            <CardBoxWidget color="text-emerald-500" :number="running_jobs"
                prefix="# " label="Running Jobs" />
            <CardBoxWidget color="text-blue-500" :number="finished_jobs"
                prefix="# " label="Finished Jobs" />
            <CardBoxWidget color="text-red-500" :number="pending_jobs"
                prefix="# " label="Pending Jobs" />
            <CardBoxWidget color="text-red-500" :number="failed_jobs"
                prefix="# " label="Failed Jobs" />
        </div>
        <Vue3EasyDataTable v-if="is_loaded" :headers="headers" :items="items"
            alternating show-index>
            <template #expand="item">
                <div style="padding: 15px">
                    Payload
                    <vue-json-pretty :data="item.payload" />
                    Returned Value
                    <vue-json-pretty :data="item.returned_payload" />
                </div>
            </template>
            <template #item-status="{ status }">
                <span v-if="status == 'submitted' || status=='queued'" class="job_status bg-yellow-100 text-yellow-800 text-xs font-medium
                    inline-flex items-center px-2.5 py-0.5 rounded
                    dark:bg-yellow-200 dark:text-yellow-800">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none"
                        viewBox="0 0 32 32" stroke-width="1.5"
                        stroke="currentColor" class="w-6 h-6">
                        <path stroke-linecap="round" stroke-linejoin="round"
                            d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    {{ status }}
                </span>
                <span v-if="status == 'finished'"
                    class="job_status bg-green-100 text-green-800 text-xs font-medium inline-flex items-center px-2.5 py-0.5 rounded dark:bg-green-200 dark:text-green-800">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none"
                        viewBox="0 0 32 32" stroke-width="1.5"
                        stroke="currentColor" class="w-6 h-6">
                        <path stroke-linecap="round" stroke-linejoin="round"
                            d="M10.125 2.25h-4.5c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125v-9M10.125 2.25h.375a9 9 0 019 9v.375M10.125 2.25A3.375 3.375 0 0113.5 5.625v1.5c0 .621.504 1.125 1.125 1.125h1.5a3.375 3.375 0 013.375 3.375M9 15l2.25 2.25L15 12" />
                    </svg>
                    {{ status }}
                </span>
                <span v-if="status == 'running'"
                    class="job_status bg-blue-100 text-blue-800 text-xs font-medium inline-flex items-center px-2.5 py-0.5 rounded dark:bg-blue-200 dark:text-blue-800">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none"
                        viewBox="0 0 32 32" stroke-width="1.5"
                        stroke="currentColor" class="w-6 h-6">
                        <path stroke-linecap="round" stroke-linejoin="round"
                            d="M5.25 5.653c0-.856.917-1.398 1.667-.986l11.54 6.348a1.125 1.125 0 010 1.971l-11.54 6.347a1.125 1.125 0 01-1.667-.985V5.653z" />
                    </svg>
                    {{ status }}
                </span>
                <span v-if="status == 'failed'"
                    class="job_status bg-red-100 text-red-800 text-xs font-medium inline-flex items-center px-2.5 py-0.5 rounded dark:bg-red-200 dark:text-red-800">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none"
                        viewBox="0 0 32 32" stroke-width="1.5"
                        stroke="currentColor" class="w-6 h-6">
                        <path stroke-linecap="round" stroke-linejoin="round"
                            d="M5.25 5.653c0-.856.917-1.398 1.667-.986l11.54 6.348a1.125 1.125 0 010 1.971l-11.54 6.347a1.125 1.125 0 01-1.667-.985V5.653z" />
                    </svg>
                    {{ status }}
                </span>
            </template>
        </Vue3EasyDataTable>
    </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { get_jobs_list } from '../services/api'
import Vue3EasyDataTable from 'vue3-easy-data-table'
import { ref } from 'vue'
import VueJsonPretty from 'vue-json-pretty';
import 'vue-json-pretty/lib/styles.css';
import CardBoxWidget from "@/components/CardBoxWidget.vue";
let items = ref([])
let is_loaded = ref(false)
let running_jobs = ref(0)
let failed_jobs = ref(0)
let pending_jobs = ref(0)
let finished_jobs = ref(0)

const headers = [
    { text: "ID", value: "id" },
    { text: "Source", value: "source" },
    { text: "Type", value: "type", sortable: true },
    { text: "Status", value: "status", sortable: true }
];

function update_jobs_list() {
    get_jobs_list().then((response) => {
        items.value = response.data
        running_jobs.value = 0
        failed_jobs.value = 0
        pending_jobs.value = 0
        finished_jobs.value = 0
        items.value.map((item) => {
            if (item.status == "running") {
                running_jobs.value += 1
            } else if (item.status == "failed") {
                failed_jobs.value += 1
            } else if (item.status == "queued" || item.status == "submitted") {
                pending_jobs.value += 1
            } else if (item.status == "finished") {
                finished_jobs.value += 1
            }
        })
        is_loaded.value = true
    })
}

onMounted(() => {
    update_jobs_list()
})

</script>

<style scoped>
span.header {
    justify-content: center;
}

span .job_status {
    text-transform: capitalize;
}

.overlay-loading-dialog {
    margin-left: auto;
    margin-right: auto;
    margin-top: 20%;
}
.jobview {
    width: 90%;
    margin-left: auto;
    margin-right: auto;
}
</style>