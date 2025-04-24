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
    <main className="bg-white min-h-screen px-6 sm:px-10 lg:px-16 xl:px-24 2xl:px-32 py-6 text-gray-800 max-w-[1600px] mx-auto">
      <h2 className="text-2xl font-semibold mb-4">Account Info</h2>
      <hr className="my-5 border-gray-300" />
      {error && <p className="text-red-600 text-sm mb-6">{error}</p>}

      {user ? (
        <>
          <div className="text-left space-y-4 mb-2">
            <p>
              <strong>Username:</strong> {user.user_name}
              <span className="ml-2 text-gray-400 hover:text-gray-600 cursor-pointer">✎</span>
            </p>
            <p>
              <strong>Email:</strong> {user.email}
              <span className="ml-2 text-gray-400 hover:text-gray-600 cursor-pointer">✎</span>
            </p>
            <div className="flex items-center gap-3 pt-2">
              <span className="font-medium"><strong>Mode:</strong></span>
              <button className="px-3 py-1 border rounded-l-full bg-gray-100 text-sm">Light</button>
              <button className="px-3 py-1 border rounded-r-full bg-gray-200 text-sm">Dark</button>
            </div>
          </div>

          <div className="mt-8">
            <button className="bg-blue-600 text-white px-5 py-2 rounded-md hover:bg-blue-700 transition">
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
    </main>
  );
}
