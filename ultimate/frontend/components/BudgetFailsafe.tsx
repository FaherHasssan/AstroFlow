'use client';
import { useState } from 'react';
import { ShieldAlert, AlertTriangle, Save, Power } from 'lucide-react';
import clsx from 'clsx';

export default function BudgetFailsafe() {
  const [isLocked, setIsLocked] = useState(false);
  const [budgetCap, setBudgetCap] = useState("1.00");
  
  // Simulated real-time consumption metrics
  const currentSpend = 0.8425;
  const maxSpend = parseFloat(budgetCap) || 1.00;
  const percentage = Math.min((currentSpend / maxSpend) * 100, 100);
  
  const handleKillSwitch = () => {
    setIsLocked(!isLocked);
    // In production, this fires an instantaneous API mutation to toggle 'is_locked' on SystemBudgetLedger
  };
  
  return (
    <div className="rounded-xl border border-zinc-800 bg-[#0c0c0e] shadow-2xl overflow-hidden">
      <div className="border-b border-zinc-800 px-6 py-4 flex items-center justify-between bg-zinc-900/40">
        <div className="flex items-center gap-3">
          <ShieldAlert className="w-5 h-5 text-rose-400" />
          <h3 className="text-sm font-semibold tracking-wide text-zinc-100">BUDGET FAILSAFE ENGINE</h3>
        </div>
        <div className={clsx("px-3 py-1 text-xs font-semibold tracking-wider rounded-full border shadow-sm", 
          isLocked ? "bg-rose-500/10 text-rose-400 border-rose-500/20" : "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
        )}>
          {isLocked ? "SYSTEM LOCKED: 429 SHUNT ACTIVE" : "SYSTEM ARMED: INGRESS ACTIVE"}
        </div>
      </div>
      
      <div className="p-6 grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
        <div className="lg:col-span-2 space-y-6">
          <div className="flex justify-between items-end mb-3">
            <div>
              <p className="text-xs font-semibold text-zinc-500 uppercase tracking-wider">Aggregated Daily Spend</p>
              <div className="mt-1 flex items-baseline gap-2">
                <span className="text-4xl font-bold text-white tracking-tight">{currentSpend.toFixed(4)}</span>
                <span className="text-sm font-medium text-zinc-500">AED</span>
              </div>
            </div>
            <div className="text-right">
              <p className="text-xs font-semibold text-zinc-500 uppercase tracking-wider">Hard Ceiling Limit</p>
              <div className="mt-1 flex items-baseline gap-2 justify-end">
                <span className="text-2xl font-semibold text-zinc-300">{maxSpend.toFixed(2)}</span>
                <span className="text-sm font-medium text-zinc-500">AED</span>
              </div>
            </div>
          </div>
          
          <div className="relative h-3 w-full bg-zinc-900/80 rounded-full overflow-hidden shadow-inner border border-zinc-800/50">
            <div 
              className={clsx(
                "absolute top-0 left-0 h-full transition-all duration-700 ease-in-out", 
                percentage > 90 ? "bg-rose-500" : percentage > 70 ? "bg-amber-500" : "bg-emerald-500"
              )}
              style={{ width: `${percentage}%` }}
            />
          </div>
          <p className="text-xs font-medium text-zinc-500 mt-3 flex items-center gap-1.5">
            <AlertTriangle className="w-3.5 h-3.5" /> Circuit breaker isolates ingress routing and drops execution exactly at {maxSpend.toFixed(2)} AED.
          </p>
        </div>
        
        <div className="space-y-6 lg:border-l lg:border-zinc-800 lg:pl-8">
          <div>
             <label className="block text-xs font-bold text-zinc-500 uppercase tracking-wider mb-2.5">Manual Emergency Controls</label>
             <button 
                onClick={handleKillSwitch}
                className={clsx(
                  "w-full flex items-center justify-center gap-2 py-2.5 px-4 rounded-md text-sm font-semibold border shadow-sm transition-all", 
                  isLocked 
                    ? "bg-rose-500/10 text-rose-400 border-rose-500/30 hover:bg-rose-500/20 shadow-rose-500/10" 
                    : "bg-zinc-800/80 text-zinc-200 border-zinc-700 hover:bg-zinc-700 hover:text-white"
                )}
             >
                <Power className="w-4 h-4" /> 
                {isLocked ? "Unlock System Engine" : "Global System Kill-Switch"}
             </button>
          </div>
          
          <div>
             <label className="block text-xs font-bold text-zinc-500 uppercase tracking-wider mb-2.5">Localized Scaling Target (AED)</label>
             <div className="flex gap-2">
                <input 
                  type="number" 
                  value={budgetCap}
                  onChange={(e) => setBudgetCap(e.target.value)}
                  step="0.01"
                  min="0.01"
                  max="1.00"
                  className="bg-zinc-950 border border-zinc-700 text-zinc-200 text-sm font-medium rounded-md px-3 py-2 w-full focus:outline-none focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/50 shadow-inner"
                />
                <button className="bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 px-3.5 rounded-md hover:bg-emerald-500/20 transition-colors shadow-sm flex items-center justify-center">
                  <Save className="w-4 h-4" />
                </button>
             </div>
          </div>
        </div>
      </div>
    </div>
  );
}
