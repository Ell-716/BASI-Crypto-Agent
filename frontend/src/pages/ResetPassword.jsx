import { useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import axios from 'axios';

const ResetPassword = () => {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');

  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

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
    } catch (err) {
      const msg = err.response?.data?.error || 'Something went wrong.';
      setError(msg);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-black px-4">
      <div className="bg-white p-8 rounded-xl max-w-md w-full shadow-lg text-center">
        <h2 className="text-2xl font-bold mb-4">Reset Your Password</h2>

        {error && <p className="text-red-600 text-sm mb-4">{error}</p>}
        {success && <p className="text-green-600 text-sm mb-4">{success}</p>}

        <form onSubmit={handleSubmit} className="space-y-4 text-left">
          <input
            type="password"
            placeholder="New password"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            required
            className="w-full px-4 py-3 border border-gray-300 rounded-md"
          />
          <input
            type="password"
            placeholder="Confirm password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
            className="w-full px-4 py-3 border border-gray-300 rounded-md"
          />
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
