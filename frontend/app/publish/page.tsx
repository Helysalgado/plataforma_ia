/**
 * Publish page - Create new resource
 * 
 * US-08: Publicar Nuevo Recurso (Internal)
 * 
 * Features:
 * - Requires authentication and email verification
 * - ResourceForm for content input
 * - Source type selection (Internal vs GitHub-linked)
 * - Status selection (Sandbox vs Request Validation)
 * - Redirect to resource detail after creation
 */

'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';
import { resourcesApi, type CreateResourceRequest } from '@/services/resources';
import { ResourceForm } from '@/components/ResourceForm';
import toast from 'react-hot-toast';

export default function PublishPage() {
  const router = useRouter();
  const { user, isAuthenticated, loading: authLoading } = useAuth();
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Redirect if not authenticated or email not verified
  useEffect(() => {
    if (!authLoading) {
      if (!isAuthenticated) {
        router.push('/login?redirect=/publish');
      } else if (!user?.email_verified_at) {
        router.push('/profile?message=verify_email_to_publish');
      }
    }
  }, [isAuthenticated, user, authLoading, router]);

  const handleSubmit = async (data: CreateResourceRequest) => {
    setLoading(true);
    setError(null);

    try {
      const newResource = await resourcesApi.create(data);
      
      // Success toast
      toast.success(
        data.status === 'Pending Validation'
          ? '¡Recurso publicado! Solicitud de validación enviada.'
          : '¡Recurso publicado exitosamente!'
      );
      
      // Success - redirect to resource detail
      router.push(`/resources/${newResource.id}?published=true`);
    } catch (error) {
      console.error('Publish error:', error);
      
      const err = error as { response?: { data?: Record<string, unknown>; detail?: string } };
      if (err.response?.data) {
        // Backend validation errors
        const firstError = Object.values(err.response.data)[0];
        setError(Array.isArray(firstError) ? firstError[0] : String(firstError));
      } else {
        setError('Error al publicar recurso. Intenta de nuevo.');
      }
      toast.error(err.response?.detail || 'Error al publicar recurso');
    } finally {
      setLoading(false);
    }
  };

  // Show loading while checking auth
  if (authLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  // Don't render if not authenticated (will redirect)
  if (!isAuthenticated || !user?.email_verified_at) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <Link
            href="/explore"
            className="text-blue-600 hover:text-blue-700 mb-4 inline-flex items-center gap-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Volver a Explorar
          </Link>
          <h1 className="text-3xl font-bold text-gray-900 mt-2">Publicar Recurso</h1>
          <p className="mt-2 text-gray-600">
            Comparte tu prompt, workflow, notebook u otro recurso de IA con la comunidad CCG
          </p>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-lg shadow-sm p-8">
          {/* Info banner */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <p className="text-sm text-blue-800">
              <strong>Consejos para publicar:</strong>
            </p>
            <ul className="text-sm text-blue-700 mt-2 space-y-1 list-disc list-inside">
              <li>Usa un título descriptivo y conciso</li>
              <li>Explica claramente el propósito y uso del recurso</li>
              <li>Agrega tags relevantes para facilitar la búsqueda</li>
              <li>Si solicitas validación, un admin revisará tu recurso</li>
            </ul>
          </div>

          {/* Error message */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6 text-red-800 text-sm">
              {error}
            </div>
          )}

          {/* Resource Form */}
          <ResourceForm
            mode="create"
            onSubmit={handleSubmit}
            loading={loading}
          />
        </div>
      </main>
    </div>
  );
}
