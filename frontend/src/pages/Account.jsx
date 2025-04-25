import React, { useEffect, useState } from 'react';
import api from '@/api/axios';
import { jwtDecode } from 'jwt-decode';
import { useTheme } from '../context/ThemeContext';

export default function Account() {
  const [user, setUser] = useState(null);
  const [error, setError] = useState('');
  const [editingUsername, setEditingUsername] = useState(false);
  const [newUsername, setNewUsername] = useState('');
  const { darkMode, setDarkMode } = useTheme();
  const [confirmOpen, setConfirmOpen] = useState(false);

  const handleDeleteAccount = async () => {
    try {
      await api.delete(`/users/${user.id}`);
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      window.location.href = '/login';
    } catch (err) {
      setError('Failed to delete account');
      console.error('Delete account error:', err);
    }
  };

  useEffect(() => {
    document.documentElement.classList.toggle('dark', darkMode);
    localStorage.setItem('theme', darkMode ? 'dark' : 'light');
  }, [darkMode]);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      setError('Not authenticated.');
      return;
    }

    let userId;
    try {
      const decoded = jwtDecode(token);
      userId = decoded.sub;
    } catch (err) {
      setError('Invalid token.');
      return;
    }

    api.get(`/users/${userId}`)
      .then((res) => {
        setUser(res.data);
        setNewUsername(res.data.user_name);
      })
      .catch((err) => {
        const msg = err.response?.data?.error || 'Failed to fetch user data';
        setError(msg);
      });
  }, []);

  const handleUsernameUpdate = async () => {
    try {
      await api.put(`/users/${user.id}`, { user_name: newUsername });
      setUser({ ...user, user_name: newUsername });
      setEditingUsername(false);
    } catch (err) {
      setError('Failed to update username');
    }
  };

  return (
    <main className="bg-white dark:bg-gray-900 min-h-screen px-6 sm:px-10 lg:px-16 xl:px-24 2xl:px-32 py-6 text-gray-800 dark:text-gray-100 max-w-[1600px] mx-auto">
      <h2 className="text-2xl font-semibold mb-4">Account Info</h2>
      <hr className="my-5 border-gray-300" />
      {error && <p className="text-red-600 text-sm mb-6">{error}</p>}

      {user ? (
        <>
          <div className="text-left space-y-4 mb-2">
            <p>
              <strong>Username: </strong>
              {editingUsername ? (
                <>
                  <input
                    value={newUsername}
                    onChange={(e) => setNewUsername(e.target.value)}
                    className="border px-2 ml-2 rounded-sm"
                  />
                  <button onClick={handleUsernameUpdate} className="ml-2 text-blue-600 hover:underline">Save</button>
                  <button onClick={() => setEditingUsername(false)} className="ml-2 text-gray-500 hover:underline">Cancel</button>
                </>
              ) : (
                <>
                  {user.user_name}
                  <span
                    onClick={() => setEditingUsername(true)}
                    className="material-icons text-gray-400 hover:text-gray-600 cursor-pointer text-base ml-2 align-middle"
                  >
                    edit
                  </span>
                </>
              )}
            </p>

            <p>
              <strong>Email:</strong> {user.email}</p>

            <div className="flex items-center gap-3 pt-2">
              <span className="font-medium"><strong>Mode:</strong></span>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={darkMode}
                  onChange={() => setDarkMode(!darkMode)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 rounded-full peer dark:bg-gray-700 peer-checked:bg-blue-600 transition-colors duration-300"></div>
                <div className="absolute left-1 top-1 w-4 h-4 bg-white rounded-full shadow-md transform transition-transform duration-300 peer-checked:translate-x-5"></div>
                <span className="ml-3 text-sm font-medium text-gray-900 dark:text-gray-300">
                  {darkMode ? 'Dark' : 'Light'}
                </span>
              </label>
            </div>
          </div>

          <div className="mt-8">
            <button
              onClick={() => setConfirmOpen(true)}
              className="bg-blue-600 text-white px-5 py-2 rounded-md hover:bg-blue-700 transition"
            >
              Delete account
            </button>
          </div>
        </>
      ) : !error ? (
        <p>Loading...</p>
      ) : null}

      <hr className="my-5 border-gray-300" />

      <h2 className="text-2xl font-semibold mb-4">Favorite Coins</h2>
      {user?.favorite_coins?.length > 0 ? (
        <ul className="list-disc pl-6 text-left">
          {user.favorite_coins.map((symbol) => (
            <li key={symbol}>{symbol}</li>
          ))}
        </ul>
      ) : (
        <p className="text-gray-500 text-left">You haven’t added any favorite coins yet.</p>
      )}

      {confirmOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-900 p-6 rounded-xl shadow-md w-80 text-center">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Delete Account?</h3>
            <p className="text-sm text-gray-600 dark:text-gray-300 mb-6">This action cannot be undone.</p>
            <div className="flex justify-center gap-4">
              <button
                onClick={handleDeleteAccount}
                className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
              >
                Delete
              </button>
              <button
                onClick={() => setConfirmOpen(false)}
                className="bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-100 px-4 py-2 rounded hover:bg-gray-300 dark:hover:bg-gray-600"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
