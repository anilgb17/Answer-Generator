import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

export default function Dashboard() {
  const { user, token, logout, isAdmin } = useAuth();
  const navigate = useNavigate();
  const [apiKeys, setApiKeys] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  // Form state
  const [showAddKey, setShowAddKey] = useState(false);
  const [provider, setProvider] = useState('gemini');
  const [apiKey, setApiKey] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

  useEffect(() => {
    if (!token) {
      navigate('/login');
      return;
    }
    fetchApiKeys();
  }, [token, navigate]);

  const fetchApiKeys = async () => {
    try {
      const response = await fetch(`${apiBaseUrl}/api/auth/api-keys`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) throw new Error('Failed to fetch API keys');

      const data = await response.json();
      setApiKeys(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleAddKey = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setSubmitting(true);

    try {
      const response = await fetch(`${apiBaseUrl}/api/auth/api-keys`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ provider, api_key: apiKey }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to add API key');
      }

      setSuccess(`${provider} API key added successfully!`);
      setApiKey('');
      setShowAddKey(false);
      fetchApiKeys();
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const handleDeleteKey = async (providerName) => {
    if (!confirm(`Delete ${providerName} API key?`)) return;

    try {
      const response = await fetch(`${apiBaseUrl}/api/auth/api-keys/${providerName}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) throw new Error('Failed to delete API key');

      setSuccess(`${providerName} API key deleted`);
      fetchApiKeys();
    } catch (err) {
      setError(err.message);
    }
  };

  const providerInfo = {
    gemini: { name: 'Google Gemini', color: 'blue', icon: '🔷' },
    openai: { name: 'OpenAI', color: 'green', icon: '🤖' },
    anthropic: { name: 'Anthropic Claude', color: 'purple', icon: '🧠' },
    perplexity: { name: 'Perplexity', color: 'orange', icon: '🔍' },
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-gray-900">Dashboard</h1>
            </div>
            <div className="flex items-center space-x-4">
              <Link to="/" className="text-gray-700 hover:text-gray-900">
                Home
              </Link>
              {isAdmin && (
                <Link to="/admin" className="text-indigo-600 hover:text-indigo-700 font-medium">
                  Admin Panel
                </Link>
              )}
              <span className="text-gray-700">{user?.username}</span>
              <button
                onClick={logout}
                className="text-red-600 hover:text-red-700"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {/* Welcome Section */}
          <div className="bg-white shadow rounded-lg p-6 mb-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Welcome, {user?.username}!
            </h2>
            <p className="text-gray-600">
              Manage your AI provider API keys to use your own accounts for answer generation.
            </p>
          </div>

          {/* Messages */}
          {error && (
            <div className="mb-4 bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded">
              {error}
            </div>
          )}
          {success && (
            <div className="mb-4 bg-green-50 border border-green-200 text-green-800 px-4 py-3 rounded">
              {success}
            </div>
          )}

          {/* API Keys Section */}
          <div className="bg-white shadow rounded-lg p-6">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-lg font-medium text-gray-900">Your API Keys</h3>
              <button
                onClick={() => setShowAddKey(!showAddKey)}
                className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
              >
                {showAddKey ? 'Cancel' : 'Add API Key'}
              </button>
            </div>

            {/* Add Key Form */}
            {showAddKey && (
              <form onSubmit={handleAddKey} className="mb-6 p-4 bg-gray-50 rounded-lg">
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Provider
                    </label>
                    <select
                      value={provider}
                      onChange={(e) => setProvider(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    >
                      <option value="gemini">Google Gemini</option>
                      <option value="openai">OpenAI</option>
                      <option value="anthropic">Anthropic Claude</option>
                      <option value="perplexity">Perplexity</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      API Key
                    </label>
                    <input
                      type="password"
                      value={apiKey}
                      onChange={(e) => setApiKey(e.target.value)}
                      placeholder="Enter your API key"
                      required
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    />
                  </div>
                </div>
                <button
                  type="submit"
                  disabled={submitting}
                  className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50"
                >
                  {submitting ? 'Adding...' : 'Add Key'}
                </button>
              </form>
            )}

            {/* API Keys List */}
            {loading ? (
              <p className="text-gray-500">Loading...</p>
            ) : apiKeys.length === 0 ? (
              <p className="text-gray-500">No API keys added yet. Add one to get started!</p>
            ) : (
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {apiKeys.map((key) => {
                  const info = providerInfo[key.provider] || { name: key.provider, color: 'gray', icon: '🔑' };
                  return (
                    <div
                      key={key.provider}
                      className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                    >
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center">
                          <span className="text-2xl mr-2">{info.icon}</span>
                          <h4 className="font-medium text-gray-900">{info.name}</h4>
                        </div>
                        <button
                          onClick={() => handleDeleteKey(key.provider)}
                          className="text-red-600 hover:text-red-700 text-sm"
                        >
                          Delete
                        </button>
                      </div>
                      <p className="text-xs text-gray-500">
                        Added: {new Date(key.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* Info Section */}
          <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h4 className="font-medium text-blue-900 mb-2">ℹ️ How it works</h4>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• Add your AI provider API keys to use your own accounts</li>
              <li>• Your keys are encrypted and stored securely</li>
              <li>• When generating answers, your keys will be used instead of system keys</li>
              <li>• You can add multiple providers and switch between them</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
