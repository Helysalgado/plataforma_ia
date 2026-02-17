/**
 * Profile Page
 * Based on Figma design (docs/ux/figma/profile.png)
 * 
 * Features:
 * - User avatar with initials
 * - User badge (Contributor/Core Maintainer)
 * - Reputation score with progress bar
 * - Metrics dashboard (Contributions, Validations Made, Total Impact)
 * - Published resources grid
 */

'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';
import { usersApi, type UserProfile } from '@/services/users';
import type { Resource } from '@/types/api';

export default function ProfilePage() {
  const params = useParams();
  const router = useRouter();
  const { user: currentUser } = useAuth();
  
  // If no userId in params, use current user's ID
  const userId = (params.id as string) || currentUser?.id;
  
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [resources, setResources] = useState<Resource[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!userId) {
      router.push('/login');
      return;
    }
    loadProfile();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [userId]);

  const loadProfile = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [profileData, resourcesData] = await Promise.all([
        usersApi.getProfile(userId!),
        usersApi.getResources(userId!, { page_size: 12 })
      ]);
      
      setProfile(profileData);
      setResources(resourcesData.results);
    } catch (err) {
      console.error('Error loading profile:', err);
      setError('Error loading profile. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Get user initials for avatar
  const getUserInitials = () => {
    if (!profile?.name) return 'U';
    const parts = profile.name.split(' ');
    if (parts.length >= 2) {
      return parts[0][0] + parts[1][0];
    }
    return profile.name.slice(0, 2);
  };

  // Calculate progress to next level (reputation)
  const getProgressPercentage = () => {
    if (!profile) return 0;
    const reputation = profile.metrics.total_impact;
    const currentLevel = Math.floor(reputation / 500);
    const nextLevel = (currentLevel + 1) * 500;
    const progressInLevel = reputation % 500;
    return (progressInLevel / 500) * 100;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (error || !profile) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">User not found</h2>
          <p className="text-gray-600 mb-4">{error || 'This user does not exist'}</p>
          <Link href="/" className="text-primary-600 hover:text-primary-700 underline">
            Back to Home
          </Link>
        </div>
      </div>
    );
  }

  const isOwnProfile = currentUser?.id === userId;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Back Button */}
      <div className="bg-white px-6 py-4 border-b border-gray-200">
        <div className="max-w-6xl mx-auto">
          <Link
            href="/"
            className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18" />
            </svg>
            <span className="text-sm">Back to Dashboard</span>
          </Link>
        </div>
      </div>

      {/* Profile Header */}
      <div className="bg-white px-6 py-8 border-b border-gray-200">
        <div className="max-w-6xl mx-auto">
          <div className="flex items-start gap-6">
            {/* Avatar */}
            <div className="w-24 h-24 bg-primary-600 rounded-full flex items-center justify-center text-white text-3xl font-bold flex-shrink-0">
              {getUserInitials()}
            </div>

            {/* User Info */}
            <div className="flex-1">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">{profile.name}</h1>
              <div className="flex items-center gap-3 mb-4">
                <span className="text-sm text-gray-600 bg-gray-100 px-3 py-1 rounded">
                  👤 Contributor
                </span>
                <span className="text-sm text-primary-600 font-medium">
                  🏆 {profile.metrics.total_impact} Reputation
                </span>
              </div>

              {/* Progress to next level */}
              <div className="mb-4">
                <div className="flex items-center justify-between text-sm text-gray-600 mb-1">
                  <span>Progress to next level</span>
                  <span>{profile.metrics.total_impact} / {Math.ceil(profile.metrics.total_impact / 500) * 500}</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-primary-600 h-2 rounded-full transition-all"
                    style={{ width: `${getProgressPercentage()}%` }}
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Metrics Dashboard */}
      <div className="bg-white px-6 py-8 border-b border-gray-200">
        <div className="max-w-6xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Contributions */}
            <div className="text-center p-6 bg-gray-50 rounded-lg">
              <div className="w-12 h-12 mx-auto mb-3 flex items-center justify-center">
                <svg className="w-10 h-10 text-gray-400" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
                </svg>
              </div>
              <div className="text-3xl font-bold text-gray-900">{profile.metrics.total_resources}</div>
              <div className="text-sm text-gray-600 mt-1">Contributions</div>
            </div>

            {/* Validations Made */}
            <div className="text-center p-6 bg-gray-50 rounded-lg">
              <div className="w-12 h-12 mx-auto mb-3 flex items-center justify-center">
                <svg className="w-10 h-10 text-gray-400" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12c0 1.268-.63 2.39-1.593 3.068a3.745 3.745 0 01-1.043 3.296 3.745 3.745 0 01-3.296 1.043A3.745 3.745 0 0112 21c-1.268 0-2.39-.63-3.068-1.593a3.746 3.746 0 01-3.296-1.043 3.745 3.745 0 01-1.043-3.296A3.745 3.745 0 013 12c0-1.268.63-2.39 1.593-3.068a3.745 3.745 0 011.043-3.296 3.746 3.746 0 013.296-1.043A3.746 3.746 0 0112 3c1.268 0 2.39.63 3.068 1.593a3.746 3.746 0 013.296 1.043 3.746 3.746 0 011.043 3.296A3.745 3.745 0 0121 12z" />
                </svg>
              </div>
              <div className="text-3xl font-bold text-gray-900">{profile.metrics.validated_resources}</div>
              <div className="text-sm text-gray-600 mt-1">Validations Made</div>
            </div>

            {/* Total Impact */}
            <div className="text-center p-6 bg-gray-50 rounded-lg">
              <div className="w-12 h-12 mx-auto mb-3 flex items-center justify-center">
                <svg className="w-10 h-10 text-gray-400" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 18L9 11.25l4.306 4.307a11.95 11.95 0 015.814-5.519l2.74-1.22m0 0l-5.94-2.28m5.94 2.28l-2.28 5.941" />
                </svg>
              </div>
              <div className="text-3xl font-bold text-gray-900">{profile.metrics.total_impact}</div>
              <div className="text-sm text-gray-600 mt-1">Total Impact</div>
            </div>
          </div>
        </div>
      </div>

      {/* Published Resources */}
      <div className="max-w-6xl mx-auto px-6 py-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Published Resources</h2>
        
        {resources.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {resources.map((resource) => (
              <Link
                key={resource.id}
                href={`/resources/${resource.id}`}
                className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-lg hover:border-primary-300 transition-all"
              >
                <div className="flex items-start justify-between mb-3">
                  <span className={`px-2 py-1 text-xs font-medium rounded ${
                    resource.latest_version?.status === 'Validated'
                      ? 'bg-green-100 text-green-700'
                      : 'bg-gray-100 text-gray-700'
                  }`}>
                    {resource.latest_version?.status === 'Validated' ? '✓ Validated' : 'Sandbox'}
                  </span>
                  <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                    {resource.latest_version?.resource_type || 'Resource'}
                  </span>
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-2">
                  {resource.title}
                </h3>
                <div className="flex items-center gap-3 text-xs text-gray-500 mt-4">
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
              </Link>
            ))}
          </div>
        ) : (
          <div className="text-center py-16 bg-white rounded-lg border border-gray-200">
            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-gray-400" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              {isOwnProfile ? "You haven't published any resources yet" : `${profile.name} hasn't published any resources`}
            </h3>
            {isOwnProfile && (
              <>
                <p className="text-gray-600 mb-4">
                  Share your AI resources with the community!
                </p>
                <Link
                  href="/publish"
                  className="inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
                >
                  Publish Your First Resource
                </Link>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
