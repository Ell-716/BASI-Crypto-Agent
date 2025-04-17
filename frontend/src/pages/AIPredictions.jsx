import { useState } from "react";

const AIPredictions = () => {
  const [coin, setCoin] = useState("");
  const [timeframe, setTimeframe] = useState("1h");
  const [outputStyle, setOutputStyle] = useState("full");

  return (
    <div className="p-6 max-w-5xl mx-auto">
      {/* Explanation */}
      <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm text-center">
        <p className="text-lg text-gray-800 leading-relaxed">
          <strong className="text-blue-600 text-xl">Get AI-powered crypto predictions: buy, sell, or hold — in seconds.</strong><br />
          Select a coin, choose your timeframe (1h, 1d, or 1w), and pick your report type.
        </p>
        <ul className="mt-3 text-gray-700 text-base list-disc list-inside text-left inline-block text-start">
          <li><strong>Concise</strong>: A quick recommendation with 2 essential charts.</li>
          <li><strong>Full</strong>: A deep dive with all key indicators explained and 3 detailed charts.</li>
        </ul>
      </div>

      {/* Controls */}
      <div className="mt-10 flex justify-between items-center">
        {/* Coin dropdown - moved left */}
        <div className="flex-1">
          <select
            value={coin}
            onChange={(e) => setCoin(e.target.value)}
            className="border rounded-md px-3 py-2 w-40"
          >
            <option value="">Select a coin</option>
            <option value="BTC">Bitcoin (BTC)</option>
            <option value="ETH">Ethereum (ETH)</option>
          </select>
        </div>

        {/* Timeframe buttons - centered */}
        <div className="flex gap-6 flex-1 justify-center">
          {["1h", "1d", "1w"].map((tf) => (
            <button
              key={tf}
              onClick={() => setTimeframe(tf)}
              className={`px-4 py-2 rounded-md border ${
                timeframe === tf ? "bg-blue-600 text-white" : "bg-white"
              }`}
            >
              {tf}
            </button>
          ))}
        </div>

        {/* Output style toggle - moved right */}
        <div className="flex gap-3 flex-1 justify-end">
          {["full", "concise"].map((style) => (
            <button
              key={style}
              onClick={() => setOutputStyle(style)}
              className={`px-4 py-2 rounded-md border ${
                outputStyle === style ? "bg-blue-600 text-white" : "bg-white"
              }`}
            >
              {style}
            </button>
          ))}
        </div>
      </div>

      {/* Get Prediction button */}
      <div className="mt-10 flex justify-center">
        <button className="px-8 py-3 text-lg bg-blue-600 text-white rounded-md hover:bg-blue-700">
          Get Prediction
        </button>
      </div>
    </div>
  );
};

export default AIPredictions;