<template>
    <div class="container px-6 py-16 mx-auto text-center">
        <div class="max-w-lg mx-auto">
            <h1
                class="text-3xl font-bold text-gray-800 dark:text-white md:text-4xl">
                Running Inference at Any Scale</h1>
            <p class="mt-6 text-gray-500 dark:text-gray-300">Lorem ipsum
                dolor sit, amet consectetur adipisicing elit. Libero
                similique
                obcaecati illum mollitia.</p>
            <button class="px-6 py-2 mt-6 text-sm font-medium leading-5 text-center text-white capitalize bg-blue-600 rounded-lg hover:bg-blue-500 md:mx-0 md:w-auto focus:outline-none" @click="jumpTo('/interactive')">
                Start Running Inference
            </button>
        </div>
    </div>
</template>

<script setup>

import { useRouter } from 'vue-router';
const router = useRouter()

function jumpTo (page) {
    router.replace(page)
}

</script>