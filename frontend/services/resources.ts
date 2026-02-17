/**
 * Resources API service
 * 
 * Handles all API calls related to resources (list, detail, create, etc.)
 */

import { apiClient } from '@/lib/api-client';
import type { ResourceListResponse, ResourceFilters, Resource } from '@/types/api';

export const resourcesApi = {
  /**
   * Get list of resources with optional filters
   */
  list: async (filters?: ResourceFilters): Promise<ResourceListResponse> => {
    const params = new URLSearchParams();
    
    if (filters?.page) params.append('page', filters.page.toString());
    if (filters?.page_size) params.append('page_size', filters.page_size.toString());
    if (filters?.type) params.append('type', filters.type);
    if (filters?.status) params.append('status', filters.status);
    if (filters?.tags) params.append('tags', filters.tags);
    if (filters?.search) params.append('search', filters.search);
    if (filters?.ordering) params.append('ordering', filters.ordering);
    
    const response = await apiClient.get<ResourceListResponse>(
      `/resources/?${params.toString()}`
    );
    return response.data;
  },

  /**
   * Get resource by ID
   */
  get: async (id: string): Promise<Resource> => {
    const response = await apiClient.get<Resource>(`/resources/${id}/`);
    return response.data;
  },
};
