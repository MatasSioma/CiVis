import type { RouteRecordRaw } from 'vue-router';
import type { Component } from 'vue';
import { ROUTE_NAMES } from '@/router/enums/routeNames';
import { ROUTE_PATHS } from '@/router/enums/routePaths';

function loadView(label: string, importer: () => Promise<{ default: Component }>) {
  return async () => {
    if (import.meta.env.DEV) {
      console.debug(`[router] importing auth view: ${label}`);
    }

    try {
      const module = await importer();

      if (import.meta.env.DEV) {
        console.debug(`[router] imported auth view: ${label}`);
      }

      return module;
    } catch (error) {
      console.error(`[router] failed to import auth view: ${label}`, error);
      throw error;
    }
  };
}

export const authLayoutRoutes: RouteRecordRaw[] = [
  {
    path: ROUTE_PATHS.LOGIN,
    name: ROUTE_NAMES.LOGIN,
    component: loadView('LoginView', () => import('@/views/LoginView.vue')),
    meta: { guestOnly: true },
  },
  {
    path: ROUTE_PATHS.SIGNUP,
    name: ROUTE_NAMES.SIGNUP,
    component: loadView('SignupView', () => import('@/views/SignupView.vue')),
    meta: { guestOnly: true },
  },
  {
    path: ROUTE_PATHS.GATEWAY,
    name: ROUTE_NAMES.GATEWAY,
    component: loadView('GatewayView', () => import('@/views/GatewayView.vue')),
    meta: { guestOnly: true },
  },
];
