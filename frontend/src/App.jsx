import { BrowserRouter as Router, Routes, Route, useLocation, Navigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import Home from './pages/Home';
import AIPredictions from './pages/AIPredictions';
import About from './pages/About';
import SignUp from './pages/SignUp';
import LogIn from './pages/LogIn';
import ResetPassword from './pages/ResetPassword';
import Account from './pages/Account';
import CoinPage from "./pages/CoinPage";

function PrivateRoute({ children }) {
  const token = localStorage.getItem('access_token');
  return token ? children : <Navigate to="/login" />;
}

function AppContent() {
  const location = useLocation();
  const hideNavbarAndFooter = ['/signup', '/login', '/reset-password'].includes(location.pathname);

  return (
    <>
      {!hideNavbarAndFooter && <Navbar />}
      <main className="flex-grow">
        <Routes>
          <Route path="/signup" element={<SignUp />} />
          <Route path="/login" element={<LogIn />} />
          <Route path="/reset-password" element={<ResetPassword />} />
          <Route path="/" element={<PrivateRoute><Home /></PrivateRoute>} />
          <Route path="/coin/:symbol" element={<PrivateRoute><CoinPage /></PrivateRoute>} />
          <Route path="/ai-predictions" element={<PrivateRoute><AIPredictions /></PrivateRoute>} />
          <Route path="/about" element={<PrivateRoute><About /></PrivateRoute>} />
          <Route path="/account" element={<PrivateRoute><Account /></PrivateRoute>} />
          {/* Catch-all redirect to login */}
          <Route path="*" element={<Navigate to="/login" />} />
        </Routes>
      </main>
      {!hideNavbarAndFooter && <Footer />}
    </>
  );
}


function App() {
  return (
    <Router>
      <div className="flex flex-col min-h-screen">
        <AppContent />
      </div>
    </Router>
  );
}

export default App;
