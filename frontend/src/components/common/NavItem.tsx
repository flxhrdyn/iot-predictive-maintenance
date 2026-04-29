import React, { ReactElement } from 'react';

interface NavItemProps {
  icon: ReactElement;
  label: string;
  active?: boolean;
}

export function NavItem({ icon, label, active }: NavItemProps) {
  return (
    <a href="#" className={`flex items-center gap-3 px-3 py-2 rounded-lg transition-all ${active ? 'bg-white/10 text-white' : 'text-slate-400 hover:bg-white/5 hover:text-slate-200'}`}>
      {React.cloneElement(icon, { size: 16 } as any)}
      <span className="font-semibold text-xs uppercase tracking-wider">{label}</span>
    </a>
  );
}
