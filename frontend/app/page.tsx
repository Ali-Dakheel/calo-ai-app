/**
 * Main Page - Calo AI Nutrition Advisor
 */
'use client';

import { MessageSquare, ChefHat, BarChart3, Sparkles } from 'lucide-react';
import { useUIStore } from '@/lib/store';
import { ChatInterface } from '@/components/ChatInterface';
import { KitchenDashboard } from '@/components/KitchenDashboard';
import { AnalyticsPanel } from '@/components/AnalyticsPanel';
import { cn } from '@/lib/utils';

export default function Home() {
  const { activeTab, setActiveTab } = useUIStore();

  const tabs = [
    { id: 'chat' as const, label: 'AI Chat', icon: MessageSquare },
    { id: 'kitchen' as const, label: 'Kitchen', icon: ChefHat },
    { id: 'analytics' as const, label: 'Analytics', icon: BarChart3 },
  ];

  return (
    <main className="min-h-screen bg-gradient-to-br from-calo-light via-white to-green-50/30">
      {/* Header */}
      <header className="sticky top-0 z-50 backdrop-blur-lg bg-white/80 border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-calo-primary to-green-600 flex items-center justify-center shadow-lg">
                <Sparkles className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold gradient-text">Calo AI</h1>
                <p className="text-xs text-gray-500">Nutrition Advisor</p>
              </div>
            </div>

            {/* Status Indicator */}
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-green-50 border border-green-200">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
              <span className="text-xs font-medium text-green-700">AI Active</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Tab Navigation */}
        <div className="mb-6">
          <div className="inline-flex items-center gap-2 p-1 bg-white rounded-xl shadow-soft border border-gray-100">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;

              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={cn(
                    'flex items-center gap-2 px-4 py-2.5 rounded-lg font-medium text-sm transition-all duration-200',
                    isActive
                      ? 'bg-calo-primary text-white shadow-md'
                      : 'text-gray-600 hover:bg-gray-50'
                  )}
                >
                  <Icon className="w-4 h-4" />
                  {tab.label}
                </button>
              );
            })}
          </div>
        </div>

        {/* Tab Content */}
        <div className="animate-fade-in">
          {activeTab === 'chat' && (
            <div className="max-w-4xl mx-auto">
              <ChatInterface />
            </div>
          )}

          {activeTab === 'kitchen' && <KitchenDashboard />}

          {activeTab === 'analytics' && <AnalyticsPanel />}
        </div>

        {/* Footer Info */}
        <div className="mt-12 text-center">
          <p className="text-sm text-gray-500">
            Built with ❤️ by Ali Dakheel for Calo AI Specialist Application
          </p>
          <p className="text-xs text-gray-400 mt-1">
            Powered by Ollama (llama3.2) • FastAPI • ChromaDB • Next.js 15
          </p>
        </div>
      </div>
    </main>
  );
}
