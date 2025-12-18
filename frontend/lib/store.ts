/**
 * Zustand Store for UI State Management
 */
import { create } from 'zustand';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  agent?: string;
  recommendations?: string[];
}

interface ChatStore {
  // State
  messages: Message[];
  conversationId: string | null;
  isLoading: boolean;
  userId: string;
  
  // Actions
  addMessage: (message: Omit<Message, 'id' | 'timestamp'>) => void;
  clearMessages: () => void;
  setLoading: (loading: boolean) => void;
  setConversationId: (id: string) => void;
  setUserId: (id: string) => void;
}

export const useChatStore = create<ChatStore>((set) => ({
  messages: [],
  conversationId: null,
  isLoading: false,
  userId: `user_${Math.random().toString(36).substring(7)}`,
  
  addMessage: (message) =>
    set((state) => ({
      messages: [
        ...state.messages,
        {
          ...message,
          id: Math.random().toString(36).substring(7),
          timestamp: new Date(),
        },
      ],
    })),
  
  clearMessages: () =>
    set({
      messages: [],
      conversationId: null,
    }),
  
  setLoading: (loading) =>
    set({ isLoading: loading }),
  
  setConversationId: (id) =>
    set({ conversationId: id }),
  
  setUserId: (id) =>
    set({ userId: id }),
}));

interface UIStore {
  // State
  activeTab: 'chat' | 'kitchen' | 'analytics';
  sidebarOpen: boolean;
  theme: 'light' | 'dark';
  
  // Actions
  setActiveTab: (tab: 'chat' | 'kitchen' | 'analytics') => void;
  toggleSidebar: () => void;
  setTheme: (theme: 'light' | 'dark') => void;
}

export const useUIStore = create<UIStore>((set) => ({
  activeTab: 'chat',
  sidebarOpen: true,
  theme: 'light',
  
  setActiveTab: (tab) =>
    set({ activeTab: tab }),
  
  toggleSidebar: () =>
    set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  
  setTheme: (theme) =>
    set({ theme }),
}));

interface NotificationStore {
  notifications: Array<{
    id: string;
    type: 'success' | 'error' | 'info' | 'warning';
    message: string;
    timestamp: Date;
  }>;
  
  addNotification: (type: 'success' | 'error' | 'info' | 'warning', message: string) => void;
  removeNotification: (id: string) => void;
  clearNotifications: () => void;
}

export const useNotificationStore = create<NotificationStore>((set) => ({
  notifications: [],
  
  addNotification: (type, message) =>
    set((state) => ({
      notifications: [
        ...state.notifications,
        {
          id: Math.random().toString(36).substring(7),
          type,
          message,
          timestamp: new Date(),
        },
      ],
    })),
  
  removeNotification: (id) =>
    set((state) => ({
      notifications: state.notifications.filter((n) => n.id !== id),
    })),
  
  clearNotifications: () =>
    set({ notifications: [] }),
}));
