import { useEffect, useState } from "react";
import api from '@/api/axios';
import FearGreedMeter from "@/components/FearGreedMeter";
import { io } from "socket.io-client";
import SparklineChart from "@/components/SparklineChart";
import { jwtDecode } from 'jwt-decode';
import { Link } from "react-router-dom";

const Home = () => {
  const [topVolume, setTopVolume] = useState(null);
  const [fearGreed, setFearGreed] = useState(null);
  const [coins, setCoins] = useState([]);
  const [favorites, setFavorites] = useState([]);
  const [sparklineData, setSparklineData] = useState([]);
  const [snapshot, setSnapshot] = useState(null);

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

  const topCoinData = coins.find((coin) => coin.symbol === topVolume?.symbol);

  const toggleFavorite = async (symbol) => {
    const coin = coins.find(c => c.symbol === symbol);
    if (!coin || !userId) {
      console.warn("Missing coin or userId", { coin, userId });
      return;
    }

    const coinId = coin.id;
    const isFavorite = favorites.includes(symbol);
    console.log("Toggle favorite:", { symbol, isFavorite, coinId });

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

  // Fetch fear & greed and top volume once
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

  useEffect(() => {
    if (topVolume?.symbol) {
      api.get(`/dashboard/sparkline/${topVolume.symbol}`)
        .then((res) => setSparklineData(res.data))
        .catch((err) => console.error("Sparkline fetch error:", err));
    }
  }, [topVolume]);

  useEffect(() => {
    if (topVolume?.symbol) {
      api.get(`/dashboard/snapshot/${topVolume.symbol}`)
        .then((res) => setSnapshot(res.data))
        .catch((err) => console.error("Snapshot fetch error:", err));
    }
  }, [topVolume]);

  // Fetch user favorites
  useEffect(() => {
    if (!userId) return;
    api.get(`/users/${userId}`)
      .then((res) => setFavorites(res.data.favorite_coins || []))
      .catch((err) => console.error("Failed to load favorites:", err));
  }, [userId]);

  // WebSocket for live updates
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

    socket.off("coin_data");
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

  return (
    <main className="bg-white dark:bg-gray-900 min-h-screen px-4 sm:px-6 md:px-8 lg:px-10 py-6 text-gray-800 dark:text-gray-100 max-w-[1600px] mx-auto">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6 mb-6 md:mb-10">
        <div className="rounded-md border border-gray-200 dark:border-gray-700 shadow-sm p-4 bg-white dark:bg-gray-800">
          <h2 className="text-lg md:text-xl font-semibold text-center mb-3 md:mb-4">Highest 24h trading volume</h2>
          {topVolume && (
            <div className="text-center">
              <div className="flex items-center justify-center gap-2 mb-2">
                <img src={topVolume.image} alt={topVolume.coin_name} className="w-6 h-6 md:w-8 md:h-8" />
                <span className="font-bold text-sm md:text-base">{topVolume.coin_name}</span>
                <span className="text-gray-500 dark:text-gray-400 text-xs md:text-sm">{topVolume.symbol}</span>
              </div>
              {topCoinData && (
                <div className="text-3xl md:text-5xl font-bold text-gray-900 dark:text-white mt-2">
                  ${topCoinData.current_price.toLocaleString()}
                </div>
              )}
              {sparklineData.length > 0 && (
                <div className="mt-3 md:mt-4 h-[80px] md:h-[100px]">
                  <SparklineChart data={sparklineData} />
                </div>
              )}
            </div>
          )}
        </div>

        <div className="rounded-md border border-gray-200 dark:border-gray-700 shadow-sm p-4 bg-white dark:bg-gray-800">
          <h2 className="text-lg md:text-xl font-semibold text-center mb-3 md:mb-4">Fear & Greed Index</h2>
          {fearGreed ? (
            <div className="scale-90 md:scale-100">
              <FearGreedMeter value={fearGreed.value} classification={fearGreed.classification} />
            </div>
          ) : null}
        </div>
      </div>

      <div className="overflow-x-auto mt-4">
        <table className="min-w-full text-sm">
          <thead className="border-y border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800">
            <tr>
              <th className="px-1 py-2 md:px-2 md:py-3 font-bold text-black dark:text-white w-6 md:w-8"></th>
              <th className="px-1 py-2 md:px-2 md:py-3 font-bold text-black dark:text-white w-6 md:w-8">#</th>
              <th className="px-2 py-2 md:px-4 md:py-3 font-bold text-black dark:text-white text-left min-w-[120px]">Coin</th>
              <th className="px-2 py-2 md:px-4 md:py-3 font-bold text-black dark:text-white text-right min-w-[80px] md:min-w-[100px]">Price</th>
              {/* Hidden columns on mobile */}
              <th className="hidden sm:table-cell px-2 py-2 md:px-4 md:py-3 font-bold text-black dark:text-white text-right min-w-[80px] md:min-w-[100px]">24h High</th>
              <th className="hidden sm:table-cell px-2 py-2 md:px-4 md:py-3 font-bold text-black dark:text-white text-right min-w-[80px] md:min-w-[100px]">24h Low</th>
              <th className="hidden md:table-cell px-4 py-3 font-bold text-black dark:text-white text-right min-w-[120px]">24h Volume</th>
              <th className="hidden lg:table-cell px-4 py-3 font-bold text-black dark:text-white text-right min-w-[120px]">Market Cap</th>
            </tr>
          </thead>
          <tbody>
            {coins.map((coin, index) => (
              <tr key={coin.symbol} className="border-b border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800">
                <td className="px-1 py-3 text-center w-6 md:w-8">
                  <button
                    onClick={() => toggleFavorite(coin.symbol)}
                    className="text-yellow-400 text-base md:text-lg focus:outline-none"
                    title="Add to favorites"
                  >
                    {favorites.includes(coin.symbol) ? "★" : "☆"}
                  </button>
                </td>
                <td className="px-1 py-3 w-6 md:w-8 text-sm">{index + 1}</td>
                <td className="px-2 py-3 min-w-[120px]">
                  <div className="flex items-center gap-2">
                    <img src={coin.image} alt={coin.name} className="w-5 h-5 md:w-6 md:h-6" />
                    <div className="flex flex-col sm:flex-row sm:gap-1 sm:items-baseline">
                      <Link to={`/coin/${coin.symbol}`} className="font-semibold text-sm md:text-base">
                        {coin.name}
                      </Link>
                      <span className="text-gray-500 dark:text-gray-400 text-xs">{coin.symbol}</span>
                    </div>
                  </div>
                </td>
                <td className="px-2 py-3 text-right text-sm md:text-base min-w-[80px] md:min-w-[100px]">
                  ${parseFloat(coin.current_price).toLocaleString()}
                </td>
                {/* Hidden columns on mobile */}
                <td className="hidden sm:table-cell px-2 py-3 text-right text-sm md:text-base min-w-[80px] md:min-w-[100px]">
                  ${parseFloat(coin.high_24h).toLocaleString()}
                </td>
                <td className="hidden sm:table-cell px-2 py-3 text-right text-sm md:text-base min-w-[80px] md:min-w-[100px]">
                  ${parseFloat(coin.low_24h).toLocaleString()}
                </td>
                <td className="hidden md:table-cell px-4 py-3 text-right">
                  {coin.global_volume ? `$${parseFloat(coin.global_volume).toLocaleString()}` : '—'}
                </td>
                <td className="hidden lg:table-cell px-4 py-3 text-right">
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
