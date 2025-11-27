import React, { useState } from 'react';
import StoreSelector from './components/StoreSelector';
import FileList from './components/FileList';
import FileUploader from './components/FileUploader';
import ChatInterface from './components/ChatInterface';
import { FileText, MessageSquare } from 'lucide-react';

function App() {
  const [selectedStore, setSelectedStore] = useState(null);
  const [activeTab, setActiveTab] = useState('files'); // 'files' or 'chat'
  const [refreshFiles, setRefreshFiles] = useState(0); // Trigger to refresh file list

  const handleStoreSelect = (store) => {
    setSelectedStore(store);
    // Reset tab to files when store changes? Or keep active tab?
    // Let's keep active tab but maybe default to files if it was null
  };

  const handleUploadSuccess = () => {
    setRefreshFiles(prev => prev + 1);
  };

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col">
      {/* Top Bar */}
      <header className="bg-white shadow-sm z-10">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="bg-blue-600 text-white p-1.5 rounded">
              <MessageSquare className="w-5 h-5" />
            </div>
            <h1 className="text-xl font-bold text-gray-900">Gemini RAG Manager</h1>
          </div>
          <div className="text-sm text-gray-500">
            Internal Tool
          </div>
        </div>
      </header>

      <main className="flex-1 max-w-7xl mx-auto w-full px-4 py-6 flex gap-6">
        {/* Sidebar - Store Selection */}
        <div className="w-1/3 max-w-sm">
          <StoreSelector 
            onSelectStore={handleStoreSelect} 
            selectedStore={selectedStore} 
          />
          
          {selectedStore && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-sm text-blue-800">
              <h4 className="font-semibold mb-1">Current Context</h4>
              <p>You are managing <strong>{selectedStore.display_name}</strong>.</p>
              <p className="mt-2 text-xs opacity-75">ID: {selectedStore.id}</p>
            </div>
          )}
        </div>

        {/* Main Content Area */}
        <div className="flex-1">
          {!selectedStore ? (
            <div className="bg-white rounded-lg shadow p-10 text-center text-gray-500 h-full flex flex-col items-center justify-center">
              <MessageSquare className="w-16 h-16 mb-4 text-gray-300" />
              <h2 className="text-xl font-semibold mb-2">No Knowledge Base Selected</h2>
              <p>Please select or create a Store from the sidebar to manage files and chat.</p>
            </div>
          ) : (
            <div className="flex flex-col h-full">
              {/* Tabs */}
              <div className="flex gap-1 mb-4 border-b border-gray-200">
                <button
                  onClick={() => setActiveTab('files')}
                  className={`px-4 py-2 font-medium text-sm rounded-t-lg flex items-center gap-2 ${
                    activeTab === 'files'
                      ? 'bg-white text-blue-600 border-t border-l border-r border-gray-200 -mb-px'
                      : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  <FileText className="w-4 h-4" />
                  Files & Context
                </button>
                <button
                  onClick={() => setActiveTab('chat')}
                  className={`px-4 py-2 font-medium text-sm rounded-t-lg flex items-center gap-2 ${
                    activeTab === 'chat'
                      ? 'bg-white text-blue-600 border-t border-l border-r border-gray-200 -mb-px'
                      : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  <MessageSquare className="w-4 h-4" />
                  Chat Agent
                </button>
              </div>

              {/* Tab Content */}
              <div className="flex-1">
                {activeTab === 'files' && (
                  <div className="space-y-6 animate-in fade-in duration-300">
                    <FileUploader 
                      storeId={selectedStore.id} 
                      onUploadSuccess={handleUploadSuccess} 
                    />
                    <FileList 
                      storeId={selectedStore.id} 
                      refreshTrigger={refreshFiles} 
                    />
                  </div>
                )}

                {activeTab === 'chat' && (
                  <div className="animate-in fade-in duration-300 h-full">
                    <ChatInterface storeId={selectedStore.id} />
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
