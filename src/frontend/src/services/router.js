import { createWebHistory, createRouter } from "vue-router";
import Landing from '../pages/Landing.vue';
import JobView from '../pages/JobView.vue';
import DashboardView from '../pages/DashboardView.vue';
import InteractiveView from '../pages/Interactive.vue';

const routes = [
    { path: '/', component: Landing },
    { path: '/jobs', component: JobView},
    { path: '/status', component: DashboardView},
    { path: '/interactive', component: InteractiveView},
]

const router = createRouter({
    history: createWebHistory(),
    routes,
});

export default router;