import React, { useState } from 'react';
import api from '../services/api';

interface SearchResult {
  id: number;
  url: string;
  email: string;
  price: number;
  dr: number | null;
  traffic: number | null;
  relevance_score: number;
  matching_keywords: string[];
}

export default function Search() {
  const [keyword, setKeyword] = useState('');
  const [minDr, setMinDr] = useState('');
  const [maxDr, setMaxDr] = useState('');
  const [minTraffic, setMinTraffic] = useState('');
  const [maxPrice, setMaxPrice] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const params: any = { keyword };
      if (minDr) params.min_dr = parseInt(minDr);
      if (maxDr) params.max_dr = parseInt(maxDr);
      if (minTraffic) params.min_traffic = parseInt(minTraffic);
      if (maxPrice) params.max_price = parseFloat(maxPrice);

      const response = await api.post('/search/', params);
      setResults(response.data);
    } catch (err: any) {
      setError('Failed to search. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">
          Link Qualification Search
        </h1>

        <form onSubmit={handleSearch} className="bg-white shadow rounded-lg p-6 mb-8">
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            <div className="col-span-full">
              <label className="block text-sm font-medium text-gray-700">
                Keyword
              </label>
              <input
                type="text"
                required
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                value={keyword}
                onChange={(e) => setKeyword(e.target.value)}
                placeholder="Enter keyword to search..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">
                Min DR
              </label>
              <input
                type="number"
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                value={minDr}
                onChange={(e) => setMinDr(e.target.value)}
                placeholder="0"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">
                Max DR
              </label>
              <input
                type="number"
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                value={maxDr}
                onChange={(e) => setMaxDr(e.target.value)}
                placeholder="100"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">
                Min Traffic
              </label>
              <input
                type="number"
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                value={minTraffic}
                onChange={(e) => setMinTraffic(e.target.value)}
                placeholder="0"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">
                Max Price ($)
              </label>
              <input
                type="number"
                step="0.01"
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                value={maxPrice}
                onChange={(e) => setMaxPrice(e.target.value)}
                placeholder="1000"
              />
            </div>
          </div>

          <div className="mt-6">
            <button
              type="submit"
              disabled={loading}
              className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
            >
              {loading ? 'Searching...' : 'Search'}
            </button>
          </div>
        </form>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        {results.length > 0 && (
          <div className="bg-white shadow overflow-hidden sm:rounded-md">
            <ul className="divide-y divide-gray-200">
              {results.map((result) => (
                <li key={result.id} className="px-4 py-4 sm:px-6">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <p className="text-sm font-medium text-indigo-600 truncate">
                          {result.url}
                        </p>
                        <div className="ml-2 flex-shrink-0 flex">
                          <p className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                            Relevance: {(result.relevance_score * 100).toFixed(1)}%
                          </p>
                        </div>
                      </div>
                      <div className="mt-2 sm:flex sm:justify-between">
                        <div className="sm:flex">
                          <p className="flex items-center text-sm text-gray-500">
                            Email: {result.email}
                          </p>
                          <p className="mt-2 flex items-center text-sm text-gray-500 sm:mt-0 sm:ml-6">
                            Price: ${result.price}
                          </p>
                        </div>
                        <div className="mt-2 flex items-center text-sm text-gray-500 sm:mt-0">
                          <p>DR: {result.dr || 'N/A'}</p>
                          <p className="ml-4">Traffic: {result.traffic || 'N/A'}</p>
                        </div>
                      </div>
                      {result.matching_keywords.length > 0 && (
                        <div className="mt-2">
                          <p className="text-sm text-gray-500">
                            Keywords: {result.matching_keywords.join(', ')}
                          </p>
                        </div>
                      )}
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}