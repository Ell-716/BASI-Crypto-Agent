import React, { useEffect, useState } from 'react';
import api from '@/api/axios';
import { jwtDecode } from 'jwt-decode';
import { io } from 'socket.io-client';
import { useTheme } from '../context/ThemeContext';
import { Link } from "react-router-dom";

export default function Account() {
  const [user, setUser] = useState(null);
  const [coins, setCoins] = useState([]);
  const [favorites, setFavorites] = useState([]);
  const [error, setError] = useState('');
  const [editingUsername, setEditingUsername] = useState(false);
  const [newUsername, setNewUsername] = useState('');
  const [confirmOpen, setConfirmOpen] = useState(false);
  const { darkMode, setDarkMode } = useTheme();

  const token = localStorage.getItem('access_token');
  let userId = null;
  if (token) {
    try {
      const decoded = jwtDecode(token);
      userId = decoded.sub;
    } catch {
      setError("Invalid token.");
    }
  }

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

  const toggleFavorite = async (symbol) => {
    const coin = coins.find(c => c.symbol === symbol);
    if (!coin || !userId) return;
    const coinId = coin.id;
    const isFavorite = favorites.includes(symbol);
    const payload = isFavorite ? { remove_coins: [coinId] } : { add_coins: [coinId] };

    try {
      await api.put(`/users/${userId}`, payload);
      setFavorites((prev) => isFavorite ? prev.filter((s) => s !== symbol) : [...prev, symbol]);
    } catch (err) {
      console.error("Failed to update favorites:", err);
    }
  };

  useEffect(() => {
    document.documentElement.classList.toggle('dark', darkMode);
    localStorage.setItem('theme', darkMode ? 'dark' : 'light');
  }, [darkMode]);

  useEffect(() => {
    if (!token || !userId) return;

    api.get(`/users/${userId}`)
      .then((res) => {
        setUser(res.data);
        setNewUsername(res.data.user_name);
        setFavorites(res.data.favorite_coins || []);
      })
      .catch((err) => {
        const msg = err.response?.data?.error || 'Failed to fetch user data';
        setError(msg);
      });
  }, []);

  useEffect(() => {
    const socket = io("http://localhost:5050", {
      transports: ["websocket"],
      path: "/socket.io",
      forceNew: true,
      reconnection: false
    });

    socket.on("connect", () => {
      socket.emit("request_coin_data");
    });

    socket.on("coin_data", (data) => {
      setCoins(data);
    });

    socket.on("disconnect", () => {
      console.log("Disconnected from WebSocket");
    });

    return () => {
      if (socket.connected) socket.disconnect();
    };
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
                  <input value={newUsername} onChange={(e) => setNewUsername(e.target.value)} className="border px-2 ml-2 rounded-sm" />
                  <button onClick={handleUsernameUpdate} className="ml-2 text-blue-600 hover:underline">Save</button>
                  <button onClick={() => setEditingUsername(false)} className="ml-2 text-gray-500 hover:underline">Cancel</button>
                </>
              ) : (
                <>
                  {user.user_name}
                  <span onClick={() => setEditingUsername(true)} className="material-icons text-gray-400 hover:text-gray-600 cursor-pointer text-base ml-2 align-middle">edit</span>
                </>
              )}
            </p>
            <p><strong>Email:</strong> {user.email}</p>
            <div className="flex items-center gap-3 pt-2">
              <span className="font-medium"><strong>Mode:</strong></span>
              <label className="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" checked={darkMode} onChange={() => setDarkMode(!darkMode)} className="sr-only peer" />
                <div className="w-11 h-6 bg-gray-200 rounded-full peer dark:bg-gray-700 peer-checked:bg-blue-600 transition-colors duration-300"></div>
                <div className="absolute left-1 top-1 w-4 h-4 bg-white rounded-full shadow-md transform transition-transform duration-300 peer-checked:translate-x-5"></div>
                <span className="ml-3 text-sm font-medium text-gray-900 dark:text-gray-300">{darkMode ? 'Dark' : 'Light'}</span>
              </label>
            </div>
          </div>

          <div className="mt-8">
            <button onClick={() => setConfirmOpen(true)} className="bg-blue-600 text-white px-5 py-2 rounded-md hover:bg-blue-700 transition">Delete account</button>
          </div>
        </>
      ) : !error ? <p>Loading...</p> : null}

      <hr className="my-5 border-gray-300" />

      <h2 className="text-2xl font-semibold mb-4">Favorite Coins</h2>
      <div className="overflow-x-auto mt-4">
        <table className="min-w-full text-sm text-left">
          <thead className="border-y border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800">
            <tr>
              <th className="px-2 py-3 font-bold text-black dark:text-white w-8"></th>
              <th className="px-4 py-3 font-bold text-black dark:text-white w-8">#</th>
              <th className="px-4 py-3 font-bold text-black dark:text-white min-w-[180px]">Coin</th>
              <th className="px-4 py-3 font-bold text-black dark:text-white text-right min-w-[120px]">Price</th>
              <th className="px-4 py-3 font-bold text-black dark:text-white text-right min-w-[120px]">24h High</th>
              <th className="px-4 py-3 font-bold text-black dark:text-white text-right min-w-[120px]">24h Low</th>
              <th className="px-4 py-3 font-bold text-black dark:text-white text-right min-w-[150px]">24h Volume</th>
              <th className="px-4 py-3 font-bold text-black dark:text-white text-right min-w-[150px]">Market Cap</th>
            </tr>
          </thead>
          <tbody>
            {coins.filter(c => favorites.includes(c.symbol)).map((coin, index) => (
              <tr key={coin.symbol} className="border-b border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800">
                <td className="px-2 py-4 text-center w-8">
                  <button onClick={() => toggleFavorite(coin.symbol)} className="text-yellow-400 text-lg focus:outline-none" title="Add to favorites">
                    {favorites.includes(coin.symbol) ? '★' : '☆'}
                  </button>
                </td>
                <td className="px-2 py-4 w-8">{index + 1}</td>
                <td className="px-4 py-4 min-w-[180px]">
                  <div className="flex items-center gap-2 h-full">
                    <img src={coin.image} alt={coin.name} className="w-6 h-6" />
                    <div className="flex flex-col sm:flex-row sm:gap-1 sm:items-center h-full">
                      <Link to={`/coin/${coin.symbol}`}>
                        <span className="font-semibold">{coin.name}</span>
                      </Link>
                      <span className="text-gray-500 dark:text-gray-400 text-xs sm:text-sm">{coin.symbol}</span>
                    </div>
                  </div>
                </td>
                <td className="px-4 py-4 text-right min-w-[120px]">${parseFloat(coin.current_price).toLocaleString()}</td>
                <td className="px-4 py-4 text-right min-w-[120px]">${parseFloat(coin.high_24h).toLocaleString()}</td>
                <td className="px-4 py-4 text-right min-w-[120px]">${parseFloat(coin.low_24h).toLocaleString()}</td>
                <td className="px-4 py-4 text-right min-w-[150px]">{coin.global_volume ? `$${parseFloat(coin.global_volume).toLocaleString()}` : '—'}</td>
                <td className="px-4 py-4 text-right min-w-[150px]">{coin.market_cap ? `$${parseFloat(coin.market_cap).toLocaleString()}` : '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {confirmOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-xl shadow-md w-80 text-center">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Delete Account?</h3>
            <p className="text-sm text-gray-600 mb-6">This action cannot be undone.</p>
            <div className="flex justify-center gap-4">
              <button onClick={handleDeleteAccount} className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700">Delete</button>
              <button onClick={() => setConfirmOpen(false)} className="bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-100 px-4 py-2 rounded hover:bg-gray-300 dark:hover:bg-gray-600">Cancel</button>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
