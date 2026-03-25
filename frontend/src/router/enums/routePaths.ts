import type { ObjectValues } from '@/shared/types';

export const ROUTE_PATHS = {
  HOME: '',
  ABOUT: 'about',
  LOGIN: 'login',
  SIGNUP: 'signup',
} as const;

export type RoutePathsValues = ObjectValues<typeof ROUTE_PATHS>;
