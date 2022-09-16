<script setup>
import { useRoute } from 'vue-router';
import PMHeader from './components/PMHeader.vue';
import GlobalDialogOverlay from './components/GlobalDialogOverlay.vue';
const route = useRoute();
// This starter template is using Vue 3 <script setup> SFCs
// Check out https://vuejs.org/api/sfc-script-setup.html#script-setup
</script>

<template>
  <header v-if="route.path!='/profile'">
    <PMHeader />
  </header>

  <main class="main_view">
    <GlobalDialogOverlay />
    <router-view />
  </main>

  <!--<footer class="fixed inset-x-0 bottom-0">
    <PMFooter />
  </footer>-->

</template>

<style scoped>
.main_view {
  margin-left: auto;
  margin-right: auto;
  width: 80%;
  height: 100%;
}
</style>
