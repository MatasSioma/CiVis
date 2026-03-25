import type { RouteRecordRaw } from 'vue-router';
import { ROUTE_NAMES } from '@/router/enums/routeNames';
import { ROUTE_PATHS } from '@/router/enums/routePaths';

export const authLayoutRoutes: RouteRecordRaw[] = [
  {
    path: ROUTE_PATHS.LOGIN,
    name: ROUTE_NAMES.LOGIN,
    component: () => import('@/views/LoginView.vue'),
  },
  {
    path: ROUTE_PATHS.SIGNUP,
    name: ROUTE_NAMES.SIGNUP,
    component: () => import('@/views/SignupView.vue'),
  },
];
