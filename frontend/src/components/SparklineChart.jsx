import { LineChart, Line, ResponsiveContainer } from 'recharts';

const SparklineChart = ({ data }) => {
  // Data should be an array of prices
  const chartData = data.map((price, i) => ({ index: i, value: price }));

  return (
    <div className="w-full h-16">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData}>
          <Line type="monotone" dataKey="value" stroke="#10b981" strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default SparklineChart;
