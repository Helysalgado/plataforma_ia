/**
 * Interactions API service
 * 
 * Handles voting, forking, and notifications
 */

import { apiClient } from '@/lib/api-client';
import type { Resource, NotificationListResponse } from '@/types/api';

export const interactionsApi = {
  /**
   * Vote/Unvote a resource (toggle)
   */
  vote: async (resourceId: string): Promise<{ message: string; voted: boolean; votes_count: number }> => {
    const response = await apiClient.post(`/resources/${resourceId}/vote/`);
    return response.data;
  },

  /**
   * Fork (reuse) a resource
   */
  fork: async (resourceId: string): Promise<Resource> => {
    const response = await apiClient.post<Resource>(`/resources/${resourceId}/fork/`);
    return response.data;
  },

  /**
   * Get user notifications
   */
  getNotifications: async (): Promise<NotificationListResponse> => {
    const response = await apiClient.get<NotificationListResponse>('/notifications/');
    return response.data;
  },

  /**
   * Mark notification as read
   */
  markAsRead: async (notificationId: string): Promise<void> => {
    await apiClient.patch(`/notifications/${notificationId}/read/`);
  },

  /**
   * Mark all notifications as read
   */
  markAllAsRead: async (): Promise<void> => {
    await apiClient.post('/notifications/mark-all-read/');
  },
};
