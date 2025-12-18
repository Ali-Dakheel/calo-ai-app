/**
 * API Client for Calo AI Advisor Backend
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Types
export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
}

export interface ChatRequest {
  message: string;
  user_id: string;
  conversation_id?: string;
}

export interface ChatResponse {
  message: string;
  conversation_id: string;
  agent_used: string;
  recommendations?: string[];
  requires_kitchen_action: boolean;
  confidence: number;
}

export interface Meal {
  id: string;
  name: string;
  description: string;
  category: string;
  dietary_tags: string[];
  nutrition: {
    calories: number;
    protein: number;
    carbs: number;
    fats: number;
    fiber?: number;
    sodium?: number;
  };
  ingredients: string[];
  allergens: string[];
  preparation_time: number;
  price: number;
  image_url?: string;
  popularity_score: number;
}

export interface RecommendationRequest {
  user_id: string;
  preferences?: Record<string, any>;
  dietary_restrictions?: string[];
  calorie_target?: number;
  meal_category?: string;
  exclude_ingredients?: string[];
  max_results?: number;
}

export interface MealRecommendation {
  meal: Meal;
  relevance_score: number;
  reasoning: string;
  matches_preferences: string[];
}

export interface Feedback {
  id: string;
  user_id: string;
  meal_id?: string;
  rating: number;
  comment: string;
  sentiment: 'positive' | 'neutral' | 'negative';
  categories: string[];
  timestamp: string;
}

export interface KitchenRequest {
  request_id: string;
  user_id: string;
  original_message: string;
  request_type: string;
  details: Record<string, any>;
  priority: number;
  status: string;
  created_at: string;
}

export interface AnalyticsSummary {
  total_feedback: number;
  average_rating: number;
  sentiment_breakdown: Record<string, number>;
  top_complaints: string[];
  top_praises: string[];
  popular_meals: string[];
  action_items: string[];
  time_period: string;
}

// API Client Class
class CaloAPI {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || `API Error: ${response.statusText}`);
    }

    return response.json();
  }

  // Health Check
  async healthCheck(): Promise<{ status: string; services: Record<string, string> }> {
    return this.request('/health');
  }

  // Chat Endpoints
  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    return this.request('/api/v1/chat/', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async getConversationHistory(conversationId: string): Promise<{
    conversation_id: string;
    message_count: number;
    messages: ChatMessage[];
  }> {
    return this.request(`/api/v1/chat/history/${conversationId}`);
  }

  // Recommendation Endpoints
  async getRecommendations(request: RecommendationRequest): Promise<{
    recommendations: MealRecommendation[];
    total_found: number;
    query_understanding: string;
  }> {
    return this.request('/api/v1/recommendations/', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async getMeal(mealId: string): Promise<Meal> {
    return this.request(`/api/v1/recommendations/meal/${mealId}`);
  }

  async browseMeals(params?: {
    category?: string;
    dietary_tag?: string;
    max_calories?: number;
    min_protein?: number;
    limit?: number;
  }): Promise<{ total: number; meals: Meal[] }> {
    const query = new URLSearchParams(
      Object.entries(params || {})
        .filter(([_, v]) => v !== undefined)
        .map(([k, v]) => [k, String(v)])
    );
    return this.request(`/api/v1/recommendations/browse?${query}`);
  }

  async getPopularMeals(limit: number = 10): Promise<{ total: number; meals: Meal[] }> {
    return this.request(`/api/v1/recommendations/popular?limit=${limit}`);
  }

  // Kitchen Endpoints
  async createKitchenRequest(data: {
    user_id: string;
    message: string;
    request_type: string;
    details: Record<string, any>;
    priority?: number;
  }): Promise<{ request_id: string; status: string; message: string }> {
    return this.request('/api/v1/kitchen/request', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getKitchenRequests(params?: {
    status?: string;
    priority_min?: number;
  }): Promise<{ total: number; requests: KitchenRequest[] }> {
    const query = new URLSearchParams(
      Object.entries(params || {})
        .filter(([_, v]) => v !== undefined)
        .map(([k, v]) => [k, String(v)])
    );
    return this.request(`/api/v1/kitchen/requests?${query}`);
  }

  async getKitchenDashboard(): Promise<{
    statistics: {
      total_requests: number;
      pending: number;
      in_progress: number;
      completed: number;
    };
    urgent_requests: KitchenRequest[];
    recent_requests: KitchenRequest[];
    requests_by_type: Record<string, number>;
  }> {
    return this.request('/api/v1/kitchen/dashboard');
  }

  async updateKitchenRequestStatus(
    requestId: string,
    status: string,
    notes?: string
  ): Promise<{ request_id: string; status: string; message: string }> {
    return this.request(`/api/v1/kitchen/request/${requestId}/status`, {
      method: 'PATCH',
      body: JSON.stringify({ status, notes }),
    });
  }

  // Analytics Endpoints
  async submitFeedback(data: {
    user_id: string;
    meal_id?: string;
    rating: number;
    comment: string;
  }): Promise<{ feedback_id: string; status: string; message: string }> {
    const params = new URLSearchParams(
      Object.entries(data)
        .filter(([_, v]) => v !== undefined)
        .map(([k, v]) => [k, String(v)])
    );
    return this.request(`/api/v1/analytics/feedback?${params}`, {
      method: 'POST',
    });
  }

  async getFeedback(params?: {
    sentiment?: string;
    category?: string;
    min_rating?: number;
    limit?: number;
  }): Promise<{ total: number; feedback: Feedback[] }> {
    const query = new URLSearchParams(
      Object.entries(params || {})
        .filter(([_, v]) => v !== undefined)
        .map(([k, v]) => [k, String(v)])
    );
    return this.request(`/api/v1/analytics/feedback?${query}`);
  }

  async getAnalyticsSummary(params?: {
    days?: number;
    meal_id?: string;
  }): Promise<AnalyticsSummary> {
    const query = new URLSearchParams(
      Object.entries(params || {})
        .filter(([_, v]) => v !== undefined)
        .map(([k, v]) => [k, String(v)])
    );
    return this.request(`/api/v1/analytics/summary?${query}`);
  }

  async getFeedbackTrends(days: number = 30): Promise<{
    period: string;
    trends: Array<{
      date: string;
      count: number;
      average_rating: number;
      sentiment_distribution: Record<string, number>;
    }>;
  }> {
    return this.request(`/api/v1/analytics/trends?days=${days}`);
  }
}

// Export singleton instance
export const api = new CaloAPI();

// Export class for custom instances
export { CaloAPI };
