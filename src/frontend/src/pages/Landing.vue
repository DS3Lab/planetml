<template>
    <main class="mx-auto mt-16 max-w-7xl px-4 sm:mt-24">
        <div class="text-center">
            <h1
                class="text-4xl font-bold tracking-tight text-gray-900 sm:text-5xl md:text-6xl">
                <span class="block xl:inline">Run Inference</span>
                {{ ' ' }}
                <span class="block text-indigo-600 xl:inline">at any
                    scale</span>
            </h1>
            <p
                class="mx-auto mt-3 max-w-md text-base text-gray-500 sm:text-lg md:mt-5 md:max-w-3xl md:text-xl">
            </p>
            <div
                class="mx-auto mt-5 max-w-md sm:flex sm:justify-center md:mt-8">
                <div class="rounded-md shadow">
                    <a href="/upload"
                        class="flex w-full items-center justify-center rounded-md border border-transparent bg-indigo-600 px-8 py-3 text-base font-medium text-white md:py-4 md:px-10 md:text-lg">Upload
                        File</a>
                </div>
                <!-- <div class="mt-3 rounded-md shadow sm:mt-0 sm:ml-3">
                    <a href="/batch"
                        class="flex w-full items-center justify-center rounded-md border border-transparent bg-indigo-600 px-8 py-3 text-base font-medium text-white md:py-4 md:px-10 md:text-lg">
                        Batch Prompt</a>
                </div> -->
                <div class="mt-3 rounded-md shadow sm:mt-0 sm:ml-3">
                    <a href="/interactive"
                        class="flex w-full items-center justify-center rounded-md border border-transparent bg-indigo-600 px-8 py-3 text-base font-medium text-white md:py-4 md:px-10 md:text-lg">
                        Interactive Mode</a>
                </div>
            </div>
        </div>
    </main>
</template>

<script setup>

import { useRouter } from 'vue-router';
const router = useRouter()
</script>