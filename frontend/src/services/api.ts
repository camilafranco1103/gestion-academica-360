import axios, { AxiosError, type InternalAxiosRequestConfig } from 'axios';

const ACCESS_KEY = 'token';
const REFRESH_KEY = 'refreshToken';

export const tokenStore = {
  get access(): string | null {
    return localStorage.getItem(ACCESS_KEY);
  },
  get refresh(): string | null {
    return localStorage.getItem(REFRESH_KEY);
  },
  set(access: string, refresh: string) {
    localStorage.setItem(ACCESS_KEY, access);
    localStorage.setItem(REFRESH_KEY, refresh);
  },
  clear() {
    localStorage.removeItem(ACCESS_KEY);
    localStorage.removeItem(REFRESH_KEY);
  },
};

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
});

api.interceptors.request.use((config) => {
  const token = tokenStore.access;
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

interface TokenPair {
  access_token: string;
  refresh_token: string;
}

// Single in-flight refresh shared by every request that hit a 401.
let refreshing: Promise<string> | null = null;

async function refreshAccessToken(): Promise<string> {
  const refreshToken = tokenStore.refresh;
  if (!refreshToken) throw new Error('no refresh token');
  // Plain axios: the refresh call must not go through this interceptor.
  const { data } = await axios.post<TokenPair>(`${api.defaults.baseURL}/api/auth/refresh`, {
    refresh_token: refreshToken,
  });
  // The server rotates refresh tokens: the old one is now revoked.
  tokenStore.set(data.access_token, data.refresh_token);
  return data.access_token;
}

type RetriableConfig = InternalAxiosRequestConfig & { _retry?: boolean };

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const original = error.config as RetriableConfig | undefined;
    const isAuthCall = original?.url?.startsWith('/api/auth/') ?? false;

    if (error.response?.status !== 401 || !original || original._retry || isAuthCall) {
      return Promise.reject(error);
    }
    original._retry = true;
    try {
      refreshing ??= refreshAccessToken().finally(() => {
        refreshing = null;
      });
      const token = await refreshing;
      original.headers.Authorization = `Bearer ${token}`;
      return api(original);
    } catch (refreshError) {
      tokenStore.clear();
      window.location.assign('/login');
      return Promise.reject(refreshError);
    }
  },
);

export interface User {
  id: string;
  email: string;
  nombre: string;
  roles: string[];
  permissions: string[];
  is_2fa_enabled: boolean;
}

export async function getCurrentUser(): Promise<User> {
  const response = await api.get<User>('/api/auth/me');
  return response.data;
}

export interface LoginInput {
  email: string;
  password: string;
  totp_code?: string;
}

export async function login(input: LoginInput): Promise<void> {
  const { data } = await api.post<TokenPair>('/api/auth/login', input);
  tokenStore.set(data.access_token, data.refresh_token);
}

export async function logout(): Promise<void> {
  const refreshToken = tokenStore.refresh;
  tokenStore.clear();
  if (refreshToken) {
    // Best effort: revoke the refresh token server-side.
    await api.post('/api/auth/logout', { refresh_token: refreshToken }).catch(() => undefined);
  }
}

export async function getAuthConfig(): Promise<{ public_register: boolean }> {
  const { data } = await api.get<{ public_register: boolean }>('/api/auth/config');
  return data;
}

/** Extracts the API's `detail` message from an axios error, if any. */
export function apiErrorDetail(err: unknown): { status: number; detail?: string } {
  const e = err as AxiosError<{ detail?: unknown }>;
  const detail = e.response?.data?.detail;
  return { status: e.response?.status ?? 0, detail: typeof detail === 'string' ? detail : undefined };
}

export default api;
