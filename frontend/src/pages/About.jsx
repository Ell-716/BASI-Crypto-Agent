const About = () => {
  return (
    <div className="flex justify-center items-center min-h-screen p-4">
      <div className="max-w-3xl w-full rounded-md border border-gray-200 dark:border-gray-700 p-8 shadow-sm bg-white dark:bg-gray-800 animate-fade-up">
        {/* Page title */}
        <h1 className="text-3xl font-bold text-center text-blue-600 mb-8">About ₿A$I</h1>

        {/* Introduction section */}
        <p className="text-lg mb-6">
          <strong>₿A$I (Blockchain AI Smart Investor)</strong> is your personal AI Agent for the world of crypto trading.
          It’s designed to help you make smarter decisions by giving you real-time insights, AI-powered predictions,
          and clear charts of the most important market indicators. ₿A$I acts like a smart crypto analyst who watches the market,
          thinks about it, and then explains it to you in simple, clear terms.
        </p>

        {/* Features overview */}
        <p className="text-lg font-semibold mb-2 text-left">
          With ₿A$I, you're never trading alone.
        </p>
        <p className="text-lg mb-6 text-left">
          You'll have access to:
        </p>

        <ul className="list-disc list-inside mb-6 text-base text-left">
          <li><strong>Predictions with detailed reasoning and indicator charts</strong></li>
          <li><strong>Live coin chart</strong> showing market movements</li>
          <li><strong>Detailed coin information</strong> at your fingertips</li>
          <li>A <strong>dashboard</strong> that keeps you updated on everything important — instantly</li>
        </ul>

        {/* Target audience section */}
        <h2 className="text-2xl font-semibold mb-4 text-left">Who is ₿A$I for?</h2>
        <p className="text-base mb-6 text-left">
          Whether you're just starting your crypto journey or you're an experienced trader looking for an extra edge,
          ₿A$I is here to make the crypto world easier, smarter, and more accessible for you.
        </p>

        {/* Benefits section */}
        <h2 className="text-2xl font-semibold mb-4 text-left">Why ₿A$I?</h2>
        <ul className="list-disc list-inside mb-6 text-base text-left">
          <li>Real-time insights based on real data and technical analysis</li>
          <li>Understand the trends, indicators, and reasoning behind each prediction</li>
          <li>Stay updated with a live dashboard designed for quick and easy use</li>
        </ul>

        {/* Disclaimer notice */}
        <div className="bg-gray-100 dark:bg-gray-600 p-4 rounded-md text-center text-sm mb-6">
          <p><strong>Important:</strong> ₿A$I is an informational and educational tool.<br/>
          It does not provide financial advice or trading recommendations.</p>
        </div>

        {/* Contact information */}
        <div className="text-center text-base mb-4">
          <p>Have a question or just want to say hi?</p>
          <p>📧 <a href="mailto:basi.ai.agent@gmail.com" className="text-blue-600 hover:underline">basi.ai.agent@gmail.com</a></p>
        </div>

        <div className="text-center text-xs text-gray-500">
          Created with passion by Elena Bai.
        </div>
      </div>
    </div>
  );
};

export default About;
