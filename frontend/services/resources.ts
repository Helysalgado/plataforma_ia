/**
 * Resources API service
 * 
 * Handles all API calls related to resources (list, detail, create, etc.)
 */

import { apiClient } from '@/lib/api-client';
import type { ResourceListResponse, ResourceFilters, Resource } from '@/types/api';

export interface CreateResourceRequest {
  title: string;
  description: string;
  type: 'Prompt' | 'Workflow' | 'Notebook' | 'Dataset' | 'Tool' | 'Other';
  source_type: 'Internal' | 'GitHub-linked';
  tags: string[];
  content?: string;
  example?: string;
  repo_url?: string;
  repo_branch?: string;
  repo_commit_sha?: string;
  license?: string;
  status: 'Sandbox' | 'Pending Validation';
}

export interface UpdateResourceRequest {
  title?: string;
  description?: string;
  type?: 'Prompt' | 'Workflow' | 'Notebook' | 'Dataset' | 'Tool' | 'Other';
  tags?: string[];
  content?: string;
  example?: string;
  changelog?: string;
}

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

  /**
   * Create new resource
   */
  create: async (data: CreateResourceRequest): Promise<Resource> => {
    const response = await apiClient.post<Resource>('/resources/create/', data);
    return response.data;
  },

  /**
   * Update resource (creates new version if latest is Validated)
   */
  update: async (id: string, data: UpdateResourceRequest): Promise<Resource> => {
    const response = await apiClient.patch<Resource>(`/resources/${id}/`, data);
    return response.data;
  },

  /**
   * Delete resource (soft delete)
   */
  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/resources/${id}/`);
  },
};
