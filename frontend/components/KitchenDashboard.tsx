/**
 * Kitchen Dashboard Component
 * Manage special requests and kitchen operations
 */
'use client';

import { useQuery } from '@tanstack/react-query';
import { Clock, AlertCircle, CheckCircle, XCircle } from 'lucide-react';
import { api } from '@/lib/api';
import {
  formatRelativeTime,
  getPriorityColor,
  getPriorityLabel,
  getStatusColor,
  formatStatus,
  cn,
} from '@/lib/utils';

export function KitchenDashboard() {
  const { data, isLoading } = useQuery({
    queryKey: ['kitchen-dashboard'],
    queryFn: () => api.getKitchenDashboard(),
    refetchInterval: 30000, // Refetch every 30 seconds
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="loading-dots flex gap-2">
          <span className="w-3 h-3 bg-calo-primary rounded-full"></span>
          <span className="w-3 h-3 bg-calo-primary rounded-full"></span>
          <span className="w-3 h-3 bg-calo-primary rounded-full"></span>
        </div>
      </div>
    );
  }

  const stats = data?.statistics || {
    total_requests: 0,
    pending: 0,
    in_progress: 0,
    completed: 0,
  };

  const urgentRequests = data?.urgent_requests || [];
  const recentRequests = data?.recent_requests || [];

  return (
    <div className="space-y-6">
      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="card p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-blue-50 flex items-center justify-center">
              <Clock className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-calo-dark">{stats.total_requests}</p>
              <p className="text-xs text-gray-500">Total Requests</p>
            </div>
          </div>
        </div>

        <div className="card p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-yellow-50 flex items-center justify-center">
              <AlertCircle className="w-5 h-5 text-yellow-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-calo-dark">{stats.pending}</p>
              <p className="text-xs text-gray-500">Pending</p>
            </div>
          </div>
        </div>

        <div className="card p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-blue-50 flex items-center justify-center">
              <Clock className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-calo-dark">{stats.in_progress}</p>
              <p className="text-xs text-gray-500">In Progress</p>
            </div>
          </div>
        </div>

        <div className="card p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-green-50 flex items-center justify-center">
              <CheckCircle className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-calo-dark">{stats.completed}</p>
              <p className="text-xs text-gray-500">Completed</p>
            </div>
          </div>
        </div>
      </div>

      {/* Urgent Requests */}
      {urgentRequests.length > 0 && (
        <div className="card p-6">
          <h3 className="font-semibold text-lg text-calo-dark mb-4 flex items-center gap-2">
            <AlertCircle className="w-5 h-5 text-red-500" />
            Urgent Requests
          </h3>
          <div className="space-y-3">
            {urgentRequests.map((request) => (
              <div
                key={request.request_id}
                className="p-4 rounded-lg border-2 border-red-200 bg-red-50/50"
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className={cn('badge', getPriorityColor(request.priority))}>
                      {getPriorityLabel(request.priority)}
                    </span>
                    <span className={cn('badge', getStatusColor(request.status))}>
                      {formatStatus(request.status)}
                    </span>
                  </div>
                  <p className="text-xs text-gray-500">
                    {formatRelativeTime(request.created_at)}
                  </p>
                </div>
                <p className="text-sm text-calo-dark font-medium mb-1">
                  {request.request_type}
                </p>
                <p className="text-sm text-gray-600 line-clamp-2">
                  {request.original_message}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recent Requests */}
      <div className="card p-6">
        <h3 className="font-semibold text-lg text-calo-dark mb-4">
          Recent Requests
        </h3>
        <div className="space-y-3">
          {recentRequests.length === 0 ? (
            <p className="text-center text-gray-500 py-8">No requests yet</p>
          ) : (
            recentRequests.map((request) => (
              <div
                key={request.request_id}
                className="p-4 rounded-lg bg-gray-50 hover:bg-gray-100 transition-colors"
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className={cn('badge', getPriorityColor(request.priority))}>
                      {getPriorityLabel(request.priority)}
                    </span>
                    <span className={cn('badge', getStatusColor(request.status))}>
                      {formatStatus(request.status)}
                    </span>
                  </div>
                  <p className="text-xs text-gray-500">
                    {formatRelativeTime(request.created_at)}
                  </p>
                </div>
                <p className="text-sm text-calo-dark font-medium mb-1">
                  {request.request_type}
                </p>
                <p className="text-sm text-gray-600 line-clamp-2">
                  {request.original_message}
                </p>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
