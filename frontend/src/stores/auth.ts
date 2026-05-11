import { computed, reactive, readonly } from 'vue';
import { authApi, type LoginPayload, type SignupPayload } from '@/services/auth';
import { ROUTE_NAMES } from '@/router/enums/routeNames';
import type { SessionUser, UserRole } from '@/shared/types';

interface AuthState {
  user: SessionUser | null;
  isReady: boolean;
  isLoading: boolean;
}

const state = reactive<AuthState>({
  user: null,
  isReady: false,
  isLoading: false,
});

let sessionPromise: Promise<SessionUser | null> | null = null;

const STORAGE_KEYS = [
  'civis.auth',
  'civis.user',
  'civis.role',
  'civis.token',
  'civis.session',
];

export const ROLE_LABELS: Record<UserRole, string> = {
  employer: 'Darbdavys',
  job_seeker: 'Darbo ieškantis asmuo',
};

function setSession(user: SessionUser | null) {
  state.user = user;
  state.isReady = true;
}

function clearStoredAuth() {
  STORAGE_KEYS.forEach((key) => {
    localStorage.removeItem(key);
    sessionStorage.removeItem(key);
  });
}

export function getRoleLabel(role: UserRole | null | undefined) {
  return role ? (ROLE_LABELS[role] ?? '') : '';
}

export function dashboardRouteName(role: UserRole) {
  return role === 'employer'
    ? ROUTE_NAMES.EMPLOYER_DASHBOARD
    : ROUTE_NAMES.CANDIDATE_DASHBOARD;
}

export async function ensureSession() {
  if (state.isReady) {
    return state.user;
  }

  sessionPromise ??= authApi.session().then((session) => {
    setSession(session.user);
    return session.user;
  });

  try {
    return await sessionPromise;
  } finally {
    sessionPromise = null;
  }
}

export function useAuth() {
  async function login(payload: LoginPayload) {
    state.isLoading = true;

    try {
      const session = await authApi.login(payload);
      setSession(session.user);
      return session.user;
    } finally {
      state.isLoading = false;
    }
  }

  async function signup(payload: SignupPayload) {
    state.isLoading = true;

    try {
      const session = await authApi.signup(payload);
      setSession(session.user);
      return session.user;
    } finally {
      state.isLoading = false;
    }
  }

  async function logout() {
    state.isLoading = true;

    try {
      await authApi.logout();
    } finally {
      sessionPromise = null;
      clearStoredAuth();
      setSession(null);
      state.isLoading = false;
    }
  }

  return {
    state: readonly(state),
    isAuthenticated: computed(() => Boolean(state.user)),
    login,
    signup,
    logout,
  };
}
