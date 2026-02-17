/**
 * ResourceCard component
 * 
 * Displays a resource in a card format with:
 * - Title, description, type, status
 * - Tags, votes count, forks count
 * - Owner info
 * - Click to view detail
 */

import Link from 'next/link';
import { Resource } from '@/types/api';
import clsx from 'clsx';

interface ResourceCardProps {
  resource: Resource;
}

export function ResourceCard({ resource }: ResourceCardProps) {
  const { latest_version, votes_count, forks_count, owner_name, id } = resource;
  
  // Status badge color
  const statusColor = {
    'Sandbox': 'bg-gray-100 text-gray-800',
    'Pending Validation': 'bg-yellow-100 text-yellow-800',
    'Validated': 'bg-green-100 text-green-800',
  }[latest_version.status] || 'bg-gray-100 text-gray-800';
  
  // Type badge color
  const typeColor = {
    'Prompt': 'bg-blue-100 text-blue-800',
    'Workflow': 'bg-purple-100 text-purple-800',
    'Notebook': 'bg-orange-100 text-orange-800',
    'Dataset': 'bg-pink-100 text-pink-800',
    'Tool': 'bg-indigo-100 text-indigo-800',
    'Other': 'bg-gray-100 text-gray-800',
  }[latest_version.type] || 'bg-gray-100 text-gray-800';

  return (
    <Link href={`/resources/${id}`}>
      <div className="border border-gray-200 rounded-lg p-6 hover:shadow-lg transition-shadow duration-200 bg-white cursor-pointer h-full flex flex-col">
        {/* Header */}
        <div className="flex items-start justify-between mb-3">
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-gray-900 line-clamp-2 mb-1">
              {latest_version.title}
            </h3>
            <p className="text-sm text-gray-600">
              por <span className="font-medium">{owner_name}</span>
            </p>
          </div>
        </div>

        {/* Description */}
        <p className="text-sm text-gray-700 line-clamp-3 mb-4 flex-grow">
          {latest_version.description || 'Sin descripción'}
        </p>

        {/* Tags */}
        {latest_version.tags.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-4">
            {latest_version.tags.slice(0, 3).map((tag) => (
              <span
                key={tag}
                className="text-xs px-2 py-1 bg-gray-100 text-gray-700 rounded-full"
              >
                {tag}
              </span>
            ))}
            {latest_version.tags.length > 3 && (
              <span className="text-xs px-2 py-1 text-gray-500">
                +{latest_version.tags.length - 3}
              </span>
            )}
          </div>
        )}

        {/* Footer */}
        <div className="flex items-center justify-between pt-4 border-t border-gray-100">
          {/* Type and Status badges */}
          <div className="flex gap-2">
            <span className={clsx('text-xs px-2 py-1 rounded-full font-medium', typeColor)}>
              {latest_version.type}
            </span>
            <span className={clsx('text-xs px-2 py-1 rounded-full font-medium', statusColor)}>
              {latest_version.status}
            </span>
          </div>

          {/* Stats */}
          <div className="flex items-center gap-4 text-sm text-gray-600">
            <div className="flex items-center gap-1">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
              </svg>
              <span>{votes_count}</span>
            </div>
            <div className="flex items-center gap-1">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
              <span>{forks_count}</span>
            </div>
          </div>
        </div>
      </div>
    </Link>
  );
}
