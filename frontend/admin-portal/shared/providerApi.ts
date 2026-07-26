// shared/providerApi.ts

import api from '@shared/api';
import {
  Provider,
  ProviderListResponse,
  ProviderCredential,
  ProviderHealthMetrics,
  AuditLogEntry,
  ConnectionTestResult,
  ProviderStats,
  ProviderQueryParams,
  CreateProviderPayload,
  UpdateProviderPayload,
  UpdateCredentialsPayload,
  ProviderEnvironment,
  ProviderStatus,
} from '@shared/types/provider';

// ── List & Detail ──────────────────────────────────────────────────────────

export const fetchProviders = (params: ProviderQueryParams) =>
  api.get<ProviderListResponse>('/admin/providers/', { params });

export const fetchProvider = (id: string) =>
  api.get<Provider>(`/admin/providers/${id}/`);

export const fetchProviderStats = () =>
  api.get<ProviderStats>('/admin/providers/stats/');

// ── CRUD ───────────────────────────────────────────────────────────────────

export const createProvider = (data: CreateProviderPayload) =>
  api.post<Provider>('/admin/providers/', data);

export const updateProvider = (id: string, data: UpdateProviderPayload) =>
  api.patch<Provider>(`/admin/providers/${id}/`, data);

export const deleteProvider = (id: string) =>
  api.delete(`/admin/providers/${id}/`);

export const restoreProvider = (id: string) =>
  api.post<Provider>(`/admin/providers/${id}/restore/`);

// ── Status & Environment ───────────────────────────────────────────────────

export const setProviderStatus = (id: string, status: ProviderStatus) =>
  api.patch<Provider>(`/admin/providers/${id}/`, { status });

export const switchEnvironment = (id: string, environment: ProviderEnvironment) =>
  api.patch<Provider>(`/admin/providers/${id}/`, { environment });

// ── Credentials ────────────────────────────────────────────────────────────

export const fetchCredentials = (id: string) =>
  api.get<ProviderCredential[]>(`/admin/providers/${id}/credentials/`);

export const updateCredentials = (id: string, data: UpdateCredentialsPayload) =>
  api.patch<ProviderCredential[]>(`/admin/providers/${id}/credentials/`, data);

export const rotateCredential = (id: string, credentialId: string) =>
  api.post<ProviderCredential>(`/admin/providers/${id}/credentials/${credentialId}/rotate/`);

// ── Connection Testing ─────────────────────────────────────────────────────

export const testConnection = (id: string) =>
  api.post<ConnectionTestResult>(`/admin/providers/${id}/test-connection/`);

// ── Health ─────────────────────────────────────────────────────────────────

export const fetchProviderHealth = (id: string) =>
  api.get<ProviderHealthMetrics>(`/admin/providers/${id}/health/`);

// ── Audit Log ──────────────────────────────────────────────────────────────

export const fetchAuditLog = (id: string) =>
  api.get<AuditLogEntry[]>(`/admin/providers/${id}/audit/`);
