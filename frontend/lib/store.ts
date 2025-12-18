/**
 * Zustand Store for UI State Management
 */
import { create } from 'zustand';

// Helper to get or create persistent user ID
const getOrCreateUserId = (): string => {
  if (typeof window === 'undefined') return 'server-user';

  const stored = localStorage.getItem('calo_user_id');
  if (stored) return stored;

  const newId = `user_${crypto.randomUUID().slice(0, 8)}`;
  localStorage.setItem('calo_user_id', newId);
  return newId;
};

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
  setLoading: (isLoading: boolean) => void;
  setConversationId: (id: string) => void;
  setUserId: (id: string) => void;
}

export const useChatStore = create<ChatStore>((set) => ({
  messages: [],
  conversationId: null,
  isLoading: false,
  userId: getOrCreateUserId(),

  addMessage: (message) =>
    set((state) => ({
      messages: [
        ...state.messages,
        {
          ...message,
          id: crypto.randomUUID().slice(0, 8),
          timestamp: new Date(),
        },
      ],
    })),

  clearMessages: () =>
    set({
      messages: [],
      conversationId: null,
    }),

  setLoading: (isLoading) => set({ isLoading }),

  setConversationId: (id) => set({ conversationId: id }),

  setUserId: (id) => set({ userId: id }),
}));

type TabType = 'chat' | 'kitchen' | 'analytics';
type ThemeType = 'light' | 'dark';

interface UIStore {
  // State
  activeTab: TabType;
  sidebarOpen: boolean;
  theme: ThemeType;

  // Actions
  setActiveTab: (tab: TabType) => void;
  toggleSidebar: () => void;
  setTheme: (theme: ThemeType) => void;
}

export const useUIStore = create<UIStore>((set) => ({
  activeTab: 'chat',
  sidebarOpen: true,
  theme: 'light',

  setActiveTab: (tab) => set({ activeTab: tab }),

  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),

  setTheme: (theme) => set({ theme }),
}));

type NotificationType = 'success' | 'error' | 'info' | 'warning';

interface Notification {
  id: string;
  type: NotificationType;
  message: string;
  timestamp: Date;
}

interface NotificationStore {
  notifications: Notification[];
  addNotification: (type: NotificationType, message: string) => void;
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
          id: crypto.randomUUID().slice(0, 8),
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

  clearNotifications: () => set({ notifications: [] }),
}));
