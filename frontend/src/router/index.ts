import { createRouter, createWebHistory } from 'vue-router';
import MainLayout from '@/layouts/MainLayout.vue';
import AuthenticationLayout from '@/layouts/AuthenticationLayout.vue';
import { mainLayoutRoutes } from './routes/mainLayout';
import { authLayoutRoutes } from './routes/authLayout';
import { ROUTE_NAMES } from './enums/routeNames';
import {
  dashboardRouteName,
  ensureSession,
} from '@/stores/auth';
import type { UserRole } from '@/shared/types';

declare module 'vue-router' {
  interface RouteMeta {
    requiresAuth?: boolean;
    guestOnly?: boolean;
    roles?: UserRole[];
  }
}

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      component: AuthenticationLayout,
      children: authLayoutRoutes,
    },
    {
      component: MainLayout,
      path: '/',
      children: mainLayoutRoutes,
    },
  ],
});

router.beforeEach(async (to) => {
  const user = await ensureSession();

  if (to.meta.guestOnly && user) {
    return { name: dashboardRouteName(user.role) };
  }

  if (to.meta.requiresAuth && !user) {
    return {
      name: ROUTE_NAMES.LOGIN,
      query: { redirect: to.fullPath },
    };
  }

  if (user && to.meta.roles && !to.meta.roles.includes(user.role)) {
    return { name: dashboardRouteName(user.role) };
  }

  return true;
});

export default router;
