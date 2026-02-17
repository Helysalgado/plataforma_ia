/**
 * ForkButton component
 * 
 * US-17: Reutilizar Recurso (Fork)
 * 
 * Features:
 * - Fork button with confirmation modal
 * - Redirect to edit page after fork
 * - Authentication required
 * - Loading state
 */

'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { interactionsApi } from '@/services/interactions';
import toast from 'react-hot-toast';

interface ForkButtonProps {
  resourceId: string;
  resourceTitle: string;
  onForkSuccess?: (newResourceId: string) => void;
}

export function ForkButton({
  resourceId,
  resourceTitle,
  onForkSuccess,
}: ForkButtonProps) {
  const router = useRouter();
  const { isAuthenticated } = useAuth();
  
  const [showModal, setShowModal] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFork = async () => {
    setLoading(true);
    setError(null);

    try {
      const newResource = await interactionsApi.fork(resourceId);
      
      // Success - close modal
      setShowModal(false);
      
      // Success toast
      toast.success('¡Recurso reutilizado! Ahora puedes editarlo.');
      
      // Notify parent
      if (onForkSuccess) {
        onForkSuccess(newResource.id);
      }
      
      // Redirect to edit page of new resource
      router.push(`/resources/${newResource.id}/edit`);
    } catch (error) {
      console.error('Fork error:', error);
      setError('Error al reutilizar recurso. Intenta de nuevo.');
    } finally {
      setLoading(false);
    }
  };

  const handleClick = () => {
    if (!isAuthenticated) {
      alert('Debes iniciar sesión para reutilizar recursos');
      return;
    }
    
    setShowModal(true);
  };

  return (
    <>
      {/* Fork button */}
      <button
        onClick={handleClick}
        disabled={!isAuthenticated}
        className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        title={!isAuthenticated ? 'Inicia sesión para reutilizar' : 'Reutilizar este recurso'}
      >
        <svg
          className="w-5 h-5"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
          />
        </svg>
        <span>Reutilizar</span>
      </button>

      {/* Confirmation Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            {/* Header */}
            <h3 className="text-xl font-bold text-gray-900 mb-2">
              Reutilizar recurso
            </h3>
            <p className="text-gray-600 mb-4">
              Vas a crear una copia de <strong>{resourceTitle}</strong> que podrás editar libremente.
            </p>

            {/* Info */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
              <p className="text-sm text-blue-800">
                <strong>¿Qué sucede al reutilizar?</strong>
              </p>
              <ul className="text-sm text-blue-700 mt-2 space-y-1 list-disc list-inside">
                <li>Se creará una copia completa del recurso</li>
                <li>Serás el propietario de la copia</li>
                <li>Podrás editarla sin afectar el original</li>
                <li>Se mantendrá la referencia al recurso original</li>
              </ul>
            </div>

            {/* Error */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4 text-red-800 text-sm">
                {error}
              </div>
            )}

            {/* Actions */}
            <div className="flex gap-3">
              <button
                onClick={() => setShowModal(false)}
                disabled={loading}
                className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 disabled:opacity-50 transition-colors"
              >
                Cancelar
              </button>
              <button
                onClick={handleFork}
                disabled={loading}
                className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 transition-colors"
              >
                {loading ? 'Reutilizando...' : 'Confirmar'}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
