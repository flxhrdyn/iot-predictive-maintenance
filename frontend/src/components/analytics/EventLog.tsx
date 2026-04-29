interface EventLogProps {
  logs: string[];
}

export function EventLog({ logs }: EventLogProps) {
  return (
    <div className="bg-white border border-slate-200 rounded-xl flex flex-col overflow-hidden shadow-sm h-full">
      <div className="px-5 py-3 border-b border-slate-100 bg-slate-50 flex justify-between items-center">
        <h3 className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Recent Events</h3>
        <div className="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-pulse"></div>
      </div>
      <div className="flex-1 p-5 space-y-3 overflow-y-auto max-h-[250px] text-[10px] font-bold">
        {logs.length === 0 ? (
          <div className="text-slate-400 border-l-2 border-slate-200 pl-3 py-1 opacity-60">System initialized. Waiting for data...</div>
        ) : (
          logs.map((log, i) => (
            <div key={i} className={`pl-3 py-1 border-l-2 ${log.includes('CRITICAL') || log.includes('WARNING') ? 'text-rose-600 border-rose-300' : 'text-slate-500 border-slate-200'}`}>
              {log}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
