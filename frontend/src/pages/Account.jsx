import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { jwtDecode } from 'jwt-decode';

export default function Account() {
  const [user, setUser] = useState(null);
  const [error, setError] = useState('');

  const fetchUserData = async (accessToken) => {
    try {
      const decoded = jwtDecode(accessToken);
      const userId = decoded.sub;

      const res = await axios.get(`http://localhost:5050/users/${userId}`, {
        headers: { Authorization: `Bearer ${accessToken}` }
      });

      setUser(res.data);
    } catch (err) {
      const status = err.response?.status;
      if (status === 401) {
        const refreshed = await tryRefreshToken();
        if (refreshed) {
          fetchUserData(refreshed);
        } else {
          setError('Session expired. Please log in again.');
          logout();
        }
      } else {
        setError('Failed to fetch user data.');
      }
    }
  };

  const tryRefreshToken = async () => {
    const refreshToken = localStorage.getItem('refresh_token');
    try {
      const res = await axios.post('http://localhost:5050/users/refresh', {}, {
        headers: {
          Authorization: `Bearer ${refreshToken}`
        }
      });
      const newAccess = res.data.access_token;
      localStorage.setItem('access_token', newAccess);
      return newAccess;
    } catch {
      return null;
    }
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    window.location.href = '/login';
  };

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      fetchUserData(token);
    } else {
      setError('Not authenticated.');
    }
  }, []);

  return (
    <div className="min-h-screen px-6 py-10 bg-white text-gray-800">
      <h1 className="text-3xl font-bold mb-6">Account Info</h1>
      {error && <p className="text-red-600 text-sm mb-6">{error}</p>}

      {user ? (
        <div className="space-y-4">
          <p><strong>Username:</strong> {user.user_name}</p>
          <p><strong>Email:</strong> {user.email}</p>
          <div>
            <strong>Favorite Coins:</strong>
            <ul className="list-disc ml-6 mt-1">
              {user.favorite_coins.length > 0 ? (
                user.favorite_coins.map((symbol) => <li key={symbol}>{symbol}</li>)
              ) : (
                <li className="text-gray-500">None yet</li>
              )}
            </ul>
          </div>
        </div>
      ) : !error ? (
        <p>Loading...</p>
      ) : null}
    </div>
  );
}
