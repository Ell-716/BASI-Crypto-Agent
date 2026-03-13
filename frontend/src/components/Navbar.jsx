import { Link, useNavigate } from "react-router-dom";
import { useEffect, useState, useRef } from "react";
import { jwtDecode } from 'jwt-decode';
import { User, Search, Menu, ChevronDown } from 'lucide-react';
import api from '@/api/axios';

const Navbar = () => {
  const navigate = useNavigate();
  const [loggedIn, setLoggedIn] = useState(false);
  const [coins, setCoins] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [filteredCoins, setFilteredCoins] = useState([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const [showCoinDropdown, setShowCoinDropdown] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const coinDropdownRef = useRef(null);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) return;

    try {
      const decoded = jwtDecode(token);
      if (decoded.sub) {
        setLoggedIn(true);
      }
    } catch {
      setLoggedIn(false);
    }
  }, []);

  useEffect(() => {
    const fetchCoins = async () => {
      try {
        const response = await api.get('/api/coins');
        // Map API response to the format expected by search and dropdown
        const mappedCoins = response.data.map(coin => ({
          coin_name: coin.name,
          coin_symbol: coin.symbol.toLowerCase()
        }));
        setCoins(mappedCoins);
      } catch (error) {
        console.error('Error fetching coins:', error);
      }
    };

    fetchCoins();
  }, []);

  // Click outside to close coin dropdown
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (coinDropdownRef.current && !coinDropdownRef.current.contains(event.target)) {
        setShowCoinDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setLoggedIn(false);
    navigate('/login');
  };

  const handleSearchChange = (e) => {
    const query = e.target.value.toLowerCase();
    setSearchQuery(query);

    if (query.length === 0) {
      setFilteredCoins([]);
      setShowDropdown(false);
      return;
    }

    const matches = coins.filter((coin) =>
      coin.coin_name.toLowerCase().includes(query) ||
      coin.coin_symbol.toLowerCase().includes(query)
    );
    setFilteredCoins(matches);
    setShowDropdown(true);
  };

  const handleSelectCoin = (symbol) => {
    setSearchQuery('');
    setShowDropdown(false);
    navigate(`/coin/${symbol.toUpperCase()}`);
  };

  return (
    <header className="py-1 px-4 sm:px-6 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 sticky top-0 z-50">
      <div className="max-w-[1800px] mx-auto flex justify-between items-center">
        {/* Left side - Logo and Nav */}
        <div className="flex items-center gap-4 md:gap-8">
          {/* Logo */}
          <span className="text-2xl sm:text-3xl md:text-4xl font-extrabold text-blue-600 tracking-wide">
            ₿A$I
          </span>

          {/* Desktop Navigation - shows from md breakpoint */}
          <nav className="hidden md:flex space-x-4 lg:space-x-6 xl:space-x-8 items-center">
            <Link to="/" className="text-sm lg:text-base font-medium text-gray-800 dark:text-gray-100 hover:text-blue-600">Cryptocurrencies</Link>
            <Link to="/ai-predictions" className="text-sm lg:text-base font-medium text-gray-800 dark:text-gray-100 hover:text-blue-600">AI Predictions</Link>

            {/* Coin Page Dropdown */}
            <div className="relative" ref={coinDropdownRef}>
              <button
                onClick={() => setShowCoinDropdown(!showCoinDropdown)}
                className="text-sm lg:text-base font-medium text-gray-800 dark:text-gray-100 hover:text-blue-600 flex items-center gap-1"
              >
                Coin Page
                <ChevronDown className={`w-4 h-4 transition-transform ${showCoinDropdown ? 'rotate-180' : ''}`} />
              </button>

              {showCoinDropdown && coins.length > 0 && (
                <div className="absolute top-full mt-1 left-0 w-48 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-md shadow-lg z-50 py-1">
                  {coins.map((coin) => (
                    <Link
                      key={coin.coin_symbol}
                      to={`/coin/${coin.coin_symbol.toUpperCase()}`}
                      onClick={() => setShowCoinDropdown(false)}
                      className="block px-4 py-2 text-sm text-gray-800 dark:text-gray-100 hover:bg-blue-50 dark:hover:bg-gray-700"
                    >
                      {coin.coin_name} ({coin.coin_symbol.toUpperCase()})
                    </Link>
                  ))}
                </div>
              )}
            </div>

            <Link to="/about" className="text-sm lg:text-base font-medium text-gray-800 dark:text-gray-100 hover:text-blue-600">About</Link>
          </nav>

          {/* Mobile Menu Button - shows below md breakpoint */}
          <button
            className="md:hidden p-1.5 rounded-md text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            <Menu className="w-5 h-5" />
          </button>
        </div>

        {/* Right side - Search and Auth */}
        <div className="flex items-center gap-2 sm:gap-3 md:gap-4">
          {/* Search - conditionally rendered based on screen size */}
          {loggedIn && (
            <div className="relative">
              {/* Search icon - shown on all screens */}
              <div className="absolute inset-y-0 left-2 flex items-center pointer-events-none">
                <Search className="w-4 h-4 text-gray-400" />
              </div>

              {/* Search input - full width on mobile, compact on medium */}
              <input
                type="text"
                placeholder={window.innerWidth < 768 ? "Search..." : "Search..."}
                value={searchQuery}
                onChange={handleSearchChange}
                className="h-8 sm:h-9 w-24 sm:w-32 md:w-40 lg:w-48 xl:w-56 pl-8 pr-2 rounded-md border border-gray-300 dark:border-gray-600 text-xs sm:text-sm bg-white dark:bg-gray-800 focus:outline-none focus:ring-1 focus:ring-blue-600"
              />

              {/* Search dropdown */}
              {showDropdown && filteredCoins.length > 0 && (
                <div className="absolute top-9 sm:top-10 left-0 right-0 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-md shadow-md max-h-48 overflow-y-auto z-50">
                  {filteredCoins.map((coin) => (
                    <div
                      key={coin.coin_symbol}
                      onClick={() => handleSelectCoin(coin.coin_symbol)}
                      className="px-3 py-1.5 cursor-pointer hover:bg-gray-200 dark:hover:bg-gray-600 text-xs sm:text-sm"
                    >
                      {coin.coin_name} ({coin.coin_symbol.toUpperCase()})
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Auth section */}
          {loggedIn ? (
            <>
              <Link
                to="/account"
                className="hidden sm:flex h-8 w-8 md:h-9 md:w-9 rounded-full border-2 border-blue-600 bg-white dark:bg-gray-800 items-center justify-center hover:bg-gray-100 dark:hover:bg-blue-900"
              >
                <User className="w-4 h-4 md:w-5 md:h-5 text-blue-600 dark:text-blue-400" />
              </Link>
              <button
                onClick={handleLogout}
                className="h-8 sm:h-9 px-2 sm:px-3 text-xs sm:text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                Log out
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="px-2 sm:px-3 py-1 text-xs sm:text-sm border rounded-md hover:bg-blue-50 dark:hover:bg-gray-800">Login</Link>
              <Link to="/signup" className="px-2 sm:px-3 py-1 text-xs sm:text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700">Sign up</Link>
            </>
          )}
        </div>

        {/* Mobile Menu - shows below md breakpoint */}
        {mobileMenuOpen && (
          <div className="absolute top-12 sm:top-14 left-0 right-0 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 shadow-md md:hidden z-40 max-h-[calc(100vh-3.5rem)] overflow-y-auto">
            <div className="px-4 py-2">
              <Link
                to="/"
                className="block py-2 px-3 text-gray-800 dark:text-gray-100 hover:bg-blue-50 dark:hover:bg-blue-900 rounded-md text-sm sm:text-base"
                onClick={() => setMobileMenuOpen(false)}
              >
                Cryptocurrencies
              </Link>
              <Link
                to="/ai-predictions"
                className="block py-2 px-3 text-gray-800 dark:text-gray-100 hover:bg-blue-50 dark:hover:bg-blue-900 rounded-md text-sm sm:text-base"
                onClick={() => setMobileMenuOpen(false)}
              >
                AI Predictions
              </Link>

              {/* Coin Page Dropdown in Mobile */}
              <div className="py-2">
                <button
                  onClick={() => setShowCoinDropdown(!showCoinDropdown)}
                  className="w-full flex items-center justify-between py-2 px-3 text-gray-800 dark:text-gray-100 hover:bg-blue-50 dark:hover:bg-blue-900 rounded-md text-sm sm:text-base"
                >
                  Coin Page
                  <ChevronDown className={`w-4 h-4 transition-transform ${showCoinDropdown ? 'rotate-180' : ''}`} />
                </button>
                {showCoinDropdown && coins.length > 0 && (
                  <div className="mt-1 ml-4 space-y-1">
                    {coins.map((coin) => (
                      <Link
                        key={coin.coin_symbol}
                        to={`/coin/${coin.coin_symbol.toUpperCase()}`}
                        onClick={() => {
                          setShowCoinDropdown(false);
                          setMobileMenuOpen(false);
                        }}
                        className="block py-2 px-3 text-sm text-gray-700 dark:text-gray-300 hover:bg-blue-50 dark:hover:bg-gray-700 rounded-md"
                      >
                        {coin.coin_name} ({coin.coin_symbol.toUpperCase()})
                      </Link>
                    ))}
                  </div>
                )}
              </div>

              <Link
                to="/about"
                className="block py-2 px-3 text-gray-800 dark:text-gray-100 hover:bg-blue-50 dark:hover:bg-blue-900 rounded-md text-sm sm:text-base"
                onClick={() => setMobileMenuOpen(false)}
              >
                About
              </Link>
              {loggedIn && (
                <Link
                  to="/account"
                  className="block py-2 px-3 text-gray-800 dark:text-gray-100 hover:bg-blue-50 dark:hover:bg-blue-900 rounded-md text-sm sm:text-base"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Account
                </Link>
              )}
            </div>
          </div>
        )}
      </div>
    </header>
  );
};

export default Navbar;