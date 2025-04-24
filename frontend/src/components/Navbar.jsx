import { Link, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";

const Navbar = () => {
  const navigate = useNavigate();
  const [loggedIn, setLoggedIn] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    setLoggedIn(!!token);
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setLoggedIn(false);
    navigate('/login');
  };

  return (
    <header className="py-4 px-6 border-b border-gray-200 bg-white">
      <div className="container mx-auto flex justify-between items-center">
        <div className="flex items-center gap-10">
          <span className="text-2xl font-bold text-blue-600 bitcoin-logo">₿A$I</span>
          <nav className="hidden md:flex space-x-8">
            <Link to="/" className="text-base font-medium text-gray-800 hover:text-blue-600">Cryptocurrencies</Link>
            <Link to="/ai-predictions" className="text-base font-medium text-gray-800 hover:text-blue-600">AI Predictions</Link>
            <Link to="/about" className="text-base font-medium text-gray-800 hover:text-blue-600">About</Link>
          </nav>
        </div>

        <div className="flex space-x-4">
          {loggedIn ? (
            <>
              <Link to="/account" className="text-base font-medium text-gray-800 hover:text-blue-600">Account</Link>
              <button
                onClick={handleLogout}
                className="text-base font-medium text-gray-800 hover:text-blue-600"
              >
                Log out
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="px-4 py-1.5 border text-sm rounded-md hover:bg-blue-50">Login</Link>
              <Link to="/signup" className="px-4 py-1.5 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700">Sign up</Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
};

export default Navbar;
