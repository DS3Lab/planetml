<template>
    <div class="px-4 sm:px-6 lg:px-8">
        <div class="mt-8 flex flex-col" v-if="is_loaded">
            <div class="-my-2 -mx-4 overflow-x-auto sm:-mx-6 lg:-mx-8">
                <div
                    class="inline-block min-w-full py-2 align-middle md:px-6 lg:px-8">
                    <div
                        class="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
                        <table class="min-w-full divide-y divide-gray-300">
                            <thead class="bg-gray-50">
                                <tr>
                                    <th scope="col"
                                        class="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900 sm:pl-6">
                                        Name</th>
                                    <th scope="col"
                                        class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                                        Warmness</th>
                                    <th scope="col"
                                        class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                                        Expected Runtime (s)</th>
                                    <th scope="col"
                                        class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                                        Last Heartbeat</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-gray-200 bg-white">
                                <tr v-for="model in model_warmness"
                                    :key="model.id">
                                    <td
                                        class="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-gray-900 sm:pl-6">
                                        {{ model.name }}</td>
                                    <td
                                        class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                                        {{ warmness_level[model.warmness] }}
                                    </td>
                                    <td
                                        class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                                        {{ model.expected_runtime }}</td>
                                    <td 
                                        class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                                        {{ dayjs().to(dayjs(model.last_heartbeat))}} ({{model.last_heartbeat }})</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
  
<script setup>
import { ref, onMounted } from 'vue'
import { get_model_status } from '@/services/api'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
dayjs.extend(relativeTime)

const is_loaded = ref(false)
const model_warmness = ref([])
const warmness_level = {
    "0": "Scratch",
    "1": "VRAM",
    "0.5": "Booting"
}
onMounted(() => {
    get_model_status().then(res => {
        model_warmness.value = res.data
        // sort model_warmness by the last heartbeat
        model_warmness.value.sort((a, b) => {
            return dayjs(b.last_heartbeat).diff(dayjs(a.last_heartbeat))
        })
        is_loaded.value = true
        console.log(model_warmness.value)
    })
})
</script>