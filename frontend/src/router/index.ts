import {
  createRouter,
  createWebHistory,
  isNavigationFailure,
  type RouteRecordRaw,
} from 'vue-router';
import MainLayout from '@/layouts/MainLayout.vue';
import AuthenticationLayout from '@/layouts/AuthenticationLayout.vue';
import { mainLayoutRoutes } from './routes/mainLayout';
import { authLayoutRoutes } from './routes/authLayout';
import { ROUTE_NAMES } from './enums/routeNames';
import { dashboardRouteName, ensureSession } from '@/stores/auth';
import type { UserRole } from '@/shared/types';

declare module 'vue-router' {
  interface RouteMeta {
    requiresAuth?: boolean;
    guestOnly?: boolean;
    roles?: UserRole[];
  }
}

const isDebugEnabled = import.meta.env.DEV;

function routeLabel(route: {
  name?: unknown;
  fullPath?: string;
  path?: string;
}) {
  return `${String(route.name ?? '(unnamed)')} ${route.fullPath ?? route.path ?? ''}`;
}

function withAuthenticationLayout(route: RouteRecordRaw): RouteRecordRaw {
  return {
    path: route.path.startsWith('/') ? route.path : `/${route.path}`,
    component: AuthenticationLayout,
    children: [
      {
        ...route,
        path: '',
      },
    ],
  };
}

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    ...authLayoutRoutes.map(withAuthenticationLayout),
    {
      component: MainLayout,
      path: '/',
      children: mainLayoutRoutes,
    },
  ],
});

router.beforeEach(async (to, from) => {
  if (isDebugEnabled) {
    console.debug('[router] beforeEach', {
      from: routeLabel(from),
      to: routeLabel(to),
      matched: to.matched.map((record) => record.path),
      meta: to.meta,
    });
  }

  let user = null;

  try {
    user = await ensureSession();
  } catch (error) {
    console.error('[router] Failed to resolve auth session', error);
  }

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

router.afterEach((to, from, failure) => {
  if (!isDebugEnabled) {
    return;
  }

  if (failure) {
    const failureType = isNavigationFailure(failure) ? failure.type : 'unknown';

    console.error('[router] navigation failed', {
      from: routeLabel(from),
      to: routeLabel(to),
      type: failureType,
      failure,
    });
    return;
  }

  console.debug('[router] afterEach', {
    from: routeLabel(from),
    to: routeLabel(to),
    matched: to.matched.map((record) => ({
      path: record.path,
      name: record.name,
      components: Object.keys(record.components ?? {}),
    })),
  });
});

router.onError((error, to, from) => {
  console.error('[router] uncaught navigation error', {
    from: from ? routeLabel(from) : '(initial)',
    to: to ? routeLabel(to) : '(unknown)',
    error,
  });
});

export default router;
