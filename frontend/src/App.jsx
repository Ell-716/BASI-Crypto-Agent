import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import AIPredictions from './pages/AIPredictions';
import About from './pages/About';
import SignUp from './pages/SignUp';
import LogIn from './pages/LogIn';
import ResetPassword from './pages/ResetPassword';

function AppContent() {
  const location = useLocation();
  const hideNavbar = ['/signup', '/login', '/reset-password'].includes(location.pathname);

  return (
    <>
      {!hideNavbar && <Navbar />}
      <Routes>
        <Route path="/signup" element={<SignUp />} />
        <Route path="/login" element={<LogIn />} />
        <Route path="/reset-password" element={<ResetPassword />} />
        <Route path="/" element={<Home />} />
        <Route path="/ai-predictions" element={<AIPredictions />} />
        <Route path="/about" element={<About />} />
      </Routes>
    </>
  );
}

function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  );
}

export default App;
