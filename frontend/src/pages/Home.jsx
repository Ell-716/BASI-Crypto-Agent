import { useEffect, useState } from "react";
import api from '@/api/axios';
import FearGreedMeter from "@/components/FearGreedMeter";
import { io } from "socket.io-client";
import SparklineChart from "@/components/SparklineChart";
import { jwtDecode } from 'jwt-decode';
import { Link } from "react-router-dom";

const Home = () => {
  // State for dashboard widgets
  const [topVolume, setTopVolume] = useState(null);
  const [fearGreed, setFearGreed] = useState(null);
  const [coins, setCoins] = useState([]);
  const [favorites, setFavorites] = useState([]);
  const [sparklineData, setSparklineData] = useState([]);
  const [snapshot, setSnapshot] = useState(null);

  // Extract user ID from JWT token
  const token = localStorage.getItem('access_token');
  let userId = null;
  if (token) {
    try {
      const decoded = jwtDecode(token);
      userId = decoded.sub;
    } catch {
      console.error("Invalid token");
    }
  }

  // Find live price data for top volume coin
  const topCoinData = coins.find((coin) => coin.symbol === topVolume?.symbol);

  // Toggle favorite status for a coin
  const toggleFavorite = async (symbol) => {
    const coin = coins.find(c => c.symbol === symbol);
    if (!coin || !userId) {
      console.warn("Missing coin or userId", { coin, userId });
      return;
    }

    const coinId = coin.id;
    const isFavorite = favorites.includes(symbol);
    console.log("Toggle favorite:", { symbol, isFavorite, coinId });

    // Build request payload
    const payload = isFavorite
      ? { remove_coins: [coinId] }
      : { add_coins: [coinId] };

    try {
      await api.put(`/users/${userId}`, payload);
      setFavorites((prev) =>
        isFavorite
          ? prev.filter((s) => s !== symbol)
          : [...prev, symbol]
      );
    } catch (err) {
      console.error("Failed to update favorites:", err);
    }
  };

  // Fetch static dashboard data once on mount
  useEffect(() => {
    const fetchStaticData = async () => {
      try {
        const [volumeRes, fearGreedRes] = await Promise.all([
          api.get("/dashboard/top-volume"),
          api.get("/dashboard/fear-greed"),
        ]);
        setTopVolume(volumeRes.data);
        setFearGreed(fearGreedRes.data);
      } catch (error) {
        console.error("Error fetching static dashboard data:", error);
      }
    };
    fetchStaticData();
  }, []);

  // Fetch sparkline data when top volume coin changes
  useEffect(() => {
    if (topVolume?.symbol) {
      api.get(`/dashboard/sparkline/${topVolume.symbol}`)
        .then((res) => setSparklineData(res.data))
        .catch((err) => console.error("Sparkline fetch error:", err));
    }
  }, [topVolume]);

  // Fetch market snapshot when top volume coin changes
  useEffect(() => {
    if (topVolume?.symbol) {
      api.get(`/dashboard/snapshot/${topVolume.symbol}`)
        .then((res) => setSnapshot(res.data))
        .catch((err) => console.error("Snapshot fetch error:", err));
    }
  }, [topVolume]);

  // Load user's favorite coins
  useEffect(() => {
    if (!userId) return;
    api.get(`/users/${userId}`)
      .then((res) => setFavorites(res.data.favorite_coins || []))
      .catch((err) => console.error("Failed to load favorites:", err));
  }, [userId]);

  // WebSocket connection for real-time coin price updates
  useEffect(() => {
    let hasReceivedData = false;
    let fallbackTimer = null;

    // Initialize WebSocket connection
    const socket = io(import.meta.env.VITE_SOCKET_URL || 'http://localhost:5050', {
      transports: ["websocket"],
      path: "/socket.io",
      forceNew: true,
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionAttempts: 5
    });

    socket.on("connect", () => {
      console.log("WebSocket connected");
      socket.emit("request_coin_data");

      // Fallback to REST API if WebSocket doesn't respond
      fallbackTimer = setTimeout(async () => {
        if (!hasReceivedData) {
          console.log("WebSocket timeout, falling back to REST API");
          try {
            const res = await api.get("/api/coins");
            if (res.data && res.data.length > 0) {
              setCoins(res.data);
              console.log("Loaded coin data from REST API fallback");
            }
          } catch (err) {
            console.error("REST fallback failed:", err);
          }
        }
      }, 5000);
    });

    // Handle incoming coin data from WebSocket
    socket.on("coin_data", (data) => {
      hasReceivedData = true;
      if (fallbackTimer) {
        clearTimeout(fallbackTimer);
      }
      setCoins(data);
      console.log("Received coin data update:", data.length, "coins");
    });

    socket.on("disconnect", () => {
      console.log("Disconnected from WebSocket");
    });

    // Cleanup on unmount
    return () => {
      if (fallbackTimer) clearTimeout(fallbackTimer);
      socket.disconnect();
    };
  }, []);

  return (
    <main className="bg-white dark:bg-gray-900 min-h-screen px-6 sm:px-10 lg:px-16 xl:px-24 2xl:px-32 py-6 text-gray-800 dark:text-gray-100 max-w-[1600px] mx-auto">
      {/* Dashboard widgets - Top Volume & Fear/Greed */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-10">
        {/* Top 24h Volume Widget */}
        <div className="rounded-md border border-gray-200 dark:border-gray-700 shadow-sm p-4 bg-white dark:bg-gray-800">
          <h2 className="text-xl font-semibold text-center mb-4">Highest 24h trading volume</h2>
          {topVolume && (
            <div className="text-center">
              <div className="flex items-center justify-center gap-2 mb-2">
                <img src={topVolume.image} alt={topVolume.coin_name} className="w-8 h-8" />
                <span className="font-bold">{topVolume.coin_name}</span>
                <span className="text-gray-500 dark:text-gray-400">{topVolume.symbol}</span>
                <span className="text-gray-500 dark:text-gray-400">Price</span>
              </div>
              {topCoinData && (
                <div className="text-5xl font-bold text-gray-900 dark:text-white mt-2">
                  ${topCoinData.current_price.toLocaleString()}
                </div>
              )}
              {sparklineData.length > 0 && (
                <div className="mt-4">
                  <SparklineChart data={sparklineData} />
                </div>
              )}
            </div>
          )}
        </div>

        {/* Fear & Greed Index Widget */}
        <div className="rounded-md border border-gray-200 dark:border-gray-700 shadow-sm p-4 bg-white dark:bg-gray-800">
          <h2 className="text-xl font-semibold text-center mb-4">Fear & Greed Index</h2>
          {fearGreed ? (
            <FearGreedMeter value={fearGreed.value} classification={fearGreed.classification} />
          ) : null}
        </div>
      </div>

      {/* Cryptocurrency Table */}
      <div className="overflow-x-auto mt-4">
        <table className="min-w-full text-sm text-left">
          <thead className="border-y border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800">
            <tr>
              <th className="px-2 py-3 font-bold text-black dark:text-white w-8"></th> {/* Favorite star */}
              <th className="px-2 py-3 font-bold text-black dark:text-white w-8">#</th> {/* Rank */}
              <th className="px-2 sm:px-4 py-3 font-bold text-black dark:text-white">Coin</th>
              <th className="px-2 sm:px-4 py-3 font-bold text-black dark:text-white text-right">Price</th>
              <th className="hidden sm:table-cell px-4 py-3 font-bold text-black dark:text-white text-right min-w-[120px]">24h High</th>
              <th className="hidden sm:table-cell px-4 py-3 font-bold text-black dark:text-white text-right min-w-[120px]">24h Low</th>
              <th className="hidden md:table-cell px-4 py-3 font-bold text-black dark:text-white text-right min-w-[150px]">24h Volume</th>
              <th className="hidden lg:table-cell px-4 py-3 font-bold text-black dark:text-white text-right min-w-[150px]">Market Cap</th>
            </tr>
          </thead>
          <tbody>
            {coins.map((coin, index) => (
              <tr key={coin.symbol} className="border-b border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800">
                <td className="px-2 py-4 text-center w-8">
                  <button
                    onClick={() => toggleFavorite(coin.symbol)}
                    className="text-yellow-400 text-lg focus:outline-none"
                    title="Add to favorites"
                  >
                    {favorites.includes(coin.symbol) ? "★" : "☆"}
                  </button>
                </td>
                <td className="px-2 py-4 w-8">{index + 1}</td>
                <td className="px-2 sm:px-4 py-4">
                  <div className="flex items-center gap-2 h-full">
                    <img src={coin.image} alt={coin.name} className="w-6 h-6 shrink-0" />
                    <div className="flex flex-col sm:flex-row sm:gap-1 sm:items-center h-full">
                      <Link to={`/coin/${coin.symbol}`}>
                        <span className="font-semibold">{coin.name}</span>
                      </Link>
                      <span className="text-gray-500 dark:text-gray-400 text-xs sm:text-sm">{coin.symbol}</span>
                    </div>
                  </div>
                </td>
                <td className="px-2 sm:px-4 py-4 text-right whitespace-nowrap">
                  ${parseFloat(coin.current_price).toLocaleString()}
                </td>
                <td className="hidden sm:table-cell px-4 py-4 text-right min-w-[120px]">${parseFloat(coin.high_24h).toLocaleString()}</td>
                <td className="hidden sm:table-cell px-4 py-4 text-right min-w-[120px]">${parseFloat(coin.low_24h).toLocaleString()}</td>
                <td className="hidden md:table-cell px-4 py-4 text-right min-w-[150px]">
                  {coin.global_volume ? `$${parseFloat(coin.global_volume).toLocaleString()}` : '—'}
                </td>
                <td className="hidden lg:table-cell px-4 py-4 text-right">
                  {coin.market_cap ? `$${parseFloat(coin.market_cap).toLocaleString()}` : '—'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </main>
  );
};

export default Home;
