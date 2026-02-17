/**
 * Explore Page - Resource Catalog
 * Based on Figma design (docs/ux/figma/explore.png)
 * 
 * Features:
 * - Filter chips for resource types
 * - Organized sections (Featured, New, Requesting Validation)
 * - Clean card layout with validation badges
 */

'use client';

import { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import Link from 'next/link';
import { resourcesApi } from '@/services/resources';
import type { Resource } from '@/types/api';

export default function ExplorePage() {
  const { isAuthenticated } = useAuth();
  const searchParams = useSearchParams();
  const [featuredResources, setFeaturedResources] = useState<Resource[]>([]);
  const [newResources, setNewResources] = useState<Resource[]>([]);
  const [pendingResources, setPendingResources] = useState<Resource[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeFilter, setActiveFilter] = useState<string>('all');

  useEffect(() => {
    loadResources();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams]);

  const loadResources = async () => {
    try {
      setLoading(true);

      const searchQuery = searchParams.get('search');
      
      // Load featured (validated)
      const featuredResponse = await resourcesApi.list({
        page: 1,
        page_size: 4,
        status: 'Validated',
        ordering: '-vote_count',
        search: searchQuery || undefined,
      });
      setFeaturedResources(featuredResponse.results);

      // Load new resources
      const newResponse = await resourcesApi.list({
        page: 1,
        page_size: 8,
        ordering: '-created_at',
        search: searchQuery || undefined,
      });
      setNewResources(newResponse.results);

      // Load requesting validation
      const pendingResponse = await resourcesApi.list({
        page: 1,
        page_size: 4,
        status: 'Pending Validation',
        ordering: '-created_at',
        search: searchQuery || undefined,
      });
      setPendingResources(pendingResponse.results);

    } catch (error) {
      console.error('Error loading resources:', error);
    } finally {
      setLoading(false);
    }
  };

  const filters = [
    { id: 'all', label: 'All Types' },
    { id: 'Notebook', label: 'Notebook' },
    { id: 'Prompt', label: 'Prompt' },
    { id: 'GPT', label: 'GPT' },
    { id: 'Dataset', label: 'Dataset' },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Page Header */}
      <div className="bg-white px-6 py-8 border-b border-gray-200">
        <div className="max-w-6xl mx-auto">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Explore Resources</h1>
              <p className="mt-2 text-gray-600">
                Discover and share AI tools for bioinformatics research
              </p>
            </div>
            {isAuthenticated && (
              <Link
                href="/publish"
                className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 inline-flex items-center gap-2"
              >
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
                </svg>
                Publish Resource
              </Link>
            )}
          </div>

          {/* Filter Chips */}
          <div className="mt-6 flex items-center gap-2">
            <button className="px-3 py-1 text-sm text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 inline-flex items-center gap-1">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 3c2.755 0 5.455.232 8.083.678.533.09.917.556.917 1.096v1.044a2.25 2.25 0 01-.659 1.591l-5.432 5.432a2.25 2.25 0 00-.659 1.591v2.927a2.25 2.25 0 01-1.244 2.013L9.75 21v-6.568a2.25 2.25 0 00-.659-1.591L3.659 7.409A2.25 2.25 0 013 5.818V4.774c0-.54.384-1.006.917-1.096A48.32 48.32 0 0112 3z" />
              </svg>
              Filter
            </button>
            {filters.map((filter) => (
              <button
                key={filter.id}
                onClick={() => setActiveFilter(filter.id)}
                className={`px-3 py-1 text-sm rounded-lg transition-colors ${
                  activeFilter === filter.id
                    ? 'bg-primary-600 text-white'
                    : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
                }`}
              >
                {filter.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-6xl mx-auto px-6 py-8">
        {loading ? (
          <div className="space-y-12">
            {[...Array(3)].map((_, i) => (
              <div key={i}>
                <div className="h-6 w-48 bg-gray-200 rounded mb-4 animate-pulse"></div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                  {[...Array(4)].map((_, j) => (
                    <div key={j} className="h-48 bg-gray-100 rounded-lg animate-pulse"></div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <>
            {/* Featured Resources Section */}
            {featuredResources.length > 0 && (
              <section className="mb-12">
                <div className="flex items-center gap-2 mb-4">
                  <svg className="w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 00-2.456 2.456zM16.894 20.567L16.5 21.75l-.394-1.183a2.25 2.25 0 00-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 001.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 001.423 1.423l1.183.394-1.183.394a2.25 2.25 0 00-1.423 1.423z" />
                  </svg>
                  <h2 className="text-xl font-semibold text-gray-900">Featured Resources</h2>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {featuredResources.map((resource) => (
                    <ResourceCard key={resource.id} resource={resource} featured />
                  ))}
                </div>
              </section>
            )}

            {/* New Resources Section */}
            {newResources.length > 0 && (
              <section className="mb-12">
                <div className="flex items-center gap-2 mb-4">
                  <svg className="w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <h2 className="text-xl font-semibold text-gray-900">New Resources</h2>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                  {newResources.map((resource) => (
                    <ResourceCard key={resource.id} resource={resource} compact />
                  ))}
                </div>
              </section>
            )}

            {/* Requesting Validation Section */}
            {pendingResources.length > 0 && (
              <section>
                <div className="flex items-center gap-2 mb-4">
                  <svg className="w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <h2 className="text-xl font-semibold text-gray-900">Requesting Validation</h2>
                  <span className="text-xs text-amber-600 bg-amber-50 px-2 py-1 rounded">Help Review</span>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                  {pendingResources.map((resource) => (
                    <ResourceCard key={resource.id} resource={resource} compact />
                  ))}
                </div>
              </section>
            )}

            {/* Empty State */}
            {!loading && featuredResources.length === 0 && newResources.length === 0 && pendingResources.length === 0 && (
              <div className="text-center py-16">
                <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-gray-400" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" />
                  </svg>
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">No resources found</h3>
                <p className="text-gray-600 mb-4">
                  {searchParams.get('search')
                    ? 'Try adjusting your search or filters'
                    : 'Be the first to publish a resource!'}
                </p>
                {!searchParams.get('search') && isAuthenticated && (
                  <Link
                    href="/publish"
                    className="inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
                  >
                    Publish Resource
                  </Link>
                )}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

// Resource Card Component (inline for now, can be extracted)
function ResourceCard({
  resource,
  featured = false,
  compact = false,
}: {
  resource: Resource;
  featured?: boolean;
  compact?: boolean;
}) {
  const getStatusBadge = () => {
    const status = resource.latest_version?.status;
    if (status === 'Validated') {
      return <span className="px-2 py-1 bg-green-100 text-green-700 text-xs font-medium rounded">✓ Validated</span>;
    } else if (status === 'Pending Validation') {
      return <span className="px-2 py-1 bg-amber-100 text-amber-700 text-xs font-medium rounded">Sandbox</span>;
    }
    return <span className="px-2 py-1 bg-gray-100 text-gray-700 text-xs font-medium rounded">Sandbox</span>;
  };

  return (
    <Link
      href={`/resources/${resource.id}`}
      className={`bg-white border border-gray-200 rounded-lg hover:shadow-lg hover:border-primary-300 transition-all ${
        featured ? 'p-6' : 'p-4'
      }`}
    >
      <div className="flex items-start justify-between mb-3">
        {getStatusBadge()}
        <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
          {resource.latest_version?.resource_type || 'Resource'}
        </span>
      </div>
      
      <h3 className={`font-semibold text-gray-900 mb-2 ${featured ? 'text-lg' : 'text-base'} line-clamp-2`}>
        {resource.title}
      </h3>
      
      {featured && (
        <p className="text-sm text-gray-600 mb-3 line-clamp-2">
          {resource.latest_version?.description || 'No description available'}
        </p>
      )}

      <div className="flex items-center gap-3 text-xs text-gray-500 mb-3">
        <span className="flex items-center gap-1">
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z" />
          </svg>
          {resource.vote_count || 0}
        </span>
        <span className="flex items-center gap-1">
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M7.217 10.907a2.25 2.25 0 100 2.186m0-2.186c.18.324.283.696.283 1.093s-.103.77-.283 1.093m0-2.186l9.566-5.314m-9.566 7.5l9.566 5.314m0 0a2.25 2.25 0 103.935 2.186 2.25 2.25 0 00-3.935-2.186zm0-12.814a2.25 2.25 0 103.933-2.185 2.25 2.25 0 00-3.933 2.185z" />
          </svg>
          {resource.reuse_count || 0}
        </span>
      </div>

      {/* Tags */}
      {resource.latest_version?.tags && resource.latest_version.tags.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {resource.latest_version.tags.slice(0, 3).map((tag: string, i: number) => (
            <span key={i} className="text-xs text-gray-600 bg-gray-100 px-2 py-1 rounded">
              {tag}
            </span>
          ))}
        </div>
      )}

      <div className="mt-3 pt-3 border-t border-gray-100 flex items-center gap-2 text-xs text-gray-500">
        <div className="w-6 h-6 bg-primary-600 rounded-full flex items-center justify-center text-white text-[10px] font-medium">
          {resource.owner_name?.[0]?.toUpperCase() || 'U'}
        </div>
        <span className="truncate">{resource.owner_name || 'Anonymous'}</span>
      </div>
    </Link>
  );
}
