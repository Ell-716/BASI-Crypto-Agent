import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import AIPredictions from './pages/AIPredictions';
import About from './pages/About';
import SignUp from './pages/SignUp';
import LogIn from './pages/LogIn';

function AppContent() {
  const location = useLocation();
  const hideNavbar = ['/signup', '/login'].includes(location.pathname);

  return (
    <>
      {!hideNavbar && <Navbar />}
      <Routes>
        <Route path="/signup" element={<SignUp />} />
        <Route path="/login" element={<LogIn />} />
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
