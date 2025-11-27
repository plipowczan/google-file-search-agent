import React, { useState, useEffect } from 'react';
import { getStores, createStore, deleteStore } from '../api/api';
import { Plus, Trash2, Database } from 'lucide-react';

const StoreSelector = ({ onSelectStore, selectedStore }) => {
  const [stores, setStores] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isCreating, setIsCreating] = useState(false);
  const [newStoreName, setNewStoreName] = useState('');
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchStores();
  }, []);

  const fetchStores = async () => {
    try {
      setLoading(true);
      const data = await getStores();
      setStores(data.stores);
    } catch (err) {
      setError('Failed to load stores');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateStore = async (e) => {
    e.preventDefault();
    if (!newStoreName.trim()) return;

    try {
      setLoading(true);
      const newStore = await createStore(newStoreName);
      setStores([newStore, ...stores]);
      setNewStoreName('');
      setIsCreating(false);
      onSelectStore(newStore);
    } catch (err) {
      setError('Failed to create store. Name might be taken.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteStore = async (e, storeId) => {
    e.stopPropagation();
    if (!window.confirm('Are you sure? This will delete the store and all its files permanently.')) return;

    try {
      await deleteStore(storeId);
      setStores(stores.filter(s => s.id !== storeId));
      if (selectedStore && selectedStore.id === storeId) {
        onSelectStore(null);
      }
    } catch (err) {
      setError('Failed to delete store');
      console.error(err);
    }
  };

  return (
    <div className="bg-white p-4 rounded-lg shadow mb-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold flex items-center gap-2">
          <Database className="w-5 h-5" />
          Knowledge Bases
        </h2>
        <button
          onClick={() => setIsCreating(!isCreating)}
          className="bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700 flex items-center gap-1 text-sm"
        >
          <Plus className="w-4 h-4" /> New Store
        </button>
      </div>

      {error && (
        <div className="bg-red-100 text-red-700 p-2 rounded mb-4 text-sm">
          {error}
        </div>
      )}

      {isCreating && (
        <form onSubmit={handleCreateStore} className="mb-4 flex gap-2">
          <input
            type="text"
            value={newStoreName}
            onChange={(e) => setNewStoreName(e.target.value)}
            placeholder="Store Name (e.g. HR Docs)"
            className="flex-1 border rounded px-3 py-2 text-sm"
            autoFocus
          />
          <button
            type="submit"
            disabled={loading}
            className="bg-green-600 text-white px-3 py-2 rounded hover:bg-green-700 text-sm"
          >
            Create
          </button>
        </form>
      )}

      {loading && stores.length === 0 ? (
        <p className="text-gray-500 text-sm">Loading stores...</p>
      ) : (
        <div className="space-y-2 max-h-60 overflow-y-auto">
          {stores.length === 0 ? (
            <p className="text-gray-500 text-sm italic">No stores created yet.</p>
          ) : (
            stores.map((store) => (
              <div
                key={store.id}
                onClick={() => onSelectStore(store)}
                className={`p-3 rounded border cursor-pointer flex justify-between items-center transition-colors ${
                  selectedStore?.id === store.id
                    ? 'bg-blue-50 border-blue-500 ring-1 ring-blue-500'
                    : 'hover:bg-gray-50 border-gray-200'
                }`}
              >
                <div>
                  <div className="font-medium text-gray-900">{store.display_name}</div>
                  <div className="text-xs text-gray-500">
                    {new Date(store.created_at).toLocaleDateString()}
                  </div>
                </div>
                <button
                  onClick={(e) => handleDeleteStore(e, store.id)}
                  className="text-gray-400 hover:text-red-600 p-1"
                  title="Delete Store"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
};

export default StoreSelector;
