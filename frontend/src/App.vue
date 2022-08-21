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

  <main class="main_view">
    <router-view />
  </main>

  <footer class="fixed inset-x-0 bottom-0">
    <PMFooter />
  </footer>

</template>

<style scoped>
.main_view {
    margin-left: auto;
    margin-right: auto;
    width: 80%;
    height: 100%;
}
</style>
