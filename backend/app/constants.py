# Single source of truth for all supported coins.
# Update this list if you want to add or remove coins.
# Each coin must have a corresponding Binance USDT pair and CoinGecko ID.

COINS = [
    {
        "binance_symbol": "BTCUSDT",
        "symbol": "BTC",
        "name": "Bitcoin",
        "coingecko_id": "bitcoin",
        "image": "https://assets.coingecko.com/coins/images/1/large/bitcoin.png"
    },
    {
        "binance_symbol": "ETHUSDT",
        "symbol": "ETH",
        "name": "Ethereum",
        "coingecko_id": "ethereum",
        "image": "https://assets.coingecko.com/coins/images/279/large/ethereum.png"
    },
    {
        "binance_symbol": "BNBUSDT",
        "symbol": "BNB",
        "name": "BNB",
        "coingecko_id": "binancecoin",
        "image": "https://assets.coingecko.com/coins/images/825/large/bnb-icon2_2x.png"
    },
    {
        "binance_symbol": "SOLUSDT",
        "symbol": "SOL",
        "name": "Solana",
        "coingecko_id": "solana",
        "image": "https://assets.coingecko.com/coins/images/4128/large/solana.png"
    },
    {
        "binance_symbol": "XRPUSDT",
        "symbol": "XRP",
        "name": "XRP",
        "coingecko_id": "ripple",
        "image": "https://assets.coingecko.com/coins/images/44/large/xrp-symbol-white-128.png"
    },
    {
        "binance_symbol": "ADAUSDT",
        "symbol": "ADA",
        "name": "Cardano",
        "coingecko_id": "cardano",
        "image": "https://assets.coingecko.com/coins/images/975/large/cardano.png"
    },
    {
        "binance_symbol": "AVAXUSDT",
        "symbol": "AVAX",
        "name": "Avalanche",
        "coingecko_id": "avalanche-2",
        "image": "https://assets.coingecko.com/coins/images/12559/large/coin-round-red.png"
    },
    {
        "binance_symbol": "DOGEUSDT",
        "symbol": "DOGE",
        "name": "Dogecoin",
        "coingecko_id": "dogecoin",
        "image": "https://assets.coingecko.com/coins/images/5/large/dogecoin.png"
    },
    {
        "binance_symbol": "DOTUSDT",
        "symbol": "DOT",
        "name": "Polkadot",
        "coingecko_id": "polkadot",
        "image": "https://assets.coingecko.com/coins/images/12171/large/polkadot.png"
    },
    {
        "binance_symbol": "LINKUSDT",
        "symbol": "LINK",
        "name": "Chainlink",
        "coingecko_id": "chainlink",
        "image": "https://assets.coingecko.com/coins/images/877/large/chainlink-new-logo.png"
    },
]

# Convenience lookups derived from COINS — do not edit these manually
COIN_SYMBOL_TO_ID = {c["symbol"]: c["coingecko_id"] for c in COINS}
TOP_10_BINANCE_COINS = [
    {"symbol": c["binance_symbol"], "name": c["name"], "image": c["image"]}
    for c in COINS
]
