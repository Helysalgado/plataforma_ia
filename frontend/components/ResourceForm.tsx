/**
 * ResourceForm component
 * 
 * Reusable form for creating and editing resources
 * Used by /publish and /resources/[id]/edit
 * 
 * Features:
 * - Validation (title, description, type, tags, content)
 * - Source type selection (Internal vs GitHub-linked)
 * - Dynamic fields based on source_type
 * - Tags input with comma separation
 * - Status selection (Sandbox vs Request Validation)
 */

'use client';

import { useState } from 'react';
import type { CreateResourceRequest, UpdateResourceRequest } from '@/services/resources';
import type { Resource } from '@/types/api';

interface ResourceFormProps {
  mode: 'create' | 'edit';
  initialData?: Partial<Resource>;
  onSubmit: (data: CreateResourceRequest | UpdateResourceRequest) => Promise<void>;
  loading: boolean;
}

const RESOURCE_TYPES = ['Prompt', 'Workflow', 'Notebook', 'Dataset', 'Tool', 'Other'] as const;

export function ResourceForm({ mode, initialData, onSubmit, loading }: ResourceFormProps) {
  const [formData, setFormData] = useState({
    title: initialData?.latest_version?.title || '',
    description: initialData?.latest_version?.description || '',
    type: initialData?.latest_version?.type || 'Prompt' as const,
    source_type: mode === 'create' ? ('Internal' as const) : initialData?.source_type || 'Internal' as const,
    tags: initialData?.latest_version?.tags?.join(', ') || '',
    content: initialData?.latest_version?.content || '',
    example: initialData?.latest_version?.example || '',
    repo_url: '',
    repo_branch: '',
    status: 'Sandbox' as const,
    changelog: mode === 'edit' ? '' : undefined,
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  // Client-side validation
  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    // Title validation
    if (!formData.title || formData.title.trim().length < 3) {
      newErrors.title = 'El título debe tener al menos 3 caracteres';
    } else if (formData.title.length > 200) {
      newErrors.title = 'El título no puede exceder 200 caracteres';
    }

    // Description validation
    if (!formData.description || formData.description.trim().length < 10) {
      newErrors.description = 'La descripción debe tener al menos 10 caracteres';
    }

    // Source-specific validations
    if (formData.source_type === 'Internal') {
      if (!formData.content || formData.content.trim().length < 10) {
        newErrors.content = 'El contenido debe tener al menos 10 caracteres';
      }
    } else if (formData.source_type === 'GitHub-linked') {
      if (!formData.repo_url || !formData.repo_url.match(/^https:\/\/github\.com\/.+\/.+/)) {
        newErrors.repo_url = 'URL de GitHub inválida (ejemplo: https://github.com/user/repo)';
      }
    }

    // Tags validation (optional but format check)
    if (formData.tags) {
      const tags = formData.tags.split(',').map(t => t.trim()).filter(t => t.length > 0);
      if (tags.some(tag => tag.length > 50)) {
        newErrors.tags = 'Cada tag debe tener máximo 50 caracteres';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    // Parse tags
    const tagsArray = formData.tags
      .split(',')
      .map(t => t.trim())
      .filter(t => t.length > 0);

    // Prepare data based on mode
    if (mode === 'create') {
      const createData: CreateResourceRequest = {
        title: formData.title,
        description: formData.description,
        type: formData.type,
        source_type: formData.source_type,
        tags: tagsArray,
        status: formData.status,
      };

      if (formData.source_type === 'Internal') {
        createData.content = formData.content;
        createData.example = formData.example || undefined;
      } else {
        createData.repo_url = formData.repo_url;
        createData.repo_branch = formData.repo_branch || undefined;
      }

      await onSubmit(createData);
    } else {
      const updateData: UpdateResourceRequest = {
        title: formData.title,
        description: formData.description,
        type: formData.type,
        tags: tagsArray,
        content: formData.content || undefined,
        example: formData.example || undefined,
        changelog: formData.changelog || undefined,
      };

      await onSubmit(updateData);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));
    // Clear error for this field
    if (errors[e.target.name]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[e.target.name];
        return newErrors;
      });
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Title */}
      <div>
        <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-2">
          Título *
        </label>
        <input
          type="text"
          id="title"
          name="title"
          value={formData.title}
          onChange={handleChange}
          className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
            errors.title ? 'border-red-500' : 'border-gray-300'
          }`}
          placeholder="ej: Protein Folding Prompt for AlphaFold"
          disabled={loading}
        />
        {errors.title && (
          <p className="mt-1 text-sm text-red-600">{errors.title}</p>
        )}
      </div>

      {/* Description */}
      <div>
        <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
          Descripción *
        </label>
        <textarea
          id="description"
          name="description"
          value={formData.description}
          onChange={handleChange}
          rows={3}
          className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
            errors.description ? 'border-red-500' : 'border-gray-300'
          }`}
          placeholder="Describe el propósito y uso de este recurso..."
          disabled={loading}
        />
        {errors.description && (
          <p className="mt-1 text-sm text-red-600">{errors.description}</p>
        )}
      </div>

      {/* Type */}
      <div>
        <label htmlFor="type" className="block text-sm font-medium text-gray-700 mb-2">
          Tipo *
        </label>
        <select
          id="type"
          name="type"
          value={formData.type}
          onChange={handleChange}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          disabled={loading}
        >
          {RESOURCE_TYPES.map(type => (
            <option key={type} value={type}>{type}</option>
          ))}
        </select>
      </div>

      {/* Source Type (only for create) */}
      {mode === 'create' && (
        <div>
          <label htmlFor="source_type" className="block text-sm font-medium text-gray-700 mb-2">
            Tipo de fuente *
          </label>
          <select
            id="source_type"
            name="source_type"
            value={formData.source_type}
            onChange={handleChange}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={loading}
          >
            <option value="Internal">Internal (contenido en la plataforma)</option>
            <option value="GitHub-linked">GitHub-linked (enlace a repositorio)</option>
          </select>
        </div>
      )}

      {/* Tags */}
      <div>
        <label htmlFor="tags" className="block text-sm font-medium text-gray-700 mb-2">
          Tags (separados por comas)
        </label>
        <input
          type="text"
          id="tags"
          name="tags"
          value={formData.tags}
          onChange={handleChange}
          className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
            errors.tags ? 'border-red-500' : 'border-gray-300'
          }`}
          placeholder="ej: protein, folding, AlphaFold"
          disabled={loading}
        />
        {errors.tags && (
          <p className="mt-1 text-sm text-red-600">{errors.tags}</p>
        )}
        <p className="mt-1 text-xs text-gray-500">
          Ayudan a otros usuarios a encontrar tu recurso
        </p>
      </div>

      {/* Internal Content */}
      {(formData.source_type === 'Internal' || mode === 'edit') && (
        <>
          <div>
            <label htmlFor="content" className="block text-sm font-medium text-gray-700 mb-2">
              Contenido * {mode === 'edit' && '(editar contenido)'}
            </label>
            <textarea
              id="content"
              name="content"
              value={formData.content}
              onChange={handleChange}
              rows={10}
              className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm ${
                errors.content ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="Escribe el contenido de tu recurso (prompt, código, pasos, etc.)..."
              disabled={loading}
            />
            {errors.content && (
              <p className="mt-1 text-sm text-red-600">{errors.content}</p>
            )}
          </div>

          <div>
            <label htmlFor="example" className="block text-sm font-medium text-gray-700 mb-2">
              Ejemplo (opcional)
            </label>
            <textarea
              id="example"
              name="example"
              value={formData.example}
              onChange={handleChange}
              rows={5}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
              placeholder="Ejemplo de uso o output esperado..."
              disabled={loading}
            />
          </div>
        </>
      )}

      {/* GitHub Fields */}
      {mode === 'create' && formData.source_type === 'GitHub-linked' && (
        <>
          <div>
            <label htmlFor="repo_url" className="block text-sm font-medium text-gray-700 mb-2">
              URL del repositorio *
            </label>
            <input
              type="url"
              id="repo_url"
              name="repo_url"
              value={formData.repo_url}
              onChange={handleChange}
              className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                errors.repo_url ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="https://github.com/username/repository"
              disabled={loading}
            />
            {errors.repo_url && (
              <p className="mt-1 text-sm text-red-600">{errors.repo_url}</p>
            )}
          </div>

          <div>
            <label htmlFor="repo_branch" className="block text-sm font-medium text-gray-700 mb-2">
              Branch (opcional)
            </label>
            <input
              type="text"
              id="repo_branch"
              name="repo_branch"
              value={formData.repo_branch}
              onChange={handleChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="main"
              disabled={loading}
            />
          </div>
        </>
      )}

      {/* Changelog (only for edit) */}
      {mode === 'edit' && (
        <div>
          <label htmlFor="changelog" className="block text-sm font-medium text-gray-700 mb-2">
            Changelog (opcional)
          </label>
          <textarea
            id="changelog"
            name="changelog"
            value={formData.changelog || ''}
            onChange={handleChange}
            rows={3}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Describe los cambios realizados en esta versión..."
            disabled={loading}
          />
          <p className="mt-1 text-xs text-gray-500">
            Aparecerá en el historial de versiones
          </p>
        </div>
      )}

      {/* Status (only for create) */}
      {mode === 'create' && (
        <div>
          <label htmlFor="status" className="block text-sm font-medium text-gray-700 mb-2">
            Estado inicial
          </label>
          <select
            id="status"
            name="status"
            value={formData.status}
            onChange={handleChange}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={loading}
          >
            <option value="Sandbox">Sandbox (publicar sin validación)</option>
            <option value="Pending Validation">Request Validation (solicitar revisión de Admin)</option>
          </select>
          <p className="mt-1 text-xs text-gray-500">
            {formData.status === 'Sandbox'
              ? 'El recurso será visible pero sin badge de validación institucional'
              : 'Se notificará a los admins para revisar y validar tu recurso'}
          </p>
        </div>
      )}

      {/* Submit button */}
      <div className="flex gap-4">
        <button
          type="submit"
          disabled={loading}
          className="flex-1 py-3 px-6 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? 'Guardando...' : mode === 'create' ? 'Publicar Recurso' : 'Guardar Cambios'}
        </button>
      </div>
    </form>
  );
}
