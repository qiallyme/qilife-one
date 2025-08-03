import React, { useState } from 'react';
import { MiniAppDuplicateCleaner } from './components/MiniAppDuplicateCleaner';
// Import other mini-apps as you build them

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'duplicates'>('duplicates');
  return (
    <div className="flex h-screen">
      <nav className="w-48 bg-gray-200 p-4 space-y-2">
        <button
          className={`block w-full text-left py-2 px-3 rounded ${
            activeTab === 'duplicates' ? 'bg-blue-500 text-white' : ''
          }`}
          onClick={() => setActiveTab('duplicates')}
        >
          Duplicate Cleaner
        </button>
        {/* Add more tab buttons here as you implement other modules */}
      </nav>
      <main className="flex-1 overflow-auto">
        {activeTab === 'duplicates' && <MiniAppDuplicateCleaner />}
      </main>
    </div>
  );
};
