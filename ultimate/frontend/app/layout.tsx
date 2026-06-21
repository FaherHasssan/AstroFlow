import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { Building2, Activity, Settings, ShieldAlert, LayoutDashboard } from 'lucide-react';
import clsx from 'clsx';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'AstroFlow - Admin Platform',
  description: 'Zero-touch automated multi-tenant real estate lead platform',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className={clsx(inter.className, "bg-[#09090b] text-zinc-100 antialiased h-screen flex overflow-hidden")}>
        
        {/* COMPREHENSIVE CONTROL BASE ENVIRONMENT: Sidebar */}
        <aside className="w-64 border-r border-zinc-800 bg-[#0c0c0e] flex flex-col flex-shrink-0 relative z-20">
          <div className="h-16 flex items-center px-6 border-b border-zinc-800">
            <span className="font-semibold text-lg tracking-tight text-white flex items-center gap-2">
              <div className="w-6 h-6 rounded bg-emerald-500/20 border border-emerald-500/50 flex items-center justify-center shadow-inner">
                <Building2 className="w-3.5 h-3.5 text-emerald-400" />
              </div>
              AstroFlow
            </span>
          </div>
          
          <nav className="flex-1 overflow-y-auto py-6 px-3 space-y-1.5">
            <a href="#" className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md bg-zinc-800/50 text-white border border-zinc-700/50 shadow-sm">
              <LayoutDashboard className="w-4 h-4 text-zinc-400" /> Analytics Control
            </a>
            <a href="#leads" className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md text-zinc-400 hover:text-white hover:bg-zinc-800/50 transition-colors">
              <Activity className="w-4 h-4 text-emerald-400" /> Live Lead Stream
            </a>
            <a href="#gateways" className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md text-zinc-400 hover:text-white hover:bg-zinc-800/50 transition-colors">
              <Settings className="w-4 h-4 text-zinc-400" /> Integration Gateways
            </a>
            <a href="#failsafe" className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md text-zinc-400 hover:text-white hover:bg-zinc-800/50 transition-colors">
              <ShieldAlert className="w-4 h-4 text-rose-400" /> Budget Failsafe Engine
            </a>
          </nav>
          
          <div className="p-4 border-t border-zinc-800 text-xs font-mono text-zinc-500 flex items-center justify-between">
            <span>System Online</span>
            <span className="flex items-center gap-1.5"><span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span> UAE-North</span>
          </div>
        </aside>

        {/* Main Content Area */}
        <div className="flex-1 flex flex-col min-w-0 overflow-hidden relative z-10">
          
          {/* Active Multi-Tenant Branch Selector Banner */}
          <header className="h-16 border-b border-zinc-800 bg-[#0c0c0e]/80 backdrop-blur-md flex items-center justify-between px-8 flex-shrink-0">
            <div className="flex items-center gap-4">
               <h1 className="text-sm font-medium text-zinc-300 tracking-wide">Command Center</h1>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-xs text-zinc-500 uppercase tracking-wider font-semibold">Active Branch View</span>
              <select className="bg-zinc-900 border border-zinc-800 text-sm font-medium rounded-md px-3 py-1.5 focus:outline-none focus:ring-1 focus:ring-emerald-500/50 text-zinc-200 cursor-pointer hover:bg-zinc-800 transition-colors">
                <option value="hq">Downtown Dubai (Global HQ)</option>
                <option value="marina">Dubai Marina Branch</option>
                <option value="ad">Abu Dhabi Operations</option>
              </select>
            </div>
          </header>
          
          <main className="flex-1 overflow-y-auto p-8 bg-[#09090b]">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
