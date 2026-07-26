"use client";

import { useRouter } from 'next/navigation';
import { useEffect, ReactNode } from 'react';
import { useAuth } from '@shared/auth/AuthProvider';
import { UserRole } from '@shared/types';

interface Props {
  children: ReactNode;
  requiredRoles?: UserRole[];
}

export const ProtectedRoute = ({ children, requiredRoles }: Props) => {
  const { user } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!user) {
      router.replace('/login');
    } else if (requiredRoles && !requiredRoles.includes(user.role)) {
      router.replace('/unauthorized');
    }
  }, [user, router, requiredRoles]);

  if (!user) return null;
  if (requiredRoles && !requiredRoles.includes(user.role)) return null;

  return <>{children}</>;
};
