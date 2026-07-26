import { z } from 'zod';

// Zod schema for creating/updating a user. Fields aligned with User interface.
export const userSchema = z.object({
  name: z.string().min(1, 'Name is required'),
  email: z.string().email('Invalid email address'),
  roleId: z.string().min(1, 'Role is required'),
  departmentId: z.string().min(1, 'Department is required'),
  status: z.enum(['active', 'inactive', 'pending']).default('active'),
  mfaEnabled: z.boolean().default(false),
  avatarUrl: z.string().url().optional().or(z.literal('')).optional(),
});

export type UserFormValues = z.infer<typeof userSchema>;
