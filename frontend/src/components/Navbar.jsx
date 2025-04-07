// src/components/Navbar.jsx
import { Link } from "react-router-dom";

const Navbar = () => {
  return (
    <nav className="bg-white shadow px-4 py-2 flex justify-between items-center">
      <div className="text-2xl font-bold text-primary">₿A$I</div>
      <div className="space-x-4 text-sm">
        <Link to="/" className="text-text hover:text-accent">Home</Link>
        <Link to="/ai-agent" className="text-text hover:text-accent">AI Agent</Link>
        <Link to="/about" className="text-text hover:text-accent">About</Link>
      </div>
    </nav>
  );
};

export default Navbar;
