
<template>
    <div class="">
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
                <span v-if="status == 'submitted' || status=='pending'"
                    class="bg-blue-100 text-blue-800 text-xs font-medium
                    inline-flex items-center px-2.5 py-0.5 rounded
                    dark:bg-blue-200 dark:text-blue-800">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none"
                        viewBox="0 0 32 32" stroke-width="1.5"
                        stroke="currentColor" class="w-6 h-6">
                        <path stroke-linecap="round" stroke-linejoin="round"
                            d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    {{ status }}
                </span>
                <span v-if="status == 'finished'"
                    class="bg-blue-100 text-blue-800 text-xs font-medium inline-flex items-center px-2.5 py-0.5 rounded dark:bg-blue-200 dark:text-blue-800">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none"
                        viewBox="0 0 32 32" stroke-width="1.5"
                        stroke="currentColor" class="w-6 h-6">
                        <path stroke-linecap="round" stroke-linejoin="round"
                            d="M10.125 2.25h-4.5c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125v-9M10.125 2.25h.375a9 9 0 019 9v.375M10.125 2.25A3.375 3.375 0 0113.5 5.625v1.5c0 .621.504 1.125 1.125 1.125h1.5a3.375 3.375 0 013.375 3.375M9 15l2.25 2.25L15 12" />
                    </svg>
                    {{ status }}
                </span>
                <span v-if="status == 'running'"
                    class="bg-blue-100 text-blue-800 text-xs font-medium inline-flex items-center px-2.5 py-0.5 rounded dark:bg-blue-200 dark:text-blue-800">
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
    setInterval(() => {
        update_jobs_list()
    }, 10000)
})

</script>

<style>
span.header {
    justify-content: center;
}

span {
    text-transform: capitalize;
}
</style>