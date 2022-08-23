import { createWebHistory, createRouter } from "vue-router";
import Landing from '../pages/Landing.vue';
import JobView from '../pages/JobView.vue';
import DashboardView from '../pages/DashboardView.vue';

const routes = [
    { path: '/', component: Landing },
    { path: '/jobs', component: JobView},
    { path: '/status', component: DashboardView},
]

const router = createRouter({
    history: createWebHistory(),
    routes,
});

export default router;