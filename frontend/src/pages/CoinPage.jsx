import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import api from "@/api/axios";
import TradingViewWidget from "../components/TradingViewWidget";

function CoinPage() {
  const { symbol } = useParams(); // BTC, ETH, etc.
  const [coinData, setCoinData] = useState(null);

  useEffect(() => {
    async function fetchCoinData() {
      try {
        const res = await api.get(`/api/coins/symbol/${symbol}`);
        setCoinData(res.data);
      } catch (error) {
        console.error("Failed to fetch coin data", error);
      }
    }
    fetchCoinData();
  }, [symbol]);

  if (!coinData) return <div className="text-center text-white mt-10">Loading...</div>;

  return (
    <div className="max-w-7xl mx-auto px-6 py-8 text-white">
      {/* Top: Info + Chart side-by-side */}
      <div className="flex flex-col lg:flex-row gap-8">
        {/* Left: Coin Info */}
          <div className="lg:w-1/3 space-y-4">
            <h1 className="text-3xl font-bold">{coinData.coin_name} ({coinData.symbol})</h1>
            <p className="text-4xl font-semibold text-green-400">${coinData.price}</p>

            <div className="space-y-2">
              <div className="bg-gray-800 p-3 rounded-md shadow-sm">Market Cap: ${coinData.market_cap}</div>
              <div className="bg-gray-800 p-3 rounded-md shadow-sm">24h Volume: ${coinData.global_volume}</div>
              <div className="bg-gray-800 p-3 rounded-md shadow-sm">24h High: ${coinData.high}</div>
              <div className="bg-gray-800 p-3 rounded-md shadow-sm">24h Low: ${coinData.low}</div>
            </div>
          </div>

          {/* Right: Chart */}
          <div className="lg:w-2/3">
            <TradingViewWidget symbol={coinData.symbol} />
        </div>
      </div>

      {/* Bottom: Description */}
      <div className="mt-10 bg-gray-800 p-6 rounded-md shadow-md">
        <h2 className="text-2xl font-semibold mb-4">About {coinData.coin_name}</h2>
        <p className="text-gray-300 whitespace-pre-line">{coinData.description}</p>
      </div>
    </div>
  );
}

export default CoinPage;
