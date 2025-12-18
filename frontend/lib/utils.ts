/**
 * Utility Functions
 */
import { clsx, type ClassValue } from 'clsx';

// Class name merger
export function cn(...inputs: ClassValue[]) {
  return clsx(inputs);
}

// Format date
export function formatDate(date: Date | string): string {
  const d = typeof date === 'string' ? new Date(date) : date;
  return d.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
}

// Format time
export function formatTime(date: Date | string): string {
  const d = typeof date === 'string' ? new Date(date) : date;
  return d.toLocaleTimeString('en-US', {
    hour: 'numeric',
    minute: '2-digit',
  });
}

// Format relative time (e.g., "2 hours ago")
export function formatRelativeTime(date: Date | string): string {
  const d = typeof date === 'string' ? new Date(date) : date;
  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - d.getTime()) / 1000);

  if (diffInSeconds < 60) return 'just now';
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
  if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)}d ago`;
  
  return formatDate(d);
}

// Format calories
export function formatCalories(calories: number): string {
  return `${calories} cal`;
}

// Format macros
export function formatMacros(protein: number, carbs: number, fats: number): string {
  return `${protein}g P • ${carbs}g C • ${fats}g F`;
}

// Get dietary tag color
export function getDietaryTagColor(tag: string): string {
  const colors: Record<string, string> = {
    vegetarian: 'bg-green-100 text-green-700',
    vegan: 'bg-emerald-100 text-emerald-700',
    gluten_free: 'bg-amber-100 text-amber-700',
    dairy_free: 'bg-blue-100 text-blue-700',
    keto: 'bg-purple-100 text-purple-700',
    low_carb: 'bg-indigo-100 text-indigo-700',
    high_protein: 'bg-red-100 text-red-700',
    halal: 'bg-teal-100 text-teal-700',
  };
  
  return colors[tag] || 'bg-gray-100 text-gray-700';
}

// Format dietary tag name
export function formatDietaryTag(tag: string): string {
  return tag
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

// Get sentiment color
export function getSentimentColor(sentiment: string): string {
  const colors: Record<string, string> = {
    positive: 'text-green-600',
    neutral: 'text-gray-600',
    negative: 'text-red-600',
  };
  
  return colors[sentiment] || 'text-gray-600';
}

// Get sentiment emoji
export function getSentimentEmoji(sentiment: string): string {
  const emojis: Record<string, string> = {
    positive: '😊',
    neutral: '😐',
    negative: '😞',
  };
  
  return emojis[sentiment] || '😐';
}

// Get priority color
export function getPriorityColor(priority: number): string {
  if (priority >= 4) return 'bg-red-100 text-red-700 border-red-200';
  if (priority >= 3) return 'bg-orange-100 text-orange-700 border-orange-200';
  return 'bg-blue-100 text-blue-700 border-blue-200';
}

// Get priority label
export function getPriorityLabel(priority: number): string {
  if (priority >= 4) return 'Urgent';
  if (priority >= 3) return 'High';
  if (priority >= 2) return 'Medium';
  return 'Low';
}

// Get status color
export function getStatusColor(status: string): string {
  const colors: Record<string, string> = {
    pending: 'bg-yellow-100 text-yellow-700',
    in_progress: 'bg-blue-100 text-blue-700',
    completed: 'bg-green-100 text-green-700',
    cancelled: 'bg-gray-100 text-gray-700',
  };
  
  return colors[status] || 'bg-gray-100 text-gray-700';
}

// Format status name
export function formatStatus(status: string): string {
  return status
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

// Truncate text
export function truncate(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
}

// Format price
export function formatPrice(price: number): string {
  return `$${price.toFixed(2)}`;
}

// Get meal category icon
export function getMealCategoryIcon(category: string): string {
  const icons: Record<string, string> = {
    breakfast: '🌅',
    lunch: '☀️',
    dinner: '🌙',
    snack: '🍎',
  };
  
  return icons[category] || '🍽️';
}

// Generate random ID
export function generateId(): string {
  return Math.random().toString(36).substring(2, 11);
}

// Debounce function
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null;
  
  return (...args: Parameters<T>) => {
    if (timeout) clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
}

// Format percentage
export function formatPercentage(value: number): string {
  return `${Math.round(value * 100)}%`;
}

// Calculate average
export function calculateAverage(numbers: number[]): number {
  if (numbers.length === 0) return 0;
  return numbers.reduce((sum, num) => sum + num, 0) / numbers.length;
}
