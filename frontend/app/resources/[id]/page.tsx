/**
 * Resource Detail Page
 * Based on Figma design (docs/ux/figma/resource-detail.png)
 * 
 * Features:
 * - Clean header with back button
 * - Author badge with "Core Maintainer" label
 * - Metrics dashboard (Uses, Votes, Validations)
 * - Action buttons (Reuse, Upvote)
 * - Tabs for Description, Notebook, Versions, Discussion
 */

'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';
import { resourcesService } from '@/services/resources';
import { VoteButton } from '@/components/VoteButton';
import { ForkButton } from '@/components/ForkButton';
import type { Resource } from '@/types/api';

export default function ResourceDetailPage() {
  const params = useParams();
  const router = useRouter();
  const resourceId = params.id as string;
  const { isAuthenticated, user } = useAuth();
  
  const [resource, setResource] = useState<Resource | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'description' | 'notebook' | 'versions' | 'discussion'>('description');

  useEffect(() => {
    loadResource();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [resourceId]);

  const loadResource = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await resourcesService.get(resourceId);
      setResource(data);
    } catch (err) {
      console.error('Error fetching resource:', err);
      setError('Error loading resource. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (error || !resource) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Resource not found</h2>
          <p className="text-gray-600 mb-4">{error || 'This resource does not exist'}</p>
          <Link
            href="/explore"
            className="text-primary-600 hover:text-primary-700 underline"
          >
            Back to Explore
          </Link>
        </div>
      </div>
    );
  }

  const { latest_version, owner_name } = resource;
  const isOwner = user?.id === resource.owner;
  const canEdit = isOwner || user?.is_admin;

  const getStatusBadge = () => {
    const status = latest_version?.status;
    if (status === 'Validated') {
      return <span className="px-3 py-1 bg-green-100 text-green-700 text-sm font-medium rounded">✓ Validated</span>;
    } else if (status === 'Pending Validation') {
      return <span className="px-3 py-1 bg-amber-100 text-amber-700 text-sm font-medium rounded">Pending</span>;
    }
    return <span className="px-3 py-1 bg-gray-100 text-gray-700 text-sm font-medium rounded">Sandbox</span>;
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header with Back Button */}
      <div className="bg-white px-6 py-4 border-b border-gray-200">
        <div className="max-w-5xl mx-auto">
          <Link
            href="/explore"
            className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18" />
            </svg>
            <span className="text-sm">Back to Dashboard</span>
          </Link>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-5xl mx-auto px-6 py-8">
        <div className="bg-white rounded-lg shadow-sm p-8">
          {/* Title & Badge */}
          <div className="flex items-start justify-between mb-4">
            <div className="flex-1">
              <h1 className="text-3xl font-bold text-gray-900 mb-3">
                {resource.title}
              </h1>
              <p className="text-gray-600 leading-relaxed">
                {latest_version?.description || 'No description available'}
              </p>
            </div>
            <div className="ml-6">
              {getStatusBadge()}
            </div>
          </div>

          {/* Tags */}
          {latest_version?.tags && latest_version.tags.length > 0 && (
            <div className="flex flex-wrap gap-2 mb-6">
              {latest_version.tags.map((tag: string, i: number) => (
                <span key={i} className="px-3 py-1 bg-gray-100 text-gray-600 text-sm rounded">
                  {tag}
                </span>
              ))}
            </div>
          )}

          {/* Author Badge */}
          <div className="flex items-center gap-3 mb-6 pb-6 border-b border-gray-200">
            <div className="w-12 h-12 bg-primary-600 rounded-full flex items-center justify-center text-white font-medium">
              {owner_name?.[0]?.toUpperCase() || 'U'}
            </div>
            <div>
              <div className="font-semibold text-gray-900">{owner_name || 'Anonymous'}</div>
              <div className="text-sm text-primary-600 font-medium">Core Maintainer [#360]</div>
            </div>
            {latest_version?.repo_url && (
              <Link
                href={latest_version.repo_url}
                target="_blank"
                rel="noopener noreferrer"
                className="ml-auto px-3 py-1 border border-gray-300 rounded text-sm text-gray-700 hover:bg-gray-50 inline-flex items-center gap-1"
              >
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                </svg>
                View on GitHub
              </Link>
            )}
          </div>

          {/* Metrics Dashboard */}
          <div className="grid grid-cols-3 gap-6 mb-8 pb-8 border-b border-gray-200">
            <div className="text-center">
              <div className="w-12 h-12 mx-auto mb-2 flex items-center justify-center">
                <svg className="w-8 h-8 text-gray-400" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z" />
                  <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </div>
              <div className="text-2xl font-bold text-gray-900">{resource.reuse_count || 0}</div>
              <div className="text-sm text-gray-600">Uses</div>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 mx-auto mb-2 flex items-center justify-center">
                <svg className="w-8 h-8 text-gray-400" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z" />
                </svg>
              </div>
              <div className="text-2xl font-bold text-gray-900">{resource.vote_count || 0}</div>
              <div className="text-sm text-gray-600">Votes</div>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 mx-auto mb-2 flex items-center justify-center">
                <svg className="w-8 h-8 text-gray-400" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div className="text-2xl font-bold text-gray-900">
                {latest_version?.status === 'Validated' ? '1' : '0'}
              </div>
              <div className="text-sm text-gray-600">Validations</div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center gap-3 mb-8">
            <ForkButton resourceId={resourceId} />
            <VoteButton resourceId={resourceId} />
            {canEdit && (
              <Link
                href={`/resources/${resourceId}/edit`}
                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 inline-flex items-center gap-2"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.13-1.897l8.932-8.931zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0115.75 21H5.25A2.25 2.25 0 013 18.75V8.25A2.25 2.25 0 015.25 6H10" />
                </svg>
                Edit
              </Link>
            )}
          </div>

          {/* Tabs */}
          <div className="border-b border-gray-200 mb-6">
            <nav className="-mb-px flex gap-8">
              {(['description', 'notebook', 'versions', 'discussion'] as const).map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`py-2 px-1 border-b-2 font-medium text-sm transition-colors ${
                    activeTab === tab
                      ? 'border-primary-600 text-primary-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  {tab.charAt(0).toUpperCase() + tab.slice(1)}
                </button>
              ))}
            </nav>
          </div>

          {/* Tab Content */}
          <div className="py-4">
            {activeTab === 'description' && (
              <div>
                <h2 className="text-lg font-semibold text-gray-900 mb-4">About This Resource</h2>
                <div className="prose max-w-none text-gray-700">
                  <p className="whitespace-pre-wrap">
                    {latest_version?.description || 'No detailed description available.'}
                  </p>
                  
                  {latest_version?.example_usage && (
                    <div className="mt-6">
                      <h3 className="text-base font-semibold text-gray-900 mb-2">Example Usage</h3>
                      <pre className="bg-gray-50 p-4 rounded-lg overflow-x-auto text-sm">
                        <code>{latest_version.example_usage}</code>
                      </pre>
                    </div>
                  )}

                  {latest_version?.content && (
                    <div className="mt-6">
                      <h3 className="text-base font-semibold text-gray-900 mb-2">Content</h3>
                      <pre className="bg-gray-50 p-4 rounded-lg overflow-x-auto text-sm max-h-96">
                        <code>{latest_version.content}</code>
                      </pre>
                    </div>
                  )}
                </div>
              </div>
            )}

            {activeTab === 'notebook' && (
              <div className="text-center py-12 text-gray-500">
                <svg className="w-16 h-16 mx-auto mb-4 text-gray-300" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25" />
                </svg>
                <p>Notebook viewer coming soon</p>
                {latest_version?.repo_url && (
                  <Link
                    href={latest_version.repo_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-block mt-2 text-primary-600 hover:underline"
                  >
                    View on GitHub
                  </Link>
                )}
              </div>
            )}

            {activeTab === 'versions' && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Version History</h3>
                <div className="space-y-4">
                  <div className="flex items-start gap-4 p-4 bg-gray-50 rounded-lg">
                    <div className="flex-shrink-0 w-16 text-center">
                      <div className="text-sm font-medium text-gray-900">
                        v{latest_version?.version_number || '1.0.0'}
                      </div>
                      <div className="text-xs text-gray-500 mt-1">Latest</div>
                    </div>
                    <div className="flex-1">
                      <div className="font-medium text-gray-900 mb-1">Current version</div>
                      <p className="text-sm text-gray-600">
                        {latest_version?.changelog || 'Initial release'}
                      </p>
                      <div className="mt-2 text-xs text-gray-500">
                        {new Date(latest_version?.created_at || '').toLocaleDateString('en-US', {
                          year: 'numeric',
                          month: 'long',
                          day: 'numeric',
                        })}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'discussion' && (
              <div className="text-center py-12 text-gray-500">
                <svg className="w-16 h-16 mx-auto mb-4 text-gray-300" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M20.25 8.511c.884.284 1.5 1.128 1.5 2.097v4.286c0 1.136-.847 2.1-1.98 2.193-.34.027-.68.052-1.02.072v3.091l-3-3c-1.354 0-2.694-.055-4.02-.163a2.115 2.115 0 01-.825-.242m9.345-8.334a2.126 2.126 0 00-.476-.095 48.64 48.64 0 00-8.048 0c-1.131.094-1.976 1.057-1.976 2.192v4.286c0 .837.46 1.58 1.155 1.951m9.345-8.334V6.637c0-1.621-1.152-3.026-2.76-3.235A48.455 48.455 0 0011.25 3c-2.115 0-4.198.137-6.24.402-1.608.209-2.760 1.614-2.760 3.235v6.226c0 1.621 1.152 3.026 2.760 3.235.577.075 1.157.14 1.74.194V21l4.155-4.155" />
                </svg>
                <p>Discussions coming soon</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
