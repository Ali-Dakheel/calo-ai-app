/**
 * Error State Component
 * Reusable error display with retry functionality
 */
'use client';

import { AlertCircle, RefreshCw } from 'lucide-react';

interface ErrorStateProps {
  message?: string;
  onRetry?: () => void;
}

export const ErrorState = ({
  message = 'Something went wrong. Please try again.',
  onRetry,
}: ErrorStateProps) => {
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if ((e.key === 'Enter' || e.key === ' ') && onRetry) {
      e.preventDefault();
      onRetry();
    }
  };

  return (
    <div
      className="flex flex-col items-center justify-center py-12 px-4"
      role="alert"
      aria-live="polite"
    >
      <div className="w-16 h-16 rounded-full bg-red-50 flex items-center justify-center mb-4">
        <AlertCircle className="w-8 h-8 text-red-500" aria-hidden="true" />
      </div>
      <h3 className="text-lg font-semibold text-calo-dark mb-2">
        Error Loading Data
      </h3>
      <p className="text-sm text-gray-600 text-center max-w-md mb-4">
        {message}
      </p>
      {onRetry && (
        <button
          type="button"
          onClick={onRetry}
          onKeyDown={handleKeyDown}
          className="flex items-center gap-2 px-4 py-2 bg-calo-primary text-white rounded-lg hover:bg-green-600 transition-colors focus:outline-none focus:ring-2 focus:ring-calo-primary focus:ring-offset-2"
          aria-label="Retry loading data"
        >
          <RefreshCw className="w-4 h-4" aria-hidden="true" />
          Try Again
        </button>
      )}
    </div>
  );
};
