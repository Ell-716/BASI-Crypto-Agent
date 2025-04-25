import { useEffect } from "react";

function TradingViewWidget({ symbol }) {
  useEffect(() => {
    const script = document.createElement("script");
    script.src = "https://s3.tradingview.com/tv.js";
    script.async = true;
    script.onload = () => {
      new window.TradingView.widget({
        width: "100%",
        height: 610,
        symbol: `BINANCE:${symbol}USDT`,
        interval: "60",
        timezone: "Etc/UTC",
        theme: "dark",
        style: "1",
        locale: "en",
        toolbar_bg: "#f1f3f6",
        enable_publishing: false,
        hide_side_toolbar: false,
        container_id: "tradingview_container",
        studies: [
          "Moving Average@tv-basicstudies"
        ],
        studies_overrides: {
          "Moving Average@tv-basicstudies.length": 9,
          "Moving Average@tv-basicstudies.color": "#FFA500",
          "Moving Average@tv-basicstudies.plot.linewidth": 2
        }
      });
    };
    document.body.appendChild(script);
  }, [symbol]);

  return (
    <div className="tradingview-widget-container">
      <div id="tradingview_container"></div>
    </div>
  );
}

export default TradingViewWidget;
