export interface Role {
  id: string;
  name: string;
  description?: string;
  status: 'active' | 'inactive';
  permissions: string[];
  createdAt: string;
  userCount?: number;
  permissionCount?: number;
}
