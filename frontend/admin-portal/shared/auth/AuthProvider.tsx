// frontend/shared/auth/AuthProvider.tsx

"use client";

import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import api from '@shared/api';
import { AuthUser, UserRole } from '@shared/types';
import TokenStorage from '@shared/auth/TokenStorage';
import jwtDecode from 'jwt-decode';

interface AuthContextProps {
  user: AuthUser | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

interface JwtPayload {
  sub: string;
  email: string;
  role: UserRole;
  name: string;
}

const AuthContext = createContext<AuthContextProps | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [token, setToken] = useState<string | null>(null);

  // Initialise from storage and verify token via backend
  useEffect(() => {
    const stored = TokenStorage.getToken();
    if (stored) {
      api
        .get('/auth/me/')
        .then((res) => {
          setUser(res.data as AuthUser);
          setToken(stored);
        })
        .catch(() => {
          TokenStorage.clear();
        });
    }
  }, []);

  const login = async (email: string, password: string): Promise<void> => {
    const response = await api.post('/auth/login/', { email, password });
    const jwt: string = response.data.access;
    TokenStorage.setToken(jwt);
    const payload = jwtDecode<JwtPayload>(jwt);
    const authUser: AuthUser = {
      id: payload.sub,
      email: payload.email,
      role: payload.role,
      name: payload.name,
    };
    setUser(authUser);
    setToken(jwt);
  };

  const logout = () => {
    TokenStorage.clear();
    setUser(null);
    setToken(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextProps => {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return ctx;
};
