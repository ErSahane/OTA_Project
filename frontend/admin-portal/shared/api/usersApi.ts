import { v4 as uuidv4 } from 'uuid';
import type { User } from '../types/user';
import { useQuery, useMutation, useQueryClient, UseQueryResult, UseMutationResult } from '@tanstack/react-query';

// In‑memory mock store (initialised on first import)
const mockUsers: User[] = [];

/** Fetch paginated list of users (mock implementation) */
export const fetchUsers = async (page: number = 1, pageSize: number = 20, search?: string): Promise<{ data: User[]; total: number }> => {
  // Simple filter for mock data
  let filtered = mockUsers;
  if (search) {
    const lower = search.toLowerCase();
    filtered = filtered.filter((u) => u.name.toLowerCase().includes(lower) || u.email.toLowerCase().includes(lower));
  }
  const total = filtered.length;
  const start = (page - 1) * pageSize;
  const data = filtered.slice(start, start + pageSize);
  return { data, total };
};

/** Fetch a single user by id */
export const fetchUser = async (id: string): Promise<User> => {
  const user = mockUsers.find((u) => u.id === id);
  if (!user) throw new Error('User not found');
  return user;
};

/** Create a new user */
export const createUser = async (payload: Omit<User, 'id' | 'createdAt'>): Promise<User> => {
  const newUser: User = {
    ...payload,
    id: uuidv4(),
    createdAt: new Date().toISOString(),
  } as User;
  mockUsers.push(newUser);
  return newUser;
};

/** Update an existing user */
export const updateUser = async (id: string, payload: Partial<Omit<User, 'id' | 'createdAt'>>): Promise<User> => {
  const index = mockUsers.findIndex((u) => u.id === id);
  if (index === -1) throw new Error('User not found');
  const updated = { ...mockUsers[index], ...payload } as User;
  mockUsers[index] = updated;
  return updated;
};

/** Delete a user (soft delete) */
export const deleteUser = async (id: string): Promise<void> => {
  const index = mockUsers.findIndex((u) => u.id === id);
  if (index === -1) throw new Error('User not found');
  // Mark as inactive for soft delete
  mockUsers[index].status = 'inactive';
};

/** React‑Query hooks */
export const useUsers = (page: number, pageSize: number, search?: string): UseQueryResult<{ data: User[]; total: number }, Error> =>
  useQuery(['users', page, pageSize, search], () => fetchUsers(page, pageSize, search), { keepPreviousData: true });

export const useUser = (id: string): UseQueryResult<User, Error> => useQuery(['user', id], () => fetchUser(id));

export const useCreateUser = (): UseMutationResult<User, Error, Omit<User, 'id' | 'createdAt'>, unknown> => {
  const queryClient = useQueryClient();
  return useMutation((payload) => createUser(payload), {
    onSuccess: () => {
      queryClient.invalidateQueries(['users']);
    },
  });
};

export const useUpdateUser = (): UseMutationResult<User, Error, { id: string; data: Partial<Omit<User, 'id' | 'createdAt'>> }, unknown> => {
  const queryClient = useQueryClient();
  return useMutation(({ id, data }) => updateUser(id, data), {
    onSuccess: (_, vars) => {
      queryClient.invalidateQueries(['user', vars.id]);
      queryClient.invalidateQueries(['users']);
    },
  });
};

export const useDeleteUser = (): UseMutationResult<void, Error, string, unknown> => {
  const queryClient = useQueryClient();
  return useMutation((id) => deleteUser(id), {
    onSuccess: (_, id) => {
      queryClient.invalidateQueries(['user', id]);
      queryClient.invalidateQueries(['users']);
    },
  });
};
