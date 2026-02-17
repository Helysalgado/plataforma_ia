/**
 * Explore page - Main landing page
 * 
 * Displays grid of resources with filters and search
 * US-05: Explorar Recursos
 */

'use client';

import { useState, useEffect } from 'react';
import { resourcesApi } from '@/services/resources';
import { ResourceCard } from '@/components/ResourceCard';
import { ResourceCardSkeleton } from '@/components/Skeletons';
import type { Resource, ResourceFilters } from '@/types/api';

export default function ExplorePage() {
  const [resources, setResources] = useState<Resource[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<ResourceFilters>({
    page: 1,
    page_size: 12,
    ordering: '-created_at',
  });
  const [totalCount, setTotalCount] = useState(0);

  // Fetch resources
  useEffect(() => {
    const fetchResources = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await resourcesApi.list(filters);
        setResources(response.results);
        setTotalCount(response.count);
      } catch (err) {
        console.error('Error fetching resources:', err);
        setError('Error al cargar recursos. Por favor intenta de nuevo.');
      } finally {
        setLoading(false);
      }
    };

    fetchResources();
  }, [filters]);

  // Handle filter changes
  const handleFilterChange = (key: keyof ResourceFilters, value: string | number | undefined) => {
    setFilters(prev => ({
      ...prev,
      [key]: value,
      page: key !== 'page' ? 1 : prev.page, // Reset page when changing other filters
    }));
  };

  // Handle search
  const handleSearch = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const search = formData.get('search') as string;
    handleFilterChange('search', search || undefined);
  };

  // Clear filters
  const clearFilters = () => {
    setFilters({
      page: 1,
      page_size: 12,
      ordering: '-created_at',
    });
  };

  const hasActiveFilters = filters.type || filters.status || filters.tags || filters.search;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <h1 className="text-3xl font-bold text-gray-900">Explorar Recursos</h1>
          <p className="mt-2 text-gray-600">
            Descubre prompts, workflows, notebooks y más recursos de IA
          </p>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Filters Section */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
          {/* Search Bar */}
          <form onSubmit={handleSearch} className="mb-6">
            <div className="flex gap-2">
              <input
                type="text"
                name="search"
                placeholder="Buscar por título o descripción..."
                defaultValue={filters.search}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <button
                type="submit"
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Buscar
              </button>
            </div>
          </form>

          {/* Filter Buttons */}
          <div className="flex flex-wrap gap-4">
            {/* Type Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Tipo</label>
              <select
                value={filters.type || ''}
                onChange={(e) => handleFilterChange('type', e.target.value || undefined)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Todos</option>
                <option value="Prompt">Prompt</option>
                <option value="Workflow">Workflow</option>
                <option value="Notebook">Notebook</option>
                <option value="Dataset">Dataset</option>
                <option value="Tool">Tool</option>
                <option value="Other">Other</option>
              </select>
            </div>

            {/* Status Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Estado</label>
              <select
                value={filters.status || ''}
                onChange={(e) => handleFilterChange('status', e.target.value || undefined)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Todos</option>
                <option value="Sandbox">Sandbox</option>
                <option value="Pending Validation">Pending Validation</option>
                <option value="Validated">Validated</option>
              </select>
            </div>

            {/* Ordering */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Ordenar</label>
              <select
                value={filters.ordering || '-created_at'}
                onChange={(e) => handleFilterChange('ordering', e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="-created_at">Más recientes</option>
                <option value="created_at">Más antiguos</option>
                <option value="-votes_count">Más votados</option>
              </select>
            </div>

            {/* Clear Filters */}
            {hasActiveFilters && (
              <div className="flex items-end">
                <button
                  onClick={clearFilters}
                  className="px-4 py-2 text-gray-700 hover:text-gray-900 underline"
                >
                  Limpiar filtros
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Results Count */}
        <div className="mb-4">
          <p className="text-gray-600">
            {loading ? 'Cargando...' : `${totalCount} recursos encontrados`}
          </p>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[...Array(6)].map((_, i) => (
              <ResourceCardSkeleton key={i} />
            ))}
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800">
            {error}
          </div>
        )}

        {/* Empty State */}
        {!loading && !error && resources.length === 0 && (
          <div className="text-center py-12">
            <svg
              className="mx-auto h-12 w-12 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">No se encontraron recursos</h3>
            <p className="mt-1 text-sm text-gray-500">
              {hasActiveFilters ? 'Intenta ajustar los filtros' : 'Aún no hay recursos publicados'}
            </p>
          </div>
        )}

        {/* Resources Grid */}
        {!loading && !error && resources.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {resources.map((resource) => (
              <ResourceCard key={resource.id} resource={resource} />
            ))}
          </div>
        )}

        {/* Pagination */}
        {!loading && !error && totalCount > (filters.page_size || 12) && (
          <div className="mt-8 flex justify-center gap-2">
            <button
              onClick={() => handleFilterChange('page', Math.max(1, (filters.page || 1) - 1))}
              disabled={filters.page === 1}
              className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Anterior
            </button>
            <span className="px-4 py-2 text-gray-700">
              Página {filters.page || 1} de {Math.ceil(totalCount / (filters.page_size || 12))}
            </span>
            <button
              onClick={() => handleFilterChange('page', (filters.page || 1) + 1)}
              disabled={(filters.page || 1) >= Math.ceil(totalCount / (filters.page_size || 12))}
              className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Siguiente
            </button>
          </div>
        )}
      </main>
    </div>
  );
}
