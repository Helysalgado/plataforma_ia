/**
 * VoteButton component
 * 
 * US-16: Votar Recurso
 * 
 * Features:
 * - Toggle vote/unvote (single endpoint)
 * - Optimistic UI updates (instant feedback)
 * - Rollback on error
 * - Authentication required
 * - Visual states: not voted, voted, loading, disabled
 */

'use client';

import { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { interactionsApi } from '@/services/interactions';
import toast from 'react-hot-toast';

interface VoteButtonProps {
  resourceId: string;
  initialVotesCount: number;
  initialUserHasVoted?: boolean;
  onVoteChange?: (newCount: number, voted: boolean) => void;
}

export function VoteButton({
  resourceId,
  initialVotesCount,
  initialUserHasVoted = false,
  onVoteChange,
}: VoteButtonProps) {
  const { isAuthenticated } = useAuth();
  
  const [votesCount, setVotesCount] = useState(initialVotesCount);
  const [hasVoted, setHasVoted] = useState(initialUserHasVoted);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleVote = async () => {
    if (!isAuthenticated) {
      alert('Debes iniciar sesión para votar');
      return;
    }

    // Optimistic update
    const previousCount = votesCount;
    const previousVoted = hasVoted;
    
    const newVoted = !hasVoted;
    const newCount = newVoted ? votesCount + 1 : votesCount - 1;
    
    setHasVoted(newVoted);
    setVotesCount(newCount);
    setLoading(true);
    setError(null);

    try {
      const response = await interactionsApi.vote(resourceId);
      
      // Update with actual values from backend
      setVotesCount(response.votes_count);
      setHasVoted(response.voted);
      
      // Success toast
      toast.success(response.voted ? '¡Voto registrado!' : 'Voto retirado');
      
      // Notify parent component
      if (onVoteChange) {
        onVoteChange(response.votes_count, response.voted);
      }
    } catch (error) {
      console.error('Vote error:', error);
      
      // Rollback optimistic update
      setHasVoted(previousVoted);
      setVotesCount(previousCount);
      
      setError('Error al votar. Intenta de nuevo.');
      
      // Clear error after 3 seconds
      setTimeout(() => setError(null), 3000);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative">
      <button
        onClick={handleVote}
        disabled={loading || !isAuthenticated}
        className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${
          hasVoted
            ? 'bg-blue-600 text-white hover:bg-blue-700'
            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
        } disabled:opacity-50 disabled:cursor-not-allowed`}
        title={!isAuthenticated ? 'Inicia sesión para votar' : hasVoted ? 'Quitar voto' : 'Votar'}
      >
        {/* Icon */}
        <svg
          className="w-5 h-5"
          fill={hasVoted ? 'currentColor' : 'none'}
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M5 15l7-7 7 7"
          />
        </svg>
        
        {/* Count */}
        <span>{loading ? '...' : votesCount}</span>
        
        {/* Label */}
        <span className="hidden sm:inline">
          {hasVoted ? 'Votado' : 'Votar'}
        </span>
      </button>

      {/* Error tooltip */}
      {error && (
        <div className="absolute top-full mt-2 left-0 bg-red-100 border border-red-200 text-red-800 text-sm px-3 py-2 rounded-lg whitespace-nowrap z-10">
          {error}
        </div>
      )}
    </div>
  );
}
