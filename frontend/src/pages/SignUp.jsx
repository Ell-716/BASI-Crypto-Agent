import React, { useState } from 'react';
import axios from 'axios';
import { Eye, EyeOff } from 'lucide-react';

export default function SignUp() {
  const [form, setForm] = useState({
    user_name: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [fieldErrors, setFieldErrors] = useState({});
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const isValidEmail = (email) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  const isValidUsername = (name) => /^[a-zA-Z0-9_]{3,}$/.test(name);

  const passwordChecks = {
    length: form.password.length >= 8,
    upper: /[A-Z]/.test(form.password),
    lower: /[a-z]/.test(form.password),
    number: /[0-9]/.test(form.password),
    special: /[@#$%^&*!]/.test(form.password)
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setFieldErrors({});

    const errors = {};
    if (!isValidEmail(form.email.trim())) errors.email = 'Please enter a valid email address.';
    if (!isValidUsername(form.user_name.trim())) errors.user_name = 'Username must be at least 3 characters. Letters, numbers, and underscores only.';
    if (form.password !== form.confirmPassword) errors.confirmPassword = 'Passwords do not match.';
    if (Object.keys(errors).length > 0) {
      setFieldErrors(errors);
      return;
    }

    try {
      const res = await axios.post('http://localhost:5050/users/add_user', {
        email: form.email,
        user_name: form.user_name,
        password: form.password
      });
      setSuccess(res.data.message);
      setForm({ user_name: '', email: '', password: '', confirmPassword: '' });
    } catch (err) {
      const msg = err.response?.data?.error || 'Something went wrong.';
      if (msg.includes('PASSWORD MUST CONTAIN')) {
        setFieldErrors({ password: msg });
      } else {
        setError(msg);
      }
    }
  };

  return (
    <div className="min-h-screen flex flex-col lg:flex-row bg-no-repeat bg-cover bg-center" style={{ backgroundImage: "url('/background.jpg')", backgroundPosition: 'center 50%' }}>

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

      {/* Right Column: Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-4 sm:p-8 lg:p-16">
        <div className="w-full max-w-md bg-white bg-opacity-90 border-2 border-blue-600 rounded-3xl p-6 sm:p-10 shadow-xl">
          <h2 className="text-2xl sm:text-3xl font-bold text-center text-blue-600 mb-6">
            Sign Up
          </h2>

          {error && <p className="text-red-600 text-sm mb-4 text-center">{error}</p>}
          {success && <p className="text-green-600 text-sm mb-4 text-center">{success}</p>}

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <input
                name="user_name"
                value={form.user_name}
                onChange={handleChange}
                type="text"
                placeholder="Username"
                required
                className="w-full px-5 py-4 text-lg border-2 border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-600"
              />
              {fieldErrors.user_name && <p className="text-red-600 text-sm mt-1">{fieldErrors.user_name}</p>}
            </div>

            <div>
              <input
                name="email"
                value={form.email}
                onChange={handleChange}
                type="email"
                placeholder="Email"
                required
                className="w-full px-5 py-4 text-lg border-2 border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-600"
              />
              {fieldErrors.email && <p className="text-red-600 text-sm mt-1">{fieldErrors.email}</p>}
            </div>

            <div>
              <div className="relative">
                <input
                  name="password"
                  value={form.password}
                  onChange={handleChange}
                  type={showPassword ? 'text' : 'password'}
                  placeholder="Password"
                  required
                  className="w-full px-5 py-4 text-lg border-2 border-gray-300 rounded-xl pr-12 focus:outline-none focus:ring-2 focus:ring-blue-600"
                />
                <div
                  className="absolute inset-y-0 right-4 flex items-center cursor-pointer text-gray-500 hover:text-gray-700"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                </div>
              </div>
              <ul className="text-xs text-left mt-2 space-y-1">
                <li className={passwordChecks.length ? 'text-green-600' : 'text-gray-500'}>✔ At least 8 characters</li>
                <li className={passwordChecks.upper ? 'text-green-600' : 'text-gray-500'}>✔ One uppercase letter</li>
                <li className={passwordChecks.lower ? 'text-green-600' : 'text-gray-500'}>✔ One lowercase letter</li>
                <li className={passwordChecks.number ? 'text-green-600' : 'text-gray-500'}>✔ One number</li>
                <li className={passwordChecks.special ? 'text-green-600' : 'text-gray-500'}>✔ One special character (@, #, $, etc.)</li>
              </ul>
              {fieldErrors.password && <p className="text-red-600 text-sm mt-1 whitespace-pre-line">{fieldErrors.password}</p>}
            </div>

            <div>
              <input
                name="confirmPassword"
                value={form.confirmPassword}
                onChange={handleChange}
                type="password"
                placeholder="Confirm Password"
                required
                className="w-full px-5 py-4 text-lg border-2 border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-600"
              />
              {fieldErrors.confirmPassword && <p className="text-red-600 text-sm mt-1">{fieldErrors.confirmPassword}</p>}
            </div>

            <button
              type="submit"
              className="w-full bg-blue-600 text-white text-xl font-semibold py-4 rounded-xl hover:bg-blue-700 transition mt-4"
            >
              Create Account
            </button>
          </form>

          <p className="mt-6 text-sm text-center text-gray-600">
            Already have an account?{' '}
            <a href="/login" className="text-blue-600 font-semibold hover:underline">
              Log in!
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}
