/**
 * Authentication Context
 * 
 * Provides global authentication state and methods:
 * - User data
 * - Login/Logout
 * - Token management (localStorage)
 * - Auto-fetch user on mount if token exists
 */

'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { authApi } from '@/services/auth';
import type { User, AuthContextType, LoginRequest, RegisterRequest } from '@/types/auth';

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const TOKEN_KEY = 'bioai_access_token';
const REFRESH_KEY = 'bioai_refresh_token';

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  // Initialize: check if token exists and fetch user
  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem(TOKEN_KEY);
      
      if (token) {
        try {
          const userData = await authApi.me();
          setUser(userData);
        } catch (error) {
          console.error('Failed to fetch user:', error);
          // Token invalid, clear it
          localStorage.removeItem(TOKEN_KEY);
          localStorage.removeItem(REFRESH_KEY);
        }
      }
      
      setLoading(false);
    };

    initAuth();
  }, []);

  const login = async (email: string, password: string) => {
    try {
      const response = await authApi.login({ email, password });
      
      // Store tokens
      localStorage.setItem(TOKEN_KEY, response.access);
      localStorage.setItem(REFRESH_KEY, response.refresh);
      
      // Set user
      setUser(response.user);
    } catch (error: any) {
      // Re-throw with user-friendly message
      if (error.response?.status === 401) {
        throw new Error('Credenciales incorrectas');
      } else if (error.response?.data?.detail) {
        throw new Error(error.response.data.detail);
      } else {
        throw new Error('Error al iniciar sesión. Intenta de nuevo.');
      }
    }
  };

  const logout = () => {
    // Clear tokens
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_KEY);
    
    // Clear user
    setUser(null);
    
    // Call API logout (optional, for cleanup)
    authApi.logout();
  };

  const register = async (data: RegisterRequest) => {
    try {
      await authApi.register(data);
      // Note: User must verify email before login
    } catch (error: any) {
      if (error.response?.data?.email) {
        throw new Error('Este email ya está registrado');
      } else if (error.response?.data) {
        // Backend validation errors
        const firstError = Object.values(error.response.data)[0];
        throw new Error(Array.isArray(firstError) ? firstError[0] : String(firstError));
      } else {
        throw new Error('Error al registrarse. Intenta de nuevo.');
      }
    }
  };

  const value: AuthContextType = {
    user,
    loading,
    login,
    logout,
    register,
    isAuthenticated: !!user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

// Helper to get token (for api-client interceptor)
export function getAuthToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem(TOKEN_KEY);
}
