import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './services/router'
import './index.css'
import 'flowbite';
import 'vue3-easy-data-table/dist/style.css';

const app = createApp(App)
app.use(router)
app.mount('#app')