/**
 * Authentication API service
 * 
 * Handles all API calls related to authentication (login, register, logout, etc.)
 */

import { apiClient } from '@/lib/api-client';
import type { 
  LoginRequest, 
  LoginResponse, 
  RegisterRequest, 
  RegisterResponse,
  User 
} from '@/types/auth';

export const authApi = {
  /**
   * Login with email and password
   */
  login: async (data: LoginRequest): Promise<LoginResponse> => {
    const response = await apiClient.post<LoginResponse>('/auth/login/', data);
    return response.data;
  },

  /**
   * Register new user
   */
  register: async (data: RegisterRequest): Promise<RegisterResponse> => {
    const response = await apiClient.post<RegisterResponse>('/auth/register/', data);
    return response.data;
  },

  /**
   * Verify email with token
   */
  verifyEmail: async (token: string): Promise<{ message: string }> => {
    const response = await apiClient.get(`/auth/verify-email/${token}/`);
    return response.data;
  },

  /**
   * Get current user profile
   */
  me: async (): Promise<User> => {
    const response = await apiClient.get<User>('/auth/me/');
    return response.data;
  },

  /**
   * Logout (client-side only for now)
   */
  logout: async (): Promise<void> => {
    // Token removal is handled by AuthContext
    // Backend doesn't need logout endpoint for JWT (stateless)
  },
};
