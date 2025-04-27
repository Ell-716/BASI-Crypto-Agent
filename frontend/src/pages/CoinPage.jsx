import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { io } from "socket.io-client";
import api from "@/api/axios";
import TradingViewWidget from "../components/TradingViewWidget";
import SparklineChart from "@/components/SparklineChart";

function CoinPage() {
  const { symbol } = useParams();
  const [coinStatic, setCoinStatic] = useState(null);
  const [liveCoin, setLiveCoin] = useState(null);
  const [sparklineData, setSparklineData] = useState([]);

  useEffect(() => {
    async function fetchCoinStaticData() {
      try {
        const res = await api.get(`/api/coins/symbol/${symbol}`);
        setCoinStatic(res.data);
      } catch (error) {
        console.error("Failed to fetch static coin data", error);
      }
    }
    fetchCoinStaticData();
  }, [symbol]);

  useEffect(() => {
    if (symbol) {
        api.get(`/dashboard/sparkline/${symbol}`)
          .then((res) => setSparklineData(res.data))
          .catch((err) => console.error("Sparkline fetch error:", err));
        }
    }, [symbol]);

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
      const match = data.find((c) => c.symbol === symbol);
      if (match) {
        setLiveCoin(match);
      }
    });

    socket.on("disconnect", () => {
      console.log("Disconnected from WebSocket");
    });

    return () => {
      if (socket.connected) socket.disconnect();
    };
  }, [symbol]);

  if (!coinStatic || !liveCoin) return <div className="text-center mt-10">Loading...</div>;

  return (
    <div className="max-w-7xl mx-auto px-6 py-8">
      <div className="flex flex-col lg:flex-row justify-between gap-10">
        {/* Left: Coin Info */}
        <div className="lg:w-[30%] space-y-6">
          <div className="flex items-center gap-2">
            <img src={coinStatic.image} alt={coinStatic.coin_name} className="w-10 h-10 object-contain" />
            <div className="flex items-baseline gap-2">
                <span className="text-2xl font-bold">{coinStatic.coin_name}</span>
                <span className="text-gray-500 dark:text-gray-400">{coinStatic.symbol.toUpperCase()}</span>
                <span className="text-gray-500 dark:text-gray-400">Price</span>
            </div>
          </div>
          {/* Live Price */}
          <p className="text-5xl font-bold text-gray-900 dark:text-white mt-">
            ${Number(liveCoin.current_price).toFixed(2).toLocaleString()}
          </p>

          <div className="space-y-3">
            <div className="flex justify-between bg-white border p-3 rounded-md text-black">
              <span className="font-bold">Market Cap:</span>
              <span>
                {liveCoin.market_cap ? `$${Number(liveCoin.market_cap).toLocaleString()}` : '—'}
              </span>
            </div>
            <div className="flex justify-between bg-white border p-3 rounded-md text-black">
              <span className="font-bold">24h Volume:</span>
              <span>
                {liveCoin.global_volume ? `$${Number(liveCoin.global_volume).toLocaleString()}` : '—'}
              </span>
            </div>
            <div className="flex justify-between bg-white border p-3 rounded-md text-black">
              <span className="font-bold">24h High:</span>
              <span>
                ${Number(liveCoin.high_24h).toFixed(2).toLocaleString()}
              </span>
            </div>
            <div className="flex justify-between bg-white border p-3 rounded-md text-black">
              <span className="font-bold">24h Low:</span>
              <span>
                ${Number(liveCoin.low_24h).toFixed(2).toLocaleString()}
              </span>
            </div>
            {/* Sparkline inside same block */}
            {sparklineData.length > 0 && (
              <div className="bg-white border p-3 rounded-md">
                <SparklineChart data={sparklineData} />
              </div>
            )}
          </div>
        </div>

        {/* Right: Chart */}
        <div className="lg:w-[65%]">
          <TradingViewWidget symbol={coinStatic.symbol} />
          <div className="text-left text-xs mt-2">
            Chart by <a href="https://www.tradingview.com" target="_blank" rel="noopener noreferrer" className="underline">TradingView</a>
          </div>
        </div>
      </div>

      {/* About Section */}
      <div className="mt-10 bg-white border p-6 rounded-md">
        <h2 className="text-2xl font-bold text-blue-600 mb-4">About {coinStatic.coin_name}</h2>
        <p className="text-black whitespace-pre-line">{coinStatic.description}</p>
      </div>
    </div>
  );
}

export default CoinPage;
