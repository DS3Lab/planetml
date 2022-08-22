import { createWebHistory, createRouter } from "vue-router";
import Landing from '../pages/Landing.vue';
import ResourceView from '../pages/ResourceView.vue';
import JobView from '../pages/JobView.vue';
import DashboardView from '../pages/DashboardView.vue';

const routes = [
    { path: '/', component: Landing },
    { path: '/site', component: ResourceView },
    { path: '/jobs', component: JobView},
    { path: '/dashboard', component: DashboardView},
]

const router = createRouter({
    history: createWebHistory(),
    routes,
});

export default router;