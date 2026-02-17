/**
 * Type definitions for BioAI Hub API
 */

export interface Resource {
  id: string;
  owner_name: string;
  source_type: 'Internal' | 'GitHub-linked';
  latest_version: ResourceVersion;
  forks_count: number;
  is_fork: boolean;
  derived_from_resource_id: string | null;
  created_at: string;
  updated_at: string;
  votes_count: number;
}

export interface ResourceVersion {
  id: string;
  version_number: string;
  title: string;
  description: string;
  type: 'Prompt' | 'Workflow' | 'Notebook' | 'Dataset' | 'Tool' | 'Other';
  tags: string[];
  status: 'Sandbox' | 'Pending Validation' | 'Validated';
  content?: string;
  repo_url?: string;
  repo_branch?: string;
  example?: string;
  is_latest: boolean;
  validated_at: string | null;
  created_at: string;
  pid: string;
}

export interface ResourceListResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Resource[];
}

export interface ResourceFilters {
  page?: number;
  page_size?: number;
  type?: string;
  status?: string;
  tags?: string;
  search?: string;
  ordering?: string;
}
