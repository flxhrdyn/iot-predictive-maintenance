import { useMemo } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  ChartOptions
} from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

interface FailureChartProps {
  data: number[];
}

export function FailureChart({ data }: FailureChartProps) {
  // Determine color based on latest probability
  const latestProb = data[data.length - 1] || 0;
  const lineColor = latestProb > 50 ? '#f43f5e' : '#4338ca';
  const bgColor = latestProb > 50 ? 'rgba(244, 63, 94, 0.05)' : 'rgba(67, 56, 202, 0.05)';

  const lineChartData = useMemo(() => ({
    labels: Array(30).fill(''),
    datasets: [{
      data: data,
      borderColor: lineColor,
      backgroundColor: bgColor,
      borderWidth: 2,
      fill: true,
      tension: 0.4,
      pointRadius: 0,
    }]
  }), [data, lineColor, bgColor]);

  const chartOptions: ChartOptions<'line'> = useMemo(() => ({
    responsive: true,
    maintainAspectRatio: false,
    animation: { duration: 0 },
    scales: {
      x: { display: false },
      y: { 
        beginAtZero: true, 
        max: 100, 
        grid: { color: '#f1f5f9' }, 
        ticks: { color: '#94a3b8', font: { weight: '700' as any, size: 9 } } 
      }
    },
    plugins: { legend: { display: false } }
  }), []);

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h3 className="text-xs font-bold text-slate-700 uppercase">Inference History & Probability Drift</h3>
          <p className="text-[9px] font-black text-slate-400 uppercase tracking-widest mt-0.5">Real-time Machine Learning Diagnostics</p>
        </div>
        <div className="text-[9px] font-bold text-slate-400 uppercase bg-slate-50 px-2 py-0.5 rounded border border-slate-200">AI Gateway Active</div>
      </div>
      <div className="h-64">
        <Line data={lineChartData} options={chartOptions} />
      </div>
    </div>
  );
}
