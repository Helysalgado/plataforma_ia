/**
 * User API service
 * 
 * Handles all API calls related to user profiles
 */

import { apiClient } from '@/lib/api-client';

export interface UserMetrics {
  total_resources: number;
  validated_resources: number;
  total_votes: number;
  total_reuses: number;
  total_impact: number;
}

export interface UserProfile {
  id: string;
  email: string;
  name: string;
  is_admin: boolean;
  email_verified_at: string | null;
  created_at: string;
  metrics: UserMetrics;
}

export interface UserResourcesResponse {
  count: number;
  page: number;
  page_size: number;
  results: any[]; // ResourceListItem[] from resources types
}

export const usersApi = {
  /**
   * Get user profile by ID
   */
  getProfile: async (userId: string): Promise<UserProfile> => {
    const response = await apiClient.get<UserProfile>(`/users/${userId}/`);
    return response.data;
  },

  /**
   * Get user's published resources
   */
  getResources: async (
    userId: string,
    params?: {
      status?: string;
      page?: number;
      page_size?: number;
    }
  ): Promise<UserResourcesResponse> => {
    const queryParams = new URLSearchParams();
    if (params?.status) queryParams.append('status', params.status);
    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.page_size) queryParams.append('page_size', params.page_size.toString());

    const response = await apiClient.get<UserResourcesResponse>(
      `/users/${userId}/resources/?${queryParams.toString()}`
    );
    return response.data;
  },
};
