import { Link, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { jwtDecode } from 'jwt-decode';
import { User } from 'lucide-react';

const Navbar = () => {
  const navigate = useNavigate();
  const [loggedIn, setLoggedIn] = useState(false);

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

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setLoggedIn(false);
    navigate('/login');
  };

  return (
    <header className="py-0.5 px-6 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900">
      <div className="max-w-[1600px] mx-auto px-6 sm:px-10 lg:px-16 xl:px-24 2xl:px-32 flex justify-between items-center">
        <div className="flex items-center gap-10">
          <span className="text-[45px] font-extrabold text-blue-600 tracking-wide">
            ₿A$I
          </span>
          <nav className="hidden md:flex space-x-8 pl-12">
            <Link to="/" className="text-base font-medium text-gray-800 dark:text-gray-100 hover:text-blue-600">Cryptocurrencies</Link>
            <Link to="/ai-predictions" className="text-base font-medium text-gray-800 dark:text-gray-100 hover:text-blue-600">AI Predictions</Link>
            <Link to="/about" className="text-base font-medium text-gray-800 dark:text-gray-100 hover:text-blue-600">About</Link>
          </nav>
        </div>

        <div className="flex items-center gap-4">
          {loggedIn ? (
            <>
              <Link
                to="/account"
                className="h-11 w-11 rounded-full border-2 border-blue-600 bg-white flex items-center justify-center hover:bg-blue-50"
              >
                <User className="w-6 h-6 text-blue-600" />
              </Link>
              <button
                onClick={handleLogout}
                className="h-9 px-3 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700"
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
