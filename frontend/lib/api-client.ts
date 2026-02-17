/**
 * API client for BioAI Hub backend
 * 
 * Base configuration for axios instance with backend URL
 */

import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth token
apiClient.interceptors.request.use(
  (config) => {
    // TODO: Add token from cookies/localStorage when auth is implemented
    // const token = getAuthToken();
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`;
    // }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for handling errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // TODO: Handle 401 (redirect to login), 500 (show error toast)
    return Promise.reject(error);
  }
);
