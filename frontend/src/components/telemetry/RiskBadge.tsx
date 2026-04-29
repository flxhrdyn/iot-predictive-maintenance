interface RiskBadgeProps {
  level: 'SAFE' | 'MEDIUM' | 'HIGH';
  probability: number;
}

export function RiskBadge({ level, probability }: RiskBadgeProps) {
  const getRiskStyles = (level: string) => {
    switch (level) {
      case 'HIGH': return 'bg-rose-50 border-rose-200 text-rose-800';
      case 'MEDIUM': return 'bg-amber-50 border-amber-200 text-amber-800';
      default: return 'bg-emerald-50 border-emerald-200 text-emerald-800';
    }
  };

  return (
    <div className={`rounded-xl p-6 flex flex-col justify-center border-2 ${getRiskStyles(level)} h-full`}>
      <h2 className="text-[10px] font-black uppercase tracking-widest mb-2 opacity-70">Machine Risk Level</h2>
      <div className="text-5xl font-black mb-1 tracking-tighter">{level}</div>
      <p className="text-sm font-mono font-black opacity-60 uppercase">prob: {(probability * 100).toFixed(2)}%</p>
    </div>
  );
}
