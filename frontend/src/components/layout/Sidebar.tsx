import { Cpu, LayoutDashboard, Activity, BarChart2, Settings } from 'lucide-react';
import { NavItem } from '../common/NavItem';

interface SidebarProps {
  status: 'ONLINE' | 'OFFLINE';
}

export function Sidebar({ status }: SidebarProps) {
  return (
    <aside className="w-64 flex-shrink-0 flex flex-col text-white bg-gradient-to-br from-indigo-950 to-indigo-900 border-r border-indigo-900/50">
      <div className="p-6 border-b border-white/5">
        <div className="flex items-center gap-3">
          <div className="bg-indigo-500 p-2 rounded-lg">
            <Cpu size={20} className="text-white" />
          </div>
          <div>
            <h2 className="text-sm font-black tracking-tight leading-none">PREDICTIVE</h2>
            <p className="text-[10px] font-bold text-indigo-300 tracking-widest mt-1 uppercase">Maintenance</p>
          </div>
        </div>
      </div>

      <nav className="flex-1 p-4 space-y-1">
        <NavItem icon={<LayoutDashboard />} label="Dashboard" active />
        <NavItem icon={<Activity />} label="Telemetry" />
        <NavItem icon={<BarChart2 />} label="Analytics" />
        <NavItem icon={<Settings />} label="Gateway" />
      </nav>

      <div className="p-4 border-t border-white/5">
        <div className="bg-indigo-950/50 rounded-xl p-3 border border-white/5">
          <p className="text-[9px] font-black text-indigo-400 uppercase tracking-widest mb-2">System Status</p>
          <div className={`flex items-center gap-2 text-[10px] font-bold ${status === 'ONLINE' ? 'text-emerald-400' : 'text-rose-400'}`}>
            <div className={`w-1.5 h-1.5 rounded-full ${status === 'ONLINE' ? 'bg-emerald-400 animate-pulse' : 'bg-rose-400'}`}></div>
            {status}
          </div>
        </div>
      </div>
    </aside>
  );
}
