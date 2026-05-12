import type { RouteRecordRaw } from 'vue-router';
import { ROUTE_NAMES } from '@/router/enums/routeNames';
import { ROUTE_PATHS } from '@/router/enums/routePaths';

export const authLayoutRoutes: RouteRecordRaw[] = [
  {
    path: ROUTE_PATHS.LOGIN,
    name: ROUTE_NAMES.LOGIN,
    component: () => import('@/views/LoginView.vue'),
    meta: { guestOnly: true },
  },
  {
    path: ROUTE_PATHS.SIGNUP,
    name: ROUTE_NAMES.SIGNUP,
    component: () => import('@/views/SignupView.vue'),
    meta: { guestOnly: true },
  },
  {
    path: ROUTE_PATHS.GATEWAY,
    name: ROUTE_NAMES.GATEWAY,
    component: () => import('@/views/GatewayView.vue'),
    meta: { guestOnly: true },
  },
];
