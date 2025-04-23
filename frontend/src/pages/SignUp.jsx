import React, { useState } from 'react';
import axios from 'axios';

export default function SignUp() {
  const [form, setForm] = useState({
    user_name: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (form.password !== form.confirmPassword) {
      setError("Passwords do not match.");
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
      const msg = err.response?.data?.error || "Something went wrong.";
      setError(msg);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-white px-4">
      <div className="w-full max-w-md border border-blue-600 rounded-2xl p-8 shadow-sm">
        <h1 className="text-4xl font-bold text-blue-600 text-center mb-2">₿A$I</h1>
        <p className="text-center text-gray-600 mb-6">
          Get AI-powered buy, sell or hold predictions
        </p>

        {error && <p className="text-red-600 text-sm mb-2">{error}</p>}
        {success && <p className="text-green-600 text-sm mb-2">{success}</p>}

        <form className="space-y-4" onSubmit={handleSubmit}>
          <input
            name="user_name"
            value={form.user_name}
            onChange={handleChange}
            type="text"
            placeholder="Username"
            required
            className="w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-600"
          />
          <input
            name="email"
            value={form.email}
            onChange={handleChange}
            type="email"
            placeholder="Email"
            required
            className="w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-600"
          />
          <input
            name="password"
            value={form.password}
            onChange={handleChange}
            type="password"
            placeholder="Password"
            required
            className="w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-600"
          />
          <input
            name="confirmPassword"
            value={form.confirmPassword}
            onChange={handleChange}
            type="password"
            placeholder="Confirm Password"
            required
            className="w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-600"
          />

          <button
            type="submit"
            className="w-full bg-blue-600 text-white font-semibold py-2 rounded-md hover:bg-blue-700 transition"
          >
            Create Account
          </button>
        </form>

        <p className="mt-4 text-sm text-center text-gray-600">
          Already have an account?{' '}
          <a href="/login" className="text-blue-600 font-semibold hover:underline">
            Log in
          </a>
        </p>
      </div>
    </div>
  );
}
