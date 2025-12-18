/**
 * Analytics Panel Component
 * Feedback analysis and insights visualization
 */
'use client';

import { useQuery } from '@tanstack/react-query';
import { TrendingUp, TrendingDown, Star } from 'lucide-react';
import { api } from '@/lib/api';
import { cn, getSentimentEmoji } from '@/lib/utils';
import { ErrorState } from './ErrorState';

export const AnalyticsPanel = () => {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['analytics-summary'],
    queryFn: () => api.getAnalyticsSummary({ days: 30 }),
  });

  if (isLoading) {
    return (
      <div
        className="flex items-center justify-center h-64"
        role="status"
        aria-label="Loading analytics"
      >
        <div className="loading-dots flex gap-2" aria-hidden="true">
          <span className="w-3 h-3 bg-calo-primary rounded-full"></span>
          <span className="w-3 h-3 bg-calo-primary rounded-full"></span>
          <span className="w-3 h-3 bg-calo-primary rounded-full"></span>
        </div>
        <span className="sr-only">Loading analytics...</span>
      </div>
    );
  }

  if (error) {
    return (
      <ErrorState
        message={error instanceof Error ? error.message : 'Failed to load analytics'}
        onRetry={() => refetch()}
      />
    );
  }

  const defaultSummary = {
    total_feedback: 0,
    average_rating: 0,
    sentiment_breakdown: { positive: 0, neutral: 0, negative: 0 },
    top_complaints: [] as string[],
    top_praises: [] as string[],
    popular_meals: [] as string[],
    action_items: [] as string[],
    time_period: 'Last 30 days',
  };

  const summary = {
    ...defaultSummary,
    ...data,
    sentiment_breakdown: {
      ...defaultSummary.sentiment_breakdown,
      ...data?.sentiment_breakdown,
    },
  };

  const totalSentiments =
    summary.sentiment_breakdown.positive +
    summary.sentiment_breakdown.neutral +
    summary.sentiment_breakdown.negative;

  return (
    <div className="space-y-6">
      {/* Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Total Feedback */}
        <div className="card p-6">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm text-gray-500">Total Feedback</p>
            <TrendingUp className="w-5 h-5 text-calo-primary" />
          </div>
          <p className="text-3xl font-bold text-calo-dark">{summary.total_feedback}</p>
          <p className="text-xs text-gray-500 mt-1">{summary.time_period}</p>
        </div>

        {/* Average Rating */}
        <div className="card p-6">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm text-gray-500">Average Rating</p>
            <Star className="w-5 h-5 text-calo-secondary fill-current" />
          </div>
          <div className="flex items-baseline gap-2">
            <p className="text-3xl font-bold text-calo-dark">
              {summary.average_rating.toFixed(1)}
            </p>
            <p className="text-sm text-gray-500">/ 5.0</p>
          </div>
          <div className="flex gap-1 mt-2">
            {[1, 2, 3, 4, 5].map((star) => (
              <Star
                key={star}
                className={cn(
                  'w-4 h-4',
                  star <= Math.round(summary.average_rating)
                    ? 'text-calo-secondary fill-current'
                    : 'text-gray-300'
                )}
              />
            ))}
          </div>
        </div>

        {/* Sentiment Overview */}
        <div className="card p-6">
          <p className="text-sm text-gray-500 mb-4">Sentiment Distribution</p>
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-lg">{getSentimentEmoji('positive')}</span>
                <span className="text-sm text-gray-600">Positive</span>
              </div>
              <span className="font-semibold text-green-600">
                {summary.sentiment_breakdown.positive}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-lg">{getSentimentEmoji('neutral')}</span>
                <span className="text-sm text-gray-600">Neutral</span>
              </div>
              <span className="font-semibold text-gray-600">
                {summary.sentiment_breakdown.neutral}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-lg">{getSentimentEmoji('negative')}</span>
                <span className="text-sm text-gray-600">Negative</span>
              </div>
              <span className="font-semibold text-red-600">
                {summary.sentiment_breakdown.negative}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Sentiment Bar Chart */}
      {totalSentiments > 0 && (
        <div className="card p-6">
          <h3 className="font-semibold text-lg text-calo-dark mb-4">
            Sentiment Breakdown
          </h3>
          <div className="space-y-3">
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-600">Positive</span>
                <span className="font-semibold text-green-600">
                  {((summary.sentiment_breakdown.positive / totalSentiments) * 100).toFixed(0)}%
                </span>
              </div>
              <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                <div
                  className="h-full bg-green-500 transition-all duration-500"
                  style={{
                    width: `${(summary.sentiment_breakdown.positive / totalSentiments) * 100}%`,
                  }}
                />
              </div>
            </div>
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-600">Neutral</span>
                <span className="font-semibold text-gray-600">
                  {((summary.sentiment_breakdown.neutral / totalSentiments) * 100).toFixed(0)}%
                </span>
              </div>
              <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gray-400 transition-all duration-500"
                  style={{
                    width: `${(summary.sentiment_breakdown.neutral / totalSentiments) * 100}%`,
                  }}
                />
              </div>
            </div>
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-600">Negative</span>
                <span className="font-semibold text-red-600">
                  {((summary.sentiment_breakdown.negative / totalSentiments) * 100).toFixed(0)}%
                </span>
              </div>
              <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                <div
                  className="h-full bg-red-500 transition-all duration-500"
                  style={{
                    width: `${(summary.sentiment_breakdown.negative / totalSentiments) * 100}%`,
                  }}
                />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Insights Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Top Praises */}
        {summary.top_praises.length > 0 && (
          <div className="card p-6">
            <h3 className="font-semibold text-lg text-calo-dark mb-4 flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-green-500" />
              Top Praises
            </h3>
            <ul className="space-y-2">
              {summary.top_praises.map((praise, index) => (
                <li
                  key={index}
                  className="flex items-start gap-2 text-sm text-gray-700"
                >
                  <span className="text-green-500 mt-0.5">✓</span>
                  <span>{praise}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Top Complaints */}
        {summary.top_complaints.length > 0 && (
          <div className="card p-6">
            <h3 className="font-semibold text-lg text-calo-dark mb-4 flex items-center gap-2">
              <TrendingDown className="w-5 h-5 text-red-500" />
              Top Complaints
            </h3>
            <ul className="space-y-2">
              {summary.top_complaints.map((complaint, index) => (
                <li
                  key={index}
                  className="flex items-start gap-2 text-sm text-gray-700"
                >
                  <span className="text-red-500 mt-0.5">!</span>
                  <span>{complaint}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Action Items */}
      {summary.action_items.length > 0 && (
        <div className="card p-6 bg-blue-50/50 border-blue-200">
          <h3 className="font-semibold text-lg text-calo-dark mb-4">
            Recommended Actions
          </h3>
          <ul className="space-y-3">
            {summary.action_items.map((item, index) => (
              <li
                key={index}
                className="flex items-start gap-3 p-3 bg-white rounded-lg"
              >
                <div className="w-6 h-6 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <span className="text-xs font-semibold text-blue-600">
                    {index + 1}
                  </span>
                </div>
                <span className="text-sm text-gray-700">{item}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
