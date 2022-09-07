import { createWebHistory, createRouter } from "vue-router";
import Landing from '../pages/Landing.vue';
import JobView from '../pages/JobView.vue';
import DashboardView from '../pages/DashboardView.vue';
import BatchSubmission from '../pages/BatchSubmission.vue';
import ReportView from '../pages/ReportView.vue';

const routes = [
    { path: '/', component: Landing },
    { path: '/jobs', component: JobView},
    { path: '/status', component: DashboardView},
    { path: '/batch', component: BatchSubmission},
    { path: '/report/:jobid', component: ReportView},
]

const router = createRouter({
    history: createWebHistory(),
    routes,
});

export default router;