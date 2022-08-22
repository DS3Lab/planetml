<template>
    <div class="">
        <Vue3EasyDataTable v-if="is_loaded" :headers="headers" :items="items" alternating show-index>
            <template #expand="item">
                <div style="padding: 15px">
                    Payload
                    <vue-json-pretty :data="item.payload" />
                    Returned Value
                    <vue-json-pretty :data="item.returned_payload" />
                </div>
            </template>
            <template #item-status="{ status }">
                <span
                    class="bg-blue-100 text-blue-800 text-xs font-medium inline-flex items-center px-2.5 py-0.5 rounded dark:bg-blue-200 dark:text-blue-800">
                    <svg aria-hidden="true" class="mr-1 w-3 h-3"
                        fill="currentColor" viewBox="0 0 20 20"
                        xmlns="http://www.w3.org/2000/svg">
                        <path fill-rule="evenodd"
                            d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z"
                            clip-rule="evenodd"></path>
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

let items = ref([])
let is_loaded = ref(false)

const headers = [
    { text: "ID", value: "id" },
    { text: "Source", value: "source" },
    { text: "Type", value: "type", sortable: true },
    { text: "Status", value: "status", sortable: true }
];

onMounted(() => {
    get_jobs_list().then(res => {
        res.data.map(item => {
            items.value.push(item)
        })
        is_loaded.value = true
    })
})

</script>

<style>
span.header {
    justify-content: center;    
}

</style>