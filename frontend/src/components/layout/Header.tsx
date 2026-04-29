import { useState, useEffect } from 'react';
import { User } from 'lucide-react';

export function Header() {
  const [time, setTime] = useState<Date>(new Date());

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <header className="bg-white border-b border-slate-200 px-6 py-4 flex justify-between items-center flex-shrink-0 shadow-sm">
      <div>
        <h1 className="text-lg font-black text-slate-800 tracking-tight uppercase">Predictive Maintenance Dashboard</h1>
        <p className="text-[10px] font-bold text-slate-400 tracking-[0.2em] uppercase">Industrial AI Analytics Gateway</p>
      </div>
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-3 bg-slate-50 px-3 py-1.5 rounded-lg border border-slate-200">
          <div className="text-[10px] font-bold text-slate-500 uppercase">
            {time.toLocaleDateString('en-US', { month: 'short', day: '2-digit', year: 'numeric' })}
          </div>
          <div className="h-3 w-px bg-slate-200"></div>
          <div className="text-sm font-mono font-black text-slate-700 tracking-widest">{time.toTimeString().split(' ')[0]}</div>
        </div>
        <div className="w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center text-slate-400 border border-slate-200">
          <User size={16} />
        </div>
      </div>
    </header>
  );
}
