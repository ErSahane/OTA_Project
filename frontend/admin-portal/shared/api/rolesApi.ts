// No apiClient needed for mock store
import type { Role } from '../types/user';
import { useQuery, useMutation, useQueryClient, UseQueryResult, UseMutationResult } from '@tanstack/react-query';
import { v4 as uuidv4 } from 'uuid';

// In‑memory mock store for roles
const mockRoles: Role[] = [];

/** Fetch all roles */
export const fetchRoles = async (): Promise<Role[]> => {
  return mockRoles;
};

/** Create a new role */
export const createRole = async (payload: Omit<Role, 'id'>): Promise<Role> => {
  const newRole: Role = { ...payload, id: uuidv4() };
  mockRoles.push(newRole);
  return newRole;
};

/** Update an existing role */
export const updateRole = async (id: string, payload: Partial<Omit<Role, 'id'>>): Promise<Role> => {
  const index = mockRoles.findIndex((r) => r.id === id);
  if (index === -1) throw new Error('Role not found');
  const updated = { ...mockRoles[index], ...payload } as Role;
  mockRoles[index] = updated;
  return updated;
};

/** Delete a role */
export const deleteRole = async (id: string): Promise<void> => {
  const index = mockRoles.findIndex((r) => r.id === id);
  if (index === -1) throw new Error('Role not found');
  mockRoles.splice(index, 1);
};

/** React‑Query hooks */
export const useRoles = (): UseQueryResult<Role[], Error> =>
  useQuery(['roles'], fetchRoles);

export const useCreateRole = (): UseMutationResult<Role, Error, Omit<Role, 'id'>, unknown> => {
  const queryClient = useQueryClient();
  return useMutation((payload) => createRole(payload), {
    onSuccess: () => {
      queryClient.invalidateQueries(['roles']);
    },
  });
};

export const useUpdateRole = (): UseMutationResult<Role, Error, { id: string; data: Partial<Omit<Role, 'id'>> }, unknown> => {
  const queryClient = useQueryClient();
  return useMutation(({ id, data }) => updateRole(id, data), {
    onSuccess: (_, vars) => {
      queryClient.invalidateQueries(['roles']);
      queryClient.invalidateQueries(['role', vars.id]);
    },
  });
};

export const useDeleteRole = (): UseMutationResult<void, Error, string, unknown> => {
  const queryClient = useQueryClient();
  return useMutation((id) => deleteRole(id), {
    onSuccess: () => {
      queryClient.invalidateQueries(['roles']);
    },
  });
};
