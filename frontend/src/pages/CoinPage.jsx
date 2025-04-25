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
    <div className="p-6 text-white">
      {/* Top section */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold">{coinData.coin_name} ({coinData.symbol})</h1>
        <p className="text-xl mt-2">Current Price: ${coinData.price}</p>
        <div className="flex gap-8 mt-4">
          <p>Market Cap: ${coinData.market_cap || "N/A"}</p>
          <p>24h Volume: ${coinData.volume || "N/A"}</p>
        </div>
      </div>

      {/* Chart */}
      <div className="mb-10">
        <TradingViewWidget symbol={coinData.symbol} />
      </div>

      {/* Description */}
      <div className="bg-gray-800 p-6 rounded-md shadow-md">
        <h2 className="text-2xl font-semibold mb-4">About {coinData.coin_name}</h2>
        <p className="text-gray-300 whitespace-pre-line">{coinData.description}</p>
      </div>
    </div>
  );
}

export default CoinPage;
