// frontend/shared/auth/TokenStorage.ts

class TokenStorage {
  static getToken(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem('jwt');
  }

  static setToken(token: string): void {
    if (typeof window !== 'undefined') {
      localStorage.setItem('jwt', token);
    }
  }

  static clear(): void {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('jwt');
    }
  }
}

export default TokenStorage;
