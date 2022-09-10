import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './services/router'
import './index.css'
import 'flowbite';
import 'vue3-easy-data-table/dist/style.css';
import { createPinia } from "pinia";
import { useMainStore } from "@/stores/main.js";
import { useStyleStore } from "@/stores/style.js";
import VueGtag from "vue-gtag";

const pinia = createPinia();
const app = createApp(App)
const mainStore = useMainStore(pinia);
const styleStore = useStyleStore(pinia);

app.use(router)
app.use(pinia)
app.use(VueGtag, {
    appName: "TOMA",
    pageTrackerScreenViewEnabled: true,
    config: { id: "G-VZP6PKKFW0" },
}, router)

app.mount('#app')