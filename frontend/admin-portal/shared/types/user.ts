export interface User {
  id: string;
  avatarUrl?: string;
  name: string;
  email: string;
  roleId: string;
  departmentId: string;
  status: 'active' | 'inactive' | 'pending';
  mfaEnabled: boolean;
  lastLogin?: string; // ISO string
  createdAt: string; // ISO string
}

export interface Role {
  id: string;
  name: string;
  description?: string;
  permissions: string[]; // e.g. ['users.view', 'bookings.update']
  priority: number;
  status: 'enabled' | 'disabled';
}

export interface Department {
  id: string;
  name: string;
}

export interface Invitation {
  id: string;
  email: string;
  roleId: string;
  expiresAt: string; // ISO string
  status: 'pending' | 'sent' | 'accepted' | 'cancelled';
}

export interface Session {
  id: string;
  userId: string;
  ipAddress: string;
  browser: string;
  os: string;
  loginTime: string; // ISO
  lastActivity: string; // ISO
  deviceInfo?: string;
}

export interface AuditLogEntry {
  id: string;
  userId: string;
  action: string;
  timestamp: string; // ISO
  ipAddress?: string;
  details?: string;
}

export interface APIToken {
  id: string;
  token: string; // raw token (shown only on creation)
  name: string;
  scopes: string[];
  createdAt: string;
  expiresAt?: string;
  lastUsed?: string;
}
