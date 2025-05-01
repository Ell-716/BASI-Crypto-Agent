import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import axios from 'axios';

const checkPasswordStrength = (password) => ({
  length: password.length >= 8,
  upper: /[A-Z]/.test(password),
  lower: /[a-z]/.test(password),
  number: /\d/.test(password),
  special: /[@$!%*?&#]/.test(password),
});

const ResetPassword = () => {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');

  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [passwordChecks, setPasswordChecks] = useState({});
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    setPasswordChecks(checkPasswordStrength(newPassword));
  }, [newPassword]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (newPassword !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    try {
      const res = await axios.post('http://localhost:5050/users/reset-password', {
        token,
        new_password: newPassword
      });

      setSuccess(res.data.message);
      setTimeout(() => {
        window.location.href = '/login';
      }, 2000);
    } catch (err) {
      const msg = err.response?.data?.error || 'Something went wrong.';
      if (msg.includes("expired") || msg.includes("invalid")) {
        setError("This link is invalid or has expired. Please request a new reset link.");
        setTimeout(() => {
          window.location.href = '/login';
        }, 3000);
      } else {
        setError(msg);
      }
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-black px-4">
      <div className="bg-white p-8 rounded-xl max-w-md w-full shadow-lg text-center">
        <h2 className="text-xl font-bold mb-4 text-gray-900">Reset Your Password</h2>

        {error && <p className="text-red-600 text-sm mb-4">{error}</p>}
        {success && <p className="text-green-600 text-sm mb-4">{success}</p>}

        <form onSubmit={handleSubmit} className="space-y-4 text-left">
          <div>
            <input
              type="password"
              placeholder="New password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              required
              className="w-full px-4 py-3 text-lg border border-gray-300 rounded-md text-gray-800 placeholder-gray-500 focus:ring-2 focus:ring-blue-600 bg-white"
            />
            <ul className="text-xs text-left mt-2 space-y-1">
              <li className={passwordChecks.length ? 'text-green-600' : 'text-gray-500'}>✔ At least 8 characters</li>
              <li className={passwordChecks.upper ? 'text-green-600' : 'text-gray-500'}>✔ One uppercase letter</li>
              <li className={passwordChecks.lower ? 'text-green-600' : 'text-gray-500'}>✔ One lowercase letter</li>
              <li className={passwordChecks.number ? 'text-green-600' : 'text-gray-500'}>✔ One number</li>
              <li className={passwordChecks.special ? 'text-green-600' : 'text-gray-500'}>✔ One special character (@, #, $, etc.)</li>
            </ul>
          </div>

          <div>
            <input
              type="password"
              placeholder="Confirm password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              className="w-full px-4 py-3 text-lg border border-gray-300 rounded-md text-gray-800 placeholder-gray-500 focus:ring-2 focus:ring-blue-600 bg-white"
            />
          </div>

          <button
            type="submit"
            className="w-full bg-blue-600 text-white font-semibold py-3 rounded-md hover:bg-blue-700 transition"
          >
            Update Password
          </button>
        </form>
      </div>
    </div>
  );
};

export default ResetPassword;
