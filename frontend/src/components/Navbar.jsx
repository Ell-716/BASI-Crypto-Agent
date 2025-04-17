import { Link } from "react-router-dom";

const Navbar = () => {
  return (
    <header className="py-4 px-6 border-b border-gray-200 bg-white">
      <div className="container mx-auto flex justify-between items-center">
        <div className="flex items-center gap-10">
          <div className="flex items-center gap-2">
            <div className="h-10 w-10 rounded-full border-2 border-blue-600 flex items-center justify-center">
              {/* Logo placeholder */}
            </div>
            <span className="text-2xl font-bold text-blue-600">
              <span className="bitcoin-logo">₿A$I</span>
            </span>
          </div>
          <nav className="hidden md:flex space-x-8">
            <Link to="/" className="text-base font-medium text-gray-800 hover:text-blue-600">Cryptocurrencies</Link>
            <Link to="/ai-predictions" className="text-base font-medium text-gray-800 hover:text-blue-600">AI Predictions</Link>
            <Link to="/about" className="text-base font-medium text-gray-800 hover:text-blue-600">About</Link>
          </nav>
        </div>

        <div className="flex space-x-4">
          <button className="px-4 py-1.5 border text-sm rounded-md hover:bg-blue-50">Login</button>
          <button className="px-4 py-1.5 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700">Sign up</button>
        </div>
      </div>
    </header>
  );
};

export default Navbar;
