import { useEffect, useState } from "react";
import axios from "axios";

const Home = () => {
  const [topVolume, setTopVolume] = useState(null);
  const [fearGreed, setFearGreed] = useState(null);
  const [coins, setCoins] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [volumeRes, fearGreedRes, coinsRes] = await Promise.all([
          axios.get("http://localhost:5000/dashboard/top-volume"),
          axios.get("http://localhost:5000/dashboard/fear-greed"),
          axios.get("http://localhost:5000/dashboard/coins"),
        ]);
        setTopVolume(volumeRes.data);
        setFearGreed(fearGreedRes.data);
        setCoins(coinsRes.data);
      } catch (error) {
        console.error("Error fetching dashboard data:", error);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 60000); // update every 1 minute
    return () => clearInterval(interval);
  }, []);

  return (
    <main className="bg-white min-h-screen p-6 text-gray-800">
      {/* Top section */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-10">
        <div className="rounded-md border shadow-sm p-4 bg-white">
          <h2 className="text-lg font-semibold text-center mb-4">Highest 24h trading volume</h2>
          {topVolume && (
            <div className="text-center">
              <p className="text-2xl font-bold">{topVolume.coin_name} {topVolume.symbol}</p>
              <p className="text-4xl text-blue-600 mt-2">${parseFloat(topVolume.price).toLocaleString()}</p>
            </div>
          )}
        </div>

        <div className="rounded-md border shadow-sm p-4 bg-white text-center">
          <h2 className="text-lg font-semibold mb-4">Fear & Greed Index</h2>
          {fearGreed ? (
            <div className="flex flex-col items-center">
              <div className="w-36 h-36 bg-gray-100 flex items-center justify-center rounded-full text-xl font-bold text-green-600">
                {fearGreed.classification}
              </div>
              <p className="mt-2 text-sm text-gray-500">Score: {fearGreed.value}</p>
            </div>
          ) : (
            <p>Loading...</p>
          )}
        </div>
      </div>

      {/* Table section */}
      <div className="overflow-x-auto mt-4">
        <table className="min-w-full text-sm text-left">
          <thead className="border-y border-gray-300 bg-white text-gray-600 font-medium">
            <tr>
                <th className="px-4 py-3">#</th>
                <th className="px-4 py-3">Coin</th>
                <th className="px-4 py-3">Price</th>
                <th className="px-4 py-3">24h High</th>
                <th className="px-4 py-3">24h Low</th>
                <th className="px-4 py-3">24h Volume</th>
                <th className="px-4 py-3">Market Cap</th>
            </tr>
          </thead>
          <tbody>
            {coins.map((coin, index) => (
                <tr key={coin.symbol} className="border-b border-gray-200">
                    <td className="px-4 py-2">{index + 1}</td>
                    <td className="px-4 py-2 flex items-center gap-2">
                        <img src={coin.image} alt={coin.name} className="w-5 h-5" />
                        {coin.name} {coin.symbol}
                    </td>
                    <td className="px-4 py-2">${parseFloat(coin.price).toLocaleString()}</td>
                    <td className="px-4 py-2">${parseFloat(coin.high_24h).toLocaleString()}</td>
                    <td className="px-4 py-2">${parseFloat(coin.low_24h).toLocaleString()}</td>
                    <td className="px-4 py-2">${parseFloat(coin.total_volume).toLocaleString()}</td>
                    <td className="px-4 py-2">${parseFloat(coin.market_cap).toLocaleString()}</td>
                    </tr>
                ))}
          </tbody>
        </table>
      </div>
    </main>
  );
};

export default Home;
