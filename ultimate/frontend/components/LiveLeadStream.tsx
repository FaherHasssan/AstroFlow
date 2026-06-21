'use client';
import { useState } from 'react';
import { Activity, X, FileJson, Clock, Hash, CheckCircle2, ShieldOff, Server } from 'lucide-react';
import clsx from 'clsx';

interface LeadActivity {
  id: string;
  timestamp: string;
  source: 'Property Finder' | 'Bayut' | 'Meta Ads';
  name: string;
  phone: string;
  status: 'Synced' | 'Blocked';
  rawJson: string;
}

const LIVE_LEADS: LeadActivity[] = [
  { 
    id: 'ld_98213x', 
    timestamp: '2026-06-21 13:42:10 UTC', 
    source: 'Property Finder', 
    name: 'Faher Hassan', 
    phone: '+971501234567', 
    status: 'Synced', 
    rawJson: '{\n  "source": "propertyfinder",\n  "client": {\n    "name": "Faher Hassan",\n    "phone": "0501234567"\n  }\n}' 
  },
  { 
    id: 'ld_98214y', 
    timestamp: '2026-06-21 13:41:05 UTC', 
    source: 'Meta Ads', 
    name: 'Sara Ahmed', 
    phone: '+971559876543', 
    status: 'Synced', 
    rawJson: '{\n  "source": "meta",\n  "field_data": [\n    {"name": "full_name", "values": ["Sara Ahmed"]},\n    {"name": "phone_number", "values": ["+971559876543"]}\n  ]\n}' 
  },
  { 
    id: 'ld_98215z', 
    timestamp: '2026-06-21 13:40:22 UTC', 
    source: 'Bayut', 
    name: 'John Doe', 
    phone: '+971520001111', 
    status: 'Blocked', 
    rawJson: '{\n  "source": "bayut",\n  "CustomerName": "John Doe",\n  "CustomerPhone": "0520001111"\n}' 
  },
];

