<script setup>
import { useRoute } from 'vue-router'
const route = useRoute();
import PMHeader from './components/PMHeader.vue';
import PMFooter from './components/PMFooter.vue';
// This starter template is using Vue 3 <script setup> SFCs
// Check out https://vuejs.org/api/sfc-script-setup.html#script-setup
</script>

<template>
  <header>
    <PMHeader />
  </header>

  <main>
    <router-view />
  </main>

  <footer>
    <PMFooter />
  </footer>

</template>

<style scoped>
</style>
