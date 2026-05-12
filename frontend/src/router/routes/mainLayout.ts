import type { RouteRecordRaw } from 'vue-router';
import { ROUTE_NAMES } from '@/router/enums/routeNames';
import { ROUTE_PATHS } from '@/router/enums/routePaths';
import HomeView from '@/views/HomeView.vue';

export const mainLayoutRoutes: RouteRecordRaw[] = [
  {
    path: ROUTE_PATHS.HOME,
    name: ROUTE_NAMES.HOME,
    component: HomeView,
  },
  {
    path: ROUTE_PATHS.ABOUT,
    name: ROUTE_NAMES.ABOUT,
    component: () => import('@/views/AboutView.vue'),
  },
  {
    path: ROUTE_PATHS.CANDIDATE_DASHBOARD,
    name: ROUTE_NAMES.CANDIDATE_DASHBOARD,
    component: () => import('@/views/CandidateDashboardView/main.vue'),
    meta: { requiresAuth: true, roles: ['job_seeker'] },
  },
  {
    path: ROUTE_PATHS.EMPLOYER_DASHBOARD,
    name: ROUTE_NAMES.EMPLOYER_DASHBOARD,
    component: () => import('@/views/EmployerDashboardView.vue'),
    meta: { requiresAuth: true, roles: ['employer'] },
  },
  {
    path: ROUTE_PATHS.UPLOAD_CV,
    name: ROUTE_NAMES.UPLOAD_CV,
    component: () => import('@/views/CandidateDashboardView/UploadCVView.vue'),
    meta: { requiresAuth: true, roles: ['job_seeker'] },
  },
  {
    path: ROUTE_PATHS.MY_CV,
    name: ROUTE_NAMES.MY_CV,
    component: () => import('@/views/CandidateDashboardView/MyCVView.vue'),
    meta: { requiresAuth: true, roles: ['job_seeker'] },
  },
];
