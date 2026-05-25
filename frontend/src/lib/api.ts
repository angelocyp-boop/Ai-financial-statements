import axios from 'axios';
import type {
  TokenResponse, Client, Engagement, TrialBalance, TBLine,
  FinancialStatement, DisclosureNote, ValidationSummary, Firm,
} from '@/types';

const BASE = process.env.NEXT_PUBLIC_API_URL || '';

export const api = axios.create({
  baseURL: `${BASE}/api`,
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('access_token');
    if (token) config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401 && typeof window !== 'undefined') {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(err);
  },
);

// Auth
export const authApi = {
  login: (email: string, password: string) =>
    api.post<TokenResponse>('/auth/login', { email, password }).then(r => r.data),
  register: (data: { firm_name: string; email: string; password: string; first_name: string; last_name: string }) =>
    api.post<TokenResponse>('/auth/register', data).then(r => r.data),
  me: () => api.get('/auth/me').then(r => r.data),
};

// Firms
export const firmApi = {
  getMyFirm: () => api.get<Firm>('/firms/me').then(r => r.data),
  updateFirm: (data: Partial<Firm>) => api.patch<Firm>('/firms/me', data).then(r => r.data),
  getUsers: () => api.get('/firms/me/users').then(r => r.data),
  inviteUser: (data: { email: string; first_name: string; last_name: string; role: string; password: string }) =>
    api.post('/firms/me/users', data).then(r => r.data),
};

// Clients
export const clientApi = {
  list: () => api.get<Client[]>('/clients').then(r => r.data),
  get: (id: number) => api.get<Client>(`/clients/${id}`).then(r => r.data),
  create: (data: Partial<Client>) => api.post<Client>('/clients', data).then(r => r.data),
  update: (id: number, data: Partial<Client>) => api.patch<Client>(`/clients/${id}`, data).then(r => r.data),
  archive: (id: number) => api.delete(`/clients/${id}`),
};

// Engagements
export const engagementApi = {
  list: (clientId?: number) => api.get<Engagement[]>('/engagements', { params: clientId ? { client_id: clientId } : {} }).then(r => r.data),
  get: (id: number) => api.get<Engagement>(`/engagements/${id}`).then(r => r.data),
  create: (data: Partial<Engagement>) => api.post<Engagement>('/engagements', data).then(r => r.data),
  update: (id: number, data: Partial<Engagement>) => api.patch<Engagement>(`/engagements/${id}`, data).then(r => r.data),
};

// Trial Balance
export const tbApi = {
  upload: (engId: number, file: File, isComparative: boolean) => {
    const fd = new FormData();
    fd.append('file', file);
    return api.post<TrialBalance>(`/trial-balance/upload/${engId}?is_comparative=${isComparative}`, fd, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }).then(r => r.data);
  },
  get: (id: number) => api.get<TrialBalance>(`/trial-balance/${id}`).then(r => r.data),
  listForEngagement: (engId: number) => api.get<TrialBalance[]>(`/trial-balance/engagement/${engId}`).then(r => r.data),
  updateLine: (lineId: number, data: Partial<TBLine>) => api.patch<TBLine>(`/trial-balance/line/${lineId}`, data).then(r => r.data),
  runMapping: (tbId: number) => api.post('/mapping/run', { trial_balance_id: tbId }).then(r => r.data),
};

// Statements
export const statementApi = {
  generate: (engId: number, types?: string[]) =>
    api.post<FinancialStatement[]>('/statements/generate', {
      engagement_id: engId,
      statement_types: types || ['SFP', 'PL', 'CASH_FLOW', 'EQUITY'],
    }).then(r => r.data),
  list: (engId: number) => api.get<FinancialStatement[]>(`/statements/engagement/${engId}`).then(r => r.data),
  get: (id: number) => api.get<FinancialStatement>(`/statements/${id}`).then(r => r.data),
  updateLine: (lineId: number, data: { label?: string; current_amount?: string; comparative_amount?: string; note_reference?: string }) =>
    api.patch(`/statements/line/${lineId}`, data).then(r => r.data),
  approve: (id: number) => api.post(`/statements/${id}/approve`).then(r => r.data),
};

// Disclosures
export const disclosureApi = {
  generate: (engId: number, types?: string[]) =>
    api.post<DisclosureNote[]>('/disclosures/generate', {
      engagement_id: engId,
      note_types: types || null,
    }).then(r => r.data),
  list: (engId: number) => api.get<DisclosureNote[]>(`/disclosures/engagement/${engId}`).then(r => r.data),
  update: (id: number, data: Partial<DisclosureNote>) => api.patch<DisclosureNote>(`/disclosures/${id}`, data).then(r => r.data),
  delete: (id: number) => api.delete(`/disclosures/${id}`),
};

// Validation
export const validationApi = {
  run: (engId: number) => api.post<ValidationSummary>(`/validation/run/${engId}`).then(r => r.data),
  get: (engId: number) => api.get<ValidationSummary>(`/validation/${engId}`).then(r => r.data),
  resolve: (resultId: number) => api.post(`/validation/resolve/${resultId}`).then(r => r.data),
};

// Exports
export const exportApi = {
  word: (engId: number) => api.post(`/exports/word/${engId}`, {}, { responseType: 'blob' }).then(r => r.data),
  pdf: (engId: number) => api.post(`/exports/pdf/${engId}`, {}, { responseType: 'blob' }).then(r => r.data),
};
