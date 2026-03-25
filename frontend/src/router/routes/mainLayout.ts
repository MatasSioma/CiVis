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
];