export default function LiveLeadStream() {
  const [selectedLead, setSelectedLead] = useState<LeadActivity | null>(null);

  const getSourceBadge = (source: string) => {
    switch(source) {
      case 'Property Finder': 
        return <span className="px-2 py-1 rounded-sm text-[11px] font-semibold tracking-wide bg-blue-500/10 text-blue-400 border border-blue-500/20 uppercase">Property Finder</span>;
      case 'Bayut': 
        return <span className="px-2 py-1 rounded-sm text-[11px] font-semibold tracking-wide bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 uppercase">Bayut</span>;
      case 'Meta Ads': 
        return <span className="px-2 py-1 rounded-sm text-[11px] font-semibold tracking-wide bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 uppercase">Meta Ads</span>;
      default: 
        return null;
    }
  };

  return (
    <div className="rounded-xl border border-zinc-800 bg-[#0c0c0e] shadow-2xl relative overflow-hidden flex flex-col max-h-[600px]">
      <div className="border-b border-zinc-800 px-6 py-4 flex items-center justify-between bg-zinc-900/40 shrink-0">
        <div className="flex items-center gap-3">
          <Activity className="w-5 h-5 text-indigo-400" />
          <h3 className="text-sm font-semibold tracking-wide text-zinc-100 uppercase">Real-Time Ingress Stream</h3>
        </div>
      </div>
      
      <div className="overflow-y-auto flex-1 custom-scrollbar">
        <table className="w-full text-left text-sm whitespace-nowrap">
          <thead className="bg-zinc-950/80 text-zinc-500 uppercase tracking-wider text-[10px] font-bold sticky top-0 z-10 backdrop-blur-sm shadow-sm border-b border-zinc-800">
            <tr>
              <th className="px-6 py-3.5">Ingress Timestamp</th>
              <th className="px-6 py-3.5">Portal Source</th>
              <th className="px-6 py-3.5">Client Identity</th>
              <th className="px-6 py-3.5">Action Target Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-800/50">
            {LIVE_LEADS.map((lead) => (
              <tr 
                key={lead.id} 
                onClick={() => setSelectedLead(lead)}
                className={clsx(
                  "cursor-pointer transition-colors group",
                  lead.status === 'Blocked' 
                    ? "bg-rose-950/10 hover:bg-rose-950/30 text-rose-200/80" 
                    : "hover:bg-zinc-800/30 text-zinc-300",
                  selectedLead?.id === lead.id && "bg-zinc-800/40 ring-1 ring-inset ring-zinc-700"
                )}
              >
                <td className="px-6 py-3.5">
                  <div className="flex items-center gap-2 text-zinc-400">
                    <Clock className="w-3.5 h-3.5 opacity-70 group-hover:text-white transition-colors" />
                    <span className="font-mono text-xs font-medium group-hover:text-white transition-colors">{lead.timestamp}</span>
                  </div>
                </td>
                <td className="px-6 py-3.5">{getSourceBadge(lead.source)}</td>
                <td className="px-6 py-3.5">
                  <div className="font-semibold text-zinc-200">{lead.name}</div>
                  <div className="text-xs text-zinc-500 font-mono mt-0.5 tracking-wide">{lead.phone}</div>
                </td>
                <td className="px-6 py-3.5">
                  {lead.status === 'Synced' ? (
                    <div className="flex items-center gap-2 text-emerald-400 text-xs font-bold tracking-wide uppercase">
                      <CheckCircle2 className="w-4 h-4" /> WhatsApp Link Synced
                    </div>
                  ) : (
                    <div className="flex items-center gap-2 text-rose-400/90 text-xs font-bold tracking-wide uppercase">
                      <ShieldOff className="w-4 h-4" /> Blocked by Budget Shield <span className="font-mono text-[10px] text-rose-500/70 lowercase">(0.00 AED)</span>
                    </div>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Expandable Fly-out Side Drawer for Data Inspection */}
      <div 
        className={clsx(
          "absolute top-0 right-0 h-full w-[480px] bg-[#0c0c0e]/95 backdrop-blur-xl border-l border-zinc-800 shadow-2xl transition-transform duration-300 ease-[cubic-bezier(0.16,1,0.3,1)] flex flex-col z-20", 
          selectedLead ? "translate-x-0" : "translate-x-full"
        )}
      >
        {selectedLead && (
          <>
            <div className="px-6 py-4 border-b border-zinc-800 flex items-center justify-between bg-zinc-900/60 shrink-0">
              <div className="flex items-center gap-2.5">
                <FileJson className="w-4 h-4 text-emerald-400" />
                <h4 className="text-xs font-bold text-zinc-100 uppercase tracking-wider">Raw Payload Inspector</h4>
              </div>
              <button 
                onClick={() => setSelectedLead(null)} 
                className="p-1 hover:bg-zinc-800 border border-transparent hover:border-zinc-700 rounded-md text-zinc-400 hover:text-white transition-all"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            
            <div className="p-6 flex-1 overflow-y-auto space-y-8 custom-scrollbar">
              <div>
                <h5 className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest mb-2 flex items-center gap-1.5"><Hash className="w-3 h-3"/> Internal Audit ID</h5>
                <div className="font-mono text-xs text-zinc-300 bg-zinc-950 px-3 py-2 rounded border border-zinc-800/80 shadow-inner">
                  {selectedLead.id}
                </div>
              </div>

              <div>
                <h5 className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest mb-2 flex items-center gap-1.5"><Server className="w-3 h-3"/> Webhook JSON Ingress Payload</h5>
                <pre className="bg-[#09090b] p-4 rounded-lg border border-zinc-800/80 overflow-x-auto text-xs font-mono text-emerald-400 leading-relaxed shadow-inner">
                  {selectedLead.rawJson}
                </pre>
              </div>
              
              <div>
                 <h5 className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest mb-2 flex items-center gap-1.5"><ShieldAlert className="w-3 h-3"/> Atomic Audit Trail Log</h5>
                 <div className="bg-zinc-950 p-4 rounded-lg border border-zinc-800/80 text-[11px] font-mono space-y-2 text-zinc-400 shadow-inner">
                    <div className="text-zinc-500">[SYS] Ingress timestamp recorded: {selectedLead.timestamp}</div>
                    <div className="text-zinc-400">[EVAL] Executing Budget Guard atomic check via Upstash...</div>
                    {selectedLead.status === 'Synced' ? (
                      <>
                        <div className="text-emerald-400 font-semibold">[PASS] Current daily threshold verified &lt; 1.00 AED</div>
                        <div className="text-zinc-300">[EXEC] Pydantic Schema valid. Polymorphic translation applied.</div>
                        <div className="text-zinc-300">[EXEC] SystemBudgetLedger locked FOR UPDATE.</div>
                        <div className="text-indigo-400 font-semibold">[COMMIT] Cost allocation incremented by +0.000005 AED. Sync Complete.</div>
                      </>
                    ) : (
                      <>
                        <div className="text-rose-500 font-semibold">[FAIL] Budget Guard tripped (Aggregated spend &gt;= limit).</div>
                        <div className="text-rose-400/80">[SHIELD] Terminating ASGI lifecycle. Zero CPU cycles allocated.</div>
                        <div className="text-rose-400/80">[DROP] HTTP 429 Precondition Failed returned upstream.</div>
                      </>
                    )}
                 </div>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
