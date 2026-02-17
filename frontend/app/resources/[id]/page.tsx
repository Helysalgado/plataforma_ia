/**
 * Resource detail page
 * 
 * Displays full information about a resource
 * US-07: Ver Detalle de Recurso
 */

'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { resourcesApi } from '@/services/resources';
import type { Resource } from '@/types/api';
import clsx from 'clsx';
import { VoteButton } from '@/components/VoteButton';
import { ForkButton } from '@/components/ForkButton';
import { useAuth } from '@/contexts/AuthContext';
import Link from 'next/link';

export default function ResourceDetailPage() {
  const params = useParams();
  const resourceId = params.id as string;
  const { isAuthenticated } = useAuth();
  
  const [resource, setResource] = useState<Resource | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [votesCount, setVotesCount] = useState(0);
  const [forksCount, setForksCount] = useState(0);

  useEffect(() => {
    const fetchResource = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await resourcesApi.get(resourceId);
        setResource(data);
        setVotesCount(data.votes_count);
        setForksCount(data.forks_count);
      } catch (err) {
        console.error('Error fetching resource:', err);
        setError('Error al cargar el recurso. Por favor intenta de nuevo.');
      } finally {
        setLoading(false);
      }
    };

    if (resourceId) {
      fetchResource();
    }
  }, [resourceId]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !resource) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Recurso no encontrado</h2>
          <p className="text-gray-600 mb-4">{error || 'El recurso no existe'}</p>
          <Link
            href="/explore"
            className="text-blue-600 hover:text-blue-700 underline"
          >
            Volver a Explorar
          </Link>
        </div>
      </div>
    );
  }

  const { latest_version, owner_name } = resource;

  const statusColor = {
    'Sandbox': 'bg-gray-100 text-gray-800',
    'Pending Validation': 'bg-yellow-100 text-yellow-800',
    'Validated': 'bg-green-100 text-green-800',
  }[latest_version.status] || 'bg-gray-100 text-gray-800';

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <Link
            href="/explore"
            className="text-blue-600 hover:text-blue-700 mb-4 inline-flex items-center gap-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Volver a Explorar
          </Link>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-lg shadow-sm p-8">
          {/* Title and badges */}
          <div className="mb-6">
            <div className="flex flex-wrap gap-2 mb-4">
              <span className="text-sm px-3 py-1 bg-blue-100 text-blue-800 rounded-full font-medium">
                {latest_version.type}
              </span>
              <span className={clsx('text-sm px-3 py-1 rounded-full font-medium', statusColor)}>
                {latest_version.status}
              </span>
              <span className="text-sm px-3 py-1 bg-gray-100 text-gray-600 rounded-full">
                v{latest_version.version_number}
              </span>
            </div>
            
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              {latest_version.title}
            </h1>
            
            <p className="text-gray-600">
              por <span className="font-medium">{owner_name}</span>
            </p>
          </div>

          {/* Description */}
          <div className="mb-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-2">Descripción</h2>
            <p className="text-gray-700 whitespace-pre-wrap">
              {latest_version.description || 'Sin descripción'}
            </p>
          </div>

          {/* Tags */}
          {latest_version.tags.length > 0 && (
            <div className="mb-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-2">Tags</h2>
              <div className="flex flex-wrap gap-2">
                {latest_version.tags.map((tag) => (
                  <span
                    key={tag}
                    className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Stats */}
          <div className="flex items-center gap-8 py-4 border-t border-gray-200">
            <div className="flex items-center gap-2">
              <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
              </svg>
              <span className="text-gray-700 font-medium">{votesCount} votos</span>
            </div>
            <div className="flex items-center gap-2">
              <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
              <span className="text-gray-700 font-medium">{forksCount} forks</span>
            </div>
          </div>

          {/* Actions */}
          <div className="flex flex-wrap gap-4 pt-4 border-t border-gray-200">
            <VoteButton
              resourceId={resourceId}
              initialVotesCount={votesCount}
              initialUserHasVoted={false}
              onVoteChange={(newCount) => setVotesCount(newCount)}
            />
            <ForkButton
              resourceId={resourceId}
              resourceTitle={latest_version.title}
              onForkSuccess={() => setForksCount(prev => prev + 1)}
            />
            
            {/* Owner/Admin actions */}
            {isAuthenticated && (user?.name === resource.owner_name || user?.is_admin) && (
              <>
                <Link
                  href={`/resources/${resourceId}/edit`}
                  className="flex items-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg font-medium hover:bg-gray-200 transition-colors"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                  <span>Editar</span>
                </Link>
              </>
            )}
          </div>

          {/* PID */}
          <div className="mt-6 pt-4 border-t border-gray-200">
            <p className="text-sm text-gray-600">
              <span className="font-medium">PID:</span> {latest_version.pid}
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
