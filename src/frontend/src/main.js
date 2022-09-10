import { createApp } from 'vue'
import App from './App.vue'
import router from './services/router'
import { createPinia } from "pinia";
import { useMainStore } from "@/stores/main.js";
import { useStyleStore } from "@/stores/style.js";
import VueGtag from "vue-gtag";

import './style.css'
import './index.css'
import 'flowbite';
import 'vue3-easy-data-table/dist/style.css';

const pinia = createPinia();
const app = createApp(App)

const mainStore = useMainStore(pinia);
const styleStore = useStyleStore(pinia);


app.use(router)
app.use(pinia)
app.use(VueGtag, {
    appName: "TOMA",
    pageTrackerScreenViewEnabled: true,
    config: { id: import.meta.env.VITE_G_TRACKING_ID },
}, router)

app.mount('#app')