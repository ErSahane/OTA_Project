// shared/types/provider.ts

export type ProviderType =
  | 'flights'
  | 'hotels'
  | 'cars'
  | 'transfers'
  | 'activities'
  | 'insurance'
  | 'visa'
  | 'packages';

export type ProviderEnvironment = 'sandbox' | 'production';

export type ProviderStatus = 'active' | 'inactive' | 'maintenance' | 'archived';

export type ProviderHealth = 'healthy' | 'warning' | 'offline' | 'error';

export type CredentialType =
  | 'api_key'
  | 'api_secret'
  | 'username'
  | 'password'
  | 'oauth'
  | 'bearer_token'
  | 'jwt'
  | 'certificate';

export interface ProviderCredential {
  id: string;
  type: CredentialType;
  label: string;
  maskedValue: string; // e.g. "****abc123"
  lastRotated?: string; // ISO
}

export interface ProviderEndpoint {
  name: string;
  url: string;
  method: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
  description?: string;
}

export interface ProviderCapability {
  name: string;
  supported: boolean;
}

export interface ProviderRateLimit {
  requestsPerMinute: number;
  requestsPerDay: number;
  concurrentRequests: number;
}

export interface ProviderConfig {
  timeout: number;          // seconds
  retryCount: number;
  cacheDuration: number;    // seconds
  currency: string;
  locale: string;
  country: string;
  language: string;
  requestRate: number;
  responseCache: boolean;
  webhookUrl?: string;
  callbackUrl?: string;
}

export interface ProviderHealthMetrics {
  status: ProviderHealth;
  uptimePercent: number;
  averageLatencyMs: number;
  failureRatePercent: number;
  lastHeartbeat?: string;
  lastSuccessfulRequest?: string;
  lastFailedRequest?: string;
}

export interface Provider {
  id: string;
  name: string;
  slug: string;
  description?: string;
  type: ProviderType;
  logoUrl?: string;
  environment: ProviderEnvironment;
  sandboxUrl?: string;
  productionUrl?: string;
  documentationUrl?: string;
  status: ProviderStatus;
  health: ProviderHealth;
  healthMetrics?: ProviderHealthMetrics;
  config: ProviderConfig;
  capabilities: ProviderCapability[];
  endpoints: ProviderEndpoint[];
  rateLimits: ProviderRateLimit;
  lastSync?: string;  // ISO
  createdBy: string;
  createdAt: string;
  updatedAt: string;
}

export interface ProviderListResponse {
  results: Provider[];
  count: number;
  next?: string;
  previous?: string;
}

export interface AuditLogEntry {
  id: string;
  action:
    | 'create'
    | 'update'
    | 'delete'
    | 'credential_change'
    | 'environment_change'
    | 'status_change'
    | 'connection_test'
    | 'restore';
  user: string;
  timestamp: string;
  ip?: string;
  details?: string;
}

export interface ConnectionTestResult {
  success: boolean;
  latencyMs?: number;
  httpStatus?: number;
  authResult?: string;
  errorMessage?: string;
  timestamp: string;
}

export interface ProviderStats {
  total: number;
  active: number;
  inactive: number;
  maintenance: number;
  archived: number;
  healthy: number;
  warning: number;
  offline: number;
  error: number;
}

export interface ProviderQueryParams {
  page: number;
  pageSize: number;
  search?: string;
  status?: ProviderStatus | '';
  type?: ProviderType | '';
  sortField?: string;
  sortOrder?: 'asc' | 'desc';
}

export interface CreateProviderPayload {
  name: string;
  slug: string;
  description?: string;
  type: ProviderType;
  environment: ProviderEnvironment;
  sandboxUrl?: string;
  productionUrl?: string;
  documentationUrl?: string;
  timeout: number;
  retryCount: number;
  rateLimitPerMinute: number;
}

export type UpdateProviderPayload = Partial<CreateProviderPayload>;

export interface UpdateCredentialsPayload {
  credentials: Array<{
    type: CredentialType;
    label: string;
    value: string;
  }>;
}
