import { useState, useEffect } from "react";
import api from '@/api/axios';
import ReactMarkdown from "react-markdown";

const AIPredictions = () => {
  const [coin, setCoin] = useState("");
  const [coinList, setCoinList] = useState([]);
  const [timeframe, setTimeframe] = useState("1h");
  const [outputStyle, setOutputStyle] = useState("full");
  const [loading, setLoading] = useState(false);
  const [prediction, setPrediction] = useState(null);
  const [displayedPrediction, setDisplayedPrediction] = useState(null);


  // Fetch coin list
  useEffect(() => {
    api
      .get("/api/coins")
      .then((res) => setCoinList(res.data))
      .catch((err) => console.error("Error fetching coins:", err));
  }, []);

  // Handle prediction button
  const handlePrediction = async () => {
    if (!coin) return alert("Please select a coin.");
    setLoading(true);
    setPrediction(null);

    try {
      const res = await api.get("/predict", {
        params: {
          coin,
          timeframe,
          type: outputStyle,
        },
      });
      setPrediction(res.data);
      setDisplayedPrediction({
        ...res.data,
        _coin: coin,
        _timeframe: timeframe,
      });

      await api.post("/internal/emit-coin-data");

    } catch (err) {
      console.error("Prediction error:", err);
      setPrediction({ error: "Failed to fetch prediction." });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-5xl mx-auto text-gray-800 dark:text-gray-100">
      {/* Explanation */}
      <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6 shadow-sm text-center">
        <p className="text-lg text-gray-800 dark:text-gray-100 leading-relaxed">
          <strong className="text-blue-600 text-xl">Get AI-powered crypto predictions: buy, sell, or hold — in seconds.</strong><br />
          Select a coin, choose your timeframe (1h, 1d, or 1w), and pick your report type.
        </p>
        <ul className="mt-3 text-gray-700 dark:text-gray-300 text-base list-disc list-inside text-left inline-block text-start">
          <li><strong>Concise</strong>: A quick recommendation with 2 essential charts.</li>
          <li><strong>Full</strong>: A deep dive with all key indicators explained and 3 detailed charts.</li>
        </ul>
      </div>

      {/* Controls */}
      <div className="mt-10 flex flex-col md:flex-row gap-4 md:gap-0 justify-between items-center">
        {/* Coin dropdown */}
        <div className="flex-1">
          <select
            value={coin}
            onChange={(e) => setCoin(e.target.value)}
            className="rounded-md border border-gray-200 dark:border-gray-700 shadow-sm w-46 px-3 py-4 sm:py-2 bg-white text-gray-800 dark:bg-gray-800 dark:text-gray-100 focus:outline-none focus:ring-1 focus:ring-blue-600"
          >
            <option value="">Select a coin</option>
            {coinList.map((c) => (
              <option key={c.id} value={c.symbol}>
                {c.name} ({c.symbol})
              </option>
            ))}
          </select>
        </div>

        {/* Timeframe buttons */}
        <div className="flex gap-6 flex-1 justify-center">
          {["1h", "1d", "1w"].map((tf) => (
            <button
              key={tf}
              onClick={() => setTimeframe(tf)}
              className={`px-4 py-2 rounded-md border ${
                timeframe === tf
                  ? "bg-blue-600 text-white border border-gray-200 dark:border-gray-700 rounded-md border"
                  : "rounded-md border border-gray-200 dark:border-gray-700 shadow-sm p-4 bg-white dark:bg-gray-800"
              }`}
            >
              {tf}
            </button>
          ))}
        </div>

        {/* Output style toggle */}
        <div className="flex gap-3 flex-1 justify-end">
          {["full", "concise"].map((style) => (
            <button
              key={style}
              onClick={() => setOutputStyle(style)}
              className={`px-4 py-2 rounded-md border ${
                outputStyle === style
                  ? "bg-blue-600 text-white border border-gray-200 dark:border-gray-700 rounded-md border"
                  : "rounded-md border border-gray-200 dark:border-gray-700 shadow-sm p-4 bg-white dark:bg-gray-800"
              }`}
            >
              {style}
            </button>
          ))}
        </div>
      </div>

      {/* Get Prediction button */}
      <div className="mt-10 flex justify-center">
        <button
          className="px-8 py-3 text-lg bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
          onClick={handlePrediction}
          disabled={loading}
        >
          {loading ? "Analyzing..." : "Get Prediction"}
        </button>
      </div>

      {/* Prediction Output */}
      {displayedPrediction && (
        <div className="mt-8 bg-gray-50 dark:bg-gray-900 p-4 rounded-md border border-gray-200 dark:border-gray-700">
          {displayedPrediction.error ? (
            <p className="text-red-600">{displayedPrediction.error}</p>
          ) : (
            <div className="mt-8 bg-white dark:bg-gray-800 p-6 rounded-md border dark:border-gray-700 shadow-sm">
              <h2 className="text-3xl font-bold text-blue-600 text-center mb-4">
                {coinList.find((c) => c.symbol === displayedPrediction._coin)?.name || displayedPrediction._coin} {displayedPrediction._timeframe} prediction
              </h2>
              <div className="prose dark:prose-invert text-gray-800 dark:text-gray-100 max-w-none">
                  {console.log("RAW MARKDOWN:\n", displayedPrediction.analysis)}
                <ReactMarkdown
                    components={{
                        img: ({ alt, src }) => {

                            const chartUrls = {
                                "chart-price": `http://localhost:5050/chart/price/${displayedPrediction._coin}?timeframe=${displayedPrediction._timeframe}`,
                                "chart-macd-rsi": `http://localhost:5050/chart/macd-rsi/${displayedPrediction._coin}?timeframe=${displayedPrediction._timeframe}`,
                                "chart-bollinger": `http://localhost:5050/chart/bollinger/${displayedPrediction._coin}?timeframe=${displayedPrediction._timeframe}`,
                            };

                            const chartUrl = chartUrls[src?.trim()];
                            if (!chartUrl) return <p className="text-red-600"> Unknown chart: {src}</p>;

                            return (
                                <img
                                    src={chartUrl}
                                    alt={alt}
                                    className="my-6 rounded shadow-md border border-gray-300 dark:border-gray-600"
                                />
                            );
                        }
                    }}
                >
                    {displayedPrediction.analysis}
                </ReactMarkdown>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default AIPredictions;
