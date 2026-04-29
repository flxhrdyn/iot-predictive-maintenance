import React, { ReactElement } from 'react';

interface MetricCardProps {
  label: string;
  subLabel: string; // New prop for technical sub-labels
  value: string | number;
  unit: string;
  icon: ReactElement;
  color: 'rose' | 'blue' | 'amber' | 'emerald';
  progress: number;
}

export function MetricCard({ label, subLabel, value, unit, icon, color, progress }: MetricCardProps) {
  const colorMap = {
    rose: 'text-rose-500 bg-rose-500 bg-rose-500/10',
    blue: 'text-blue-500 bg-blue-500 bg-blue-500/10',
    amber: 'text-amber-500 bg-amber-500 bg-amber-500/10',
    emerald: 'text-emerald-500 bg-emerald-500 bg-emerald-500/10'
  };

  const bgParts = colorMap[color].split(' ');

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm hover:shadow-md transition-shadow">
      <div className="flex justify-between items-start mb-4">
        <div className="flex flex-col">
          <span className="text-[9px] font-black text-slate-400 uppercase tracking-widest leading-none mb-1">{subLabel}</span>
          <h3 className="text-xs font-bold text-slate-600 uppercase">{label}</h3>
        </div>
        <div className={`p-2 rounded-lg ${bgParts[2]} ${bgParts[0]}`}>
          {React.cloneElement(icon, { size: 18 } as any)}
        </div>
      </div>
      <div className="flex items-baseline gap-1 mb-4">
        <span className="text-4xl font-black text-slate-800 tracking-tighter">{value}</span>
        <span className="text-lg font-light text-slate-400">{unit}</span>
      </div>
      <div className="w-full bg-slate-100 h-1.5 rounded-full overflow-hidden">
        <div className={`h-full transition-all duration-500 ${bgParts[1]}`} style={{ width: `${Math.min(progress, 100)}%` }}></div>
      </div>
    </div>
  );
}
