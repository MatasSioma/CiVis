import type { ObjectValues } from '@/shared/types';

export const ROUTE_NAMES = {
  HOME: 'Home',
  ABOUT: 'About',
  LOGIN: 'Login',
  SIGNUP: 'Signup',
} as const;

export type RouteNamesValues = ObjectValues<typeof ROUTE_NAMES>;
