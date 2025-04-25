import { useEffect, useState } from "react";
import api from '@/api/axios';
import FearGreedMeter from "@/components/FearGreedMeter";
import { io } from "socket.io-client";
import SparklineChart from "@/components/SparklineChart";


const Home = () => {
  const [topVolume, setTopVolume] = useState(null);
  const [fearGreed, setFearGreed] = useState(null);
  const [coins, setCoins] = useState([]);
  const [favorites, setFavorites] = useState([]);
  const [sparklineData, setSparklineData] = useState([]);
  const [snapshot, setSnapshot] = useState(null);

  const topCoinData = coins.find((coin) => coin.symbol === topVolume?.symbol);
  console.log("[RENDER] Home component rendered with", coins.length, "coins");


    const toggleFavorite = (symbol) => {
        setFavorites((prev) =>
            prev.includes(symbol)
            ? prev.filter((s) => s !== symbol)
            : [...prev, symbol]
        );
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
        api
        .get(`/dashboard/sparkline/${topVolume.symbol}`)
        .then((res) => setSparklineData(res.data))
        .catch((err) => console.error("Sparkline fetch error:", err));
    }
  }, [topVolume]);

  // Fetch the CoinSnapshot
  useEffect(() => {
      if (topVolume?.symbol) {
          api
            .get(`http://localhost:5050/dashboard/snapshot/${topVolume.symbol}`)
            .then((res) => setSnapshot(res.data))
            .catch((err) => console.error("Snapshot fetch error:", err));
      }
  }, [topVolume]);

  // Update coin data every minute
  useEffect(() => {
    console.log("[WS] useEffect triggered");

    const socket = io("http://localhost:5050", {
        transports: ["websocket"],
        path: "/socket.io",
        forceNew: true,
        reconnection: false
    });

    socket.on("connect", () => {
        console.log("Connected to WebSocket");
        socket.emit("request_coin_data");
    });

    socket.off("coin_data");
    socket.on("coin_data", (data) => {
        console.log("🔁 Updating state with", data.length, "coins");
        setCoins(data);
    });

    socket.on("disconnect", () => {
        console.log("Disconnected from WebSocket");
    });

    return () => {
        if (socket.connected) {
            console.log("[WS] Cleanup socket");
            socket.disconnect();
        }
    };
}, []);

  return (
    <main className="bg-white dark:bg-gray-900 min-h-screen px-6 sm:px-10 lg:px-16 xl:px-24 2xl:px-32 py-6 text-gray-800 dark:text-gray-100 max-w-[1600px] mx-auto">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-10">
        <div className="rounded-md border border-gray-200 dark:border-gray-700 shadow-sm p-4 bg-white dark:bg-gray-800">
          <h2 className="text-xl font-semibold text-center mb-4">Highest 24h trading volume</h2>
          {topVolume && (
            <div className="text-center">
                <div className="flex items-center justify-center gap-2 text-center text-1xl mb-2">
                    <img
                        src={topVolume.image}
                        alt={topVolume.coin_name}
                        className="w-8 h-8"
                    />
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

        <div className="rounded-md border border-gray-200 dark:border-gray-700 shadow-sm p-4 bg-white dark:bg-gray-800">
          <h2 className="text-xl font-semibold text-center mb-4">Fear & Greed Index</h2>
          {fearGreed ? (
            <FearGreedMeter
              value={fearGreed.value}
              classification={fearGreed.classification}
            />
          ) : (
            <p>Loading...</p>
          )}
        </div>
      </div>

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
                <td className="px-4 py-4 min-w-[180px]">
                    <div className="flex items-center gap-2 h-full">
                        <img src={coin.image} alt={coin.name} className="w-6 h-6" />
                        <div className="flex flex-col sm:flex-row sm:gap-1 sm:items-center h-full">
                            <span className="font-semibold">{coin.name}</span>
                            <span className="text-gray-500 dark:text-gray-400 text-xs sm:text-sm">{coin.symbol}</span>
                        </div>
                    </div>
                </td>
                <td className="px-4 py-4 text-right min-w-[120px]">
                  ${parseFloat(coin.current_price).toLocaleString()}
                </td>
                <td className="px-4 py-4 text-right min-w-[120px]">
                  ${parseFloat(coin.high_24h).toLocaleString()}
                </td>
                <td className="px-4 py-4 text-right min-w-[120px]">
                  ${parseFloat(coin.low_24h).toLocaleString()}
                </td>
                <td className="px-4 py-4 text-right min-w-[150px]">
                  {coin.global_volume ? `$${parseFloat(coin.global_volume).toLocaleString()}` : '—'}
                </td>
                <td className="px-4 py-4 text-right min-w-[150px]">
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
