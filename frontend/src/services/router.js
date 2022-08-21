import { createWebHistory, createRouter } from "vue-router";
import Landing from '../pages/Landing.vue';
import ResourceView from '../pages/ResourceView.vue';
const routes = [
    { path: '/', component: Landing },
    { path: '/site', component: ResourceView },
]

const router = createRouter({
    history: createWebHistory(),
    routes,
});

export default router;