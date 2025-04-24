import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { jwtDecode } from 'jwt-decode';

export default function Account() {
  const [user, setUser] = useState(null);
  const [error, setError] = useState('');

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

    axios
      .get(`http://localhost:5050/users/${userId}`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      .then((res) => setUser(res.data))
      .catch((err) => {
        const msg = err.response?.data?.error || 'Failed to fetch user data';
        setError(msg);
      });
  }, []);

  return (
    <div className="min-h-screen px-6 py-10 bg-white text-gray-800">
      <h1 className="text-3xl font-bold mb-6">Your Account</h1>
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
