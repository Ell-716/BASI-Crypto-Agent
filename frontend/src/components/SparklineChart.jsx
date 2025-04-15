import { LineChart, Line, ResponsiveContainer } from 'recharts';

const SparklineChart = ({ data }) => {
  if (!data || data.length === 0) return null;

  const min = Math.min(...data);
  const max = Math.max(...data);
  const range = max - min || 1;

  const chartData = data.map((price, i) => ({
    index: i,
    value: ((price - min) / range) * 100
  }));

  return (
    <div className="w-full h-24"> {/* increased height */}
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData}>
          <Line
            type="monotone"
            dataKey="value"
            stroke="#10b981"
            strokeWidth={2}
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default SparklineChart;
