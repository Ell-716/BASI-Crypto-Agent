import { useEffect, useState } from "react";

const FearGreedMeter = ({ value, classification }) => {
  const angle = (value / 100) * 180;

  const getColor = (label) => {
    switch (label.toLowerCase()) {
      case "extreme fear":
        return "#dc2626"; // red
      case "fear":
        return "#f97316"; // orange
      case "neutral":
        return "#6b7280"; // gray-500
      case "greed":
        return "#84cc16"; // lime
      case "extreme greed":
        return "#22c55e"; // green
      default:
        return "#000000"; // fallback black
    }
  };

  return (
    <div className="flex flex-col items-center p-4">
      <svg viewBox="0 0 200 120" className="w-64 h-36">
        <defs>
          <linearGradient id="fgi-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#dc2626" />
            <stop offset="25%" stopColor="#f97316" />
            <stop offset="50%" stopColor="#eab308" />
            <stop offset="75%" stopColor="#84cc16" />
            <stop offset="100%" stopColor="#22c55e" />
          </linearGradient>
        </defs>
        <path
          d="M 10 110 A 90 90 0 0 1 190 110"
          fill="none"
          stroke="url(#fgi-gradient)"
          strokeWidth="20"
        />
        <line
          x1="100"
          y1="110"
          x2={100 - 80 * Math.cos((angle * Math.PI) / 180)}
          y2={110 - 80 * Math.sin((angle * Math.PI) / 180)}
          stroke="#000"
          strokeWidth="3"
          strokeLinecap="round"
          style={{
            transition: "all 0.8s ease-in-out"
          }}
        />
        <circle cx="100" cy="110" r="5" fill="#000" />
      </svg>

      <div className="text-center mt-3">
        <div className="text-xl font-bold" style={{ color: getColor(classification) }}>
          {classification}
        </div>
        <div className="text-sm text-gray-500 mt-1">Score: {value}</div>
      </div>
    </div>
  );
};

export default FearGreedMeter;
