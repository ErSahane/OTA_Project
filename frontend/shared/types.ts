// Shared TypeScript types for the OTA Project

export type UserRole =
  | 'SuperAdmin'
  | 'Operations'
  | 'Finance'
  | 'Support'
  | 'ReadOnly';

export interface AuthUser {
  id: string;
  email: string;
  role: UserRole;
  name?: string;
}
