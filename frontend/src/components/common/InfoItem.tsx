interface InfoItemProps {
  label: string;
  value: string | number;
  highlight?: boolean;
  warning?: boolean;
}

export function InfoItem({ label, value, highlight, warning }: InfoItemProps) {
  return (
    <div>
      <p className="text-[9px] font-bold text-slate-400 uppercase mb-1">{label}</p>
      <p className={`text-sm font-black ${highlight ? 'text-indigo-600 font-mono' : warning ? 'text-amber-600 font-mono' : 'text-slate-700'}`}>{value}</p>
    </div>
  );
}
