/**
 * Edit resource page
 * 
 * US-20: Editar Recurso Propio con Versionado
 * 
 * Features:
 * - Requires authentication and ownership (or admin)
 * - Pre-fills form with current resource data
 * - Creates new version if latest is Validated
 * - Updates in-place if latest is Sandbox/Pending
 * - Shows banner explaining versioning behavior
 */

'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';
import { resourcesApi, type UpdateResourceRequest } from '@/services/resources';
import { ResourceForm } from '@/components/ResourceForm';
import type { Resource } from '@/types/api';
import toast from 'react-hot-toast';

export default function EditResourcePage() {
  const params = useParams();
  const router = useRouter();
  const resourceId = params.id as string;
  const { user, isAuthenticated, loading: authLoading } = useAuth();
  
  const [resource, setResource] = useState<Resource | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [unauthorized, setUnauthorized] = useState(false);

  // Fetch resource data
  useEffect(() => {
    const fetchResource = async () => {
      if (!authLoading && isAuthenticated) {
        try {
          setLoading(true);
          setError(null);
          const data = await resourcesApi.get(resourceId);
          
          // Check ownership
          if (data.owner_name !== user?.name && !user?.is_admin) {
            setUnauthorized(true);
            return;
          }
          
          setResource(data);
        } catch (err) {
          console.error('Error fetching resource:', err);
          setError('Error al cargar el recurso');
        } finally {
          setLoading(false);
        }
      }
    };

    fetchResource();
  }, [resourceId, isAuthenticated, authLoading, user]);

  // Redirect if not authenticated
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login?redirect=/resources/' + resourceId + '/edit');
    }
  }, [isAuthenticated, authLoading, router, resourceId]);

  const handleSubmit = async (data: UpdateResourceRequest) => {
    setSubmitting(true);
    setError(null);

    try {
      const updatedResource = await resourcesApi.update(resourceId, data);
      
      // Check if new version was created
      const isNewVersion = updatedResource.latest_version.version_number !== resource?.latest_version.version_number;
      
      // Success toast
      if (isNewVersion) {
        toast.success(`Nueva versión creada: v${updatedResource.latest_version.version_number}`);
      } else {
        toast.success('Recurso actualizado exitosamente');
      }
      
      // Redirect to resource detail with success message
      router.push(`/resources/${resourceId}?updated=true&new_version=${isNewVersion}`);
    } catch (error) {
      console.error('Update error:', error);
      
      const err = error as { response?: { data?: Record<string, unknown> } };
      if (err.response?.data) {
        const firstError = Object.values(err.response.data)[0];
        setError(Array.isArray(firstError) ? firstError[0] : String(firstError));
      } else {
        setError('Error al actualizar recurso. Intenta de nuevo.');
      }
      toast.error('Error al actualizar recurso');
    } finally {
      setSubmitting(false);
    }
  };

  // Loading state
  if (authLoading || loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  // Unauthorized state
  if (unauthorized) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <svg
            className="mx-auto h-12 w-12 text-red-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
            />
          </svg>
          <h2 className="mt-4 text-2xl font-bold text-gray-900">No autorizado</h2>
          <p className="mt-2 text-gray-600">
            Solo el propietario del recurso puede editarlo
          </p>
          <Link
            href={`/resources/${resourceId}`}
            className="mt-4 inline-block text-blue-600 hover:text-blue-700 underline"
          >
            Volver al recurso
          </Link>
        </div>
      </div>
    );
  }

  // Error state
  if (!resource && error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Error al cargar</h2>
          <p className="text-gray-600 mb-4">{error}</p>
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

  if (!resource) return null;

  const isValidated = resource.latest_version.status === 'Validated';

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <Link
            href={`/resources/${resourceId}`}
            className="text-blue-600 hover:text-blue-700 mb-4 inline-flex items-center gap-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Volver al Recurso
          </Link>
          <h1 className="text-3xl font-bold text-gray-900 mt-2">Editar Recurso</h1>
          <p className="mt-2 text-gray-600">
            {resource.latest_version.title}
          </p>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-lg shadow-sm p-8">
          {/* Versioning info banner */}
          {isValidated ? (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
              <p className="text-sm text-green-800 font-medium">
                📋 Versionado automático activado
              </p>
              <p className="text-sm text-green-700 mt-1">
                Como este recurso está <strong>Validated</strong>, al guardar cambios se creará una
                nueva versión (v{resource.latest_version.version_number} → v
                {resource.latest_version.version_number.replace(/(\d+)\.(\d+)\.(\d+)/, (_, major, minor, patch) => 
                  `${major}.${parseInt(minor) + 1}.${patch}`
                )}).
                La versión anterior permanecerá validada.
              </p>
            </div>
          ) : (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
              <p className="text-sm text-blue-800 font-medium">
                ✏️ Edición in-place
              </p>
              <p className="text-sm text-blue-700 mt-1">
                Como este recurso está en <strong>{resource.latest_version.status}</strong>, los
                cambios actualizarán la versión actual sin crear una nueva.
              </p>
            </div>
          )}

          {/* Error message */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6 text-red-800 text-sm">
              {error}
            </div>
          )}

          {/* Resource Form */}
          <ResourceForm
            mode="edit"
            initialData={resource}
            onSubmit={handleSubmit}
            loading={submitting}
          />
        </div>
      </main>
    </div>
  );
}
