import React, { useState } from 'react';
import axios from 'axios';
import { Eye, EyeOff } from 'lucide-react';

export default function LogIn() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [resetOpen, setResetOpen] = useState(false);
  const [resetEmail, setResetEmail] = useState('');
  const [resetMessage, setResetMessage] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    try {
      const res = await axios.post('http://localhost:5050/users/login', {
        email,
        password
      });
      setSuccess('Logged in successfully');
      console.log(res.data); // Save tokens to localStorage or context
    } catch (err) {
      setError(err.response?.data?.error || 'Login failed');
    }
  };

  const handleReset = async (e) => {
    e.preventDefault();
    setResetMessage('');
    try {
      const res = await axios.post('http://localhost:5050/users/request-password-reset', {
        email: resetEmail
      });
      setResetMessage(res.data.message);
    } catch (err) {
      setResetMessage('Something went wrong.');
    }
  };

  return (
    <div className="min-h-screen flex flex-col lg:flex-row bg-no-repeat bg-cover bg-center"
      style={{ backgroundImage: "url('/background.jpg')", backgroundPosition: 'center 50%' }}>

      {/* Mobile: Logo + Tagline */}
      <div className="lg:hidden flex flex-col items-center pt-10 px-4 text-white">
        <h1 className="text-7xl md:text-8xl font-extrabold text-white [text-shadow:_0_0_15px_rgb(59_130_246),_0_0_30px_rgb(59_130_246)]">
          ₿A$I
        </h1>
        <p className="text-xl md:text-2xl font-medium mt-4 text-center">
          Get AI-powered buy, sell or hold predictions!
        </p>
      </div>

      {/* Desktop: Left Column */}
      <div className="hidden lg:flex lg:w-1/2 flex-col justify-start items-start pt-40 pl-20 text-white">
        <h1 className="text-9xl font-extrabold [text-shadow:_0_0_15px_rgb(59_130_246),_0_0_30px_rgb(59_130_246)]">
          ₿A$I
        </h1>
        <p className="text-2xl font-medium mt-8">
          Get AI-powered buy, sell or hold predictions!
        </p>
      </div>

      {/* Right Column */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-4 sm:p-8 lg:p-16">
        <div className="w-full max-w-md bg-white bg-opacity-90 border-2 border-blue-600 rounded-3xl p-6 sm:p-10 shadow-xl">
          <h2 className="text-2xl sm:text-3xl font-bold text-center text-blue-600 mb-6 sm:mb-8">
            Log In
          </h2>

          {error && <p className="text-red-600 text-sm mb-4 text-center">{error}</p>}
          {success && <p className="text-green-600 text-sm mb-4 text-center">{success}</p>}

          <form onSubmit={handleLogin} className="space-y-6">
            <input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full px-5 py-4 text-lg border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-600"
            />
            <div className="relative">
              <input
                type={showPassword ? 'text' : 'password'}
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full px-5 py-4 text-lg border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-600 pr-12"
              />
              <div
                className="absolute inset-y-0 right-4 flex items-center cursor-pointer text-gray-500 hover:text-gray-700"
                onClick={() => setShowPassword(!showPassword)}>
                {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
              </div>
            </div>
            <div className="text-right text-sm">
              <button type="button" className="text-blue-600 hover:underline" onClick={() => setResetOpen(true)}>
                Forgot password?
              </button>
            </div>
            <button
              type="submit"
              className="w-full bg-blue-600 text-white text-xl font-semibold py-4 rounded-xl hover:bg-blue-700 transition">
              Log In
            </button>
          </form>

          <p className="mt-6 text-sm text-center text-gray-600">
            No account yet?{' '}
            <a href="/signup" className="text-blue-600 font-semibold hover:underline">
              Sign up!
            </a>
          </p>
        </div>
      </div>

      {/* Password Reset Modal */}
      {resetOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-70 flex justify-center items-center z-50">
          <div className="bg-white p-6 rounded-xl w-80 shadow-md text-center">
            <h3 className="text-xl font-bold mb-4">Reset Password</h3>
            <form onSubmit={handleReset} className="space-y-4">
              <input
                type="email"
                placeholder="Enter your email"
                value={resetEmail}
                onChange={(e) => setResetEmail(e.target.value)}
                required
                className="w-full px-4 py-3 border rounded-md"
              />
              <button type="submit" className="w-full bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700">
                Send Reset Link
              </button>
              <button
                type="button"
                onClick={() => setResetOpen(false)}
                className="text-sm text-gray-600 hover:underline mt-2"
              >
                Cancel
              </button>
              {resetMessage && <p className="text-sm text-green-600 mt-2">{resetMessage}</p>}
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
