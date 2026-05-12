import { computed, reactive, readonly } from 'vue';
import type { UserRole } from '@/shared/types';

export type GatewayFlow = 'login' | 'signup';

export interface GatewayLoginPayload {
  role: UserRole;
}

export interface GatewaySignupPayload {
  role: UserRole;
  email: string;
  first_name: string;
  last_name: string;
  company_name?: string;
  company_description?: string;
}

export type GatewayPayload = GatewayLoginPayload | GatewaySignupPayload;

interface GatewayState {
  flow: GatewayFlow | null;
  payload: GatewayPayload | null;
  redirect: string | null;
}

const STORAGE_KEY = 'civis.gateway';

function loadInitialState(): GatewayState {
  if (typeof window === 'undefined') {
    return { flow: null, payload: null, redirect: null };
  }

  try {
    const raw = sessionStorage.getItem(STORAGE_KEY);

    if (!raw) {
      return { flow: null, payload: null, redirect: null };
    }

    const parsed = JSON.parse(raw) as Partial<GatewayState>;

    if (parsed.flow !== 'login' && parsed.flow !== 'signup') {
      return { flow: null, payload: null, redirect: null };
    }

    if (!parsed.payload || typeof parsed.payload !== 'object') {
      return { flow: null, payload: null, redirect: null };
    }

    return {
      flow: parsed.flow,
      payload: parsed.payload as GatewayPayload,
      redirect: typeof parsed.redirect === 'string' ? parsed.redirect : null,
    };
  } catch {
    return { flow: null, payload: null, redirect: null };
  }
}

const state = reactive<GatewayState>(loadInitialState());

function persist() {
  if (state.flow && state.payload) {
    sessionStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({
        flow: state.flow,
        payload: state.payload,
        redirect: state.redirect,
      }),
    );
  } else {
    sessionStorage.removeItem(STORAGE_KEY);
  }
}

export function useGateway() {
  function start(flow: 'login', payload: GatewayLoginPayload, redirect?: string): void;
  function start(flow: 'signup', payload: GatewaySignupPayload, redirect?: string): void;
  function start(flow: GatewayFlow, payload: GatewayPayload, redirect?: string) {
    state.flow = flow;
    state.payload = payload;
    state.redirect = redirect ?? null;
    persist();
  }

  function clear() {
    state.flow = null;
    state.payload = null;
    state.redirect = null;
    persist();
  }

  return {
    state: readonly(state),
    hasFlow: computed(() => state.flow !== null && state.payload !== null),
    start,
    clear,
  };
}
