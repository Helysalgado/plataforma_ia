/**
 * Type definitions for authentication
 */

export interface User {
  id: string;
  email: string;
  name: string;
  email_verified_at: string | null;
  is_admin: boolean;
  created_at: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access: string;
  refresh: string;
  user: User;
}

export interface RegisterRequest {
  email: string;
  name: string;
  password: string;
  password_confirm: string;
}

export interface RegisterResponse {
  message: string;
  user: Omit<User, 'is_admin'>;
}

export interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  register: (data: RegisterRequest) => Promise<void>;
  isAuthenticated: boolean;
}

export interface Notification {
  id: string;
  type: 'ResourceValidated' | 'ResourceForked' | 'ValidationRevoked' | 'ValidationRequested';
  message: string;
  resource_id: string | null;
  read_at: string | null;
  created_at: string;
}

export interface NotificationListResponse {
  count: number;
  results: Notification[];
  unread_count: number;
}
