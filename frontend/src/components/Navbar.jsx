import { Link, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { jwtDecode } from 'jwt-decode';

function getInitials(name) {
  const parts = name.trim().split(' ');
  if (parts.length === 1) return parts[0][0].toUpperCase();
  return (parts[0][0] + parts[1][0]).toUpperCase();
}

const Navbar = () => {
  const navigate = useNavigate();
  const [loggedIn, setLoggedIn] = useState(false);
  const [initials, setInitials] = useState('');

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) return;

    setLoggedIn(true);

    try {
      const decoded = jwtDecode(token);
      const userId = decoded.sub;

      fetch(`http://localhost:5050/users/${userId}`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      })
        .then(res => res.json())
        .then(data => {
          if (data.user_name) {
            const userInitials = getInitials(data.user_name);
            setInitials(userInitials);
          }
        })
        .catch(() => {
          setInitials('?');
        });
    } catch {
      setInitials('?');
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setLoggedIn(false);
    navigate('/login');
  };

  return (
    <header className="py-1 px-6 border-b border-gray-200 bg-white">
      <div className="max-w-[1600px] mx-auto px-6 sm:px-10 lg:px-16 xl:px-24 2xl:px-32 flex justify-between items-center">
        <div className="flex items-center gap-10">
          <span className="text-[45px] font-extrabold text-blue-600 tracking-wide">
            ₿A$I
          </span>
          <nav className="hidden md:flex space-x-8 pl-12">
            <Link to="/" className="text-base font-medium text-gray-800 hover:text-blue-600">Cryptocurrencies</Link>
            <Link to="/ai-predictions" className="text-base font-medium text-gray-800 hover:text-blue-600">AI Predictions</Link>
            <Link to="/about" className="text-base font-medium text-gray-800 hover:text-blue-600">About</Link>
          </nav>
        </div>

        <div className="flex items-center gap-4">
          {loggedIn ? (
            <>
              <Link
                to="/account"
                className="h-11 w-11 rounded-full border-2 border-blue-600 text-blue-600 flex items-center justify-center text-sm font-semibold hover:bg-blue-50"
              >
                {initials}
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
