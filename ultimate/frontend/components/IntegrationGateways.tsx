import { Link2, Webhook, MessageCircle, ServerCog } from 'lucide-react';

interface GatewayField {
  label: string;
  placeholder: string;
  type?: 'text' | 'password';
}

interface GatewayCardProps {
  title: string;
  description: string;
  icon: React.ReactNode;
  fields: GatewayField[];
}

function GatewayCard({ title, description, icon, fields }: GatewayCardProps) {
  return (
    <div className="border border-zinc-800 bg-zinc-900/30 rounded-xl p-6 flex flex-col h-full shadow-sm hover:bg-zinc-900/50 transition-colors">
      <div className="flex items-center gap-3 mb-3">
        <div className="p-2.5 bg-zinc-950 rounded-lg border border-zinc-800/80 shadow-inner">
          {icon}
        </div>
        <h4 className="text-sm font-bold tracking-wide text-zinc-100 uppercase">{title}</h4>
      </div>
      <p className="text-xs text-zinc-400 mb-6 flex-1 leading-relaxed">{description}</p>
      
      <div className="space-y-4 mb-6">
        {fields.map((field, idx) => (
          <div key={idx}>
            <label className="block text-[10px] font-bold text-zinc-500 uppercase tracking-widest mb-1.5">{field.label}</label>
            <input 
              type={field.type || "text"} 
              placeholder={field.placeholder}
              className="w-full bg-zinc-950 border border-zinc-800 rounded-md px-3 py-2.5 text-sm font-mono text-zinc-200 focus:outline-none focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/50 transition-all placeholder-zinc-700 shadow-inner"
            />
          </div>
        ))}
      </div>
      
      <button className="mt-auto w-full py-2.5 px-4 bg-zinc-800/80 hover:bg-zinc-700 border border-zinc-700 hover:border-zinc-600 rounded-md text-xs font-bold tracking-wide uppercase text-zinc-200 transition-colors flex items-center justify-center gap-2 shadow-sm">
        <ServerCog className="w-4 h-4" /> Test Connection Pipeline
      </button>
    </div>
  );
}

export default function IntegrationGateways() {
  return (
    <div className="rounded-xl border border-zinc-800 bg-[#0c0c0e] shadow-2xl overflow-hidden">
      <div className="border-b border-zinc-800 px-6 py-4 flex items-center justify-between bg-zinc-900/40">
        <div className="flex items-center gap-3">
          <Settings className="w-5 h-5 text-teal-400" />
          <h3 className="text-sm font-semibold tracking-wide text-zinc-100 uppercase">Integration Gateways & Provisioning</h3>
        </div>
      </div>
      
      <div className="p-6 grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
        <GatewayCard 
          title="Meta Graph Pipeline"
          description="Authenticate with the Facebook Graph API to ingest real-time Meta Lead Generation form submissions directly into the platform."
          icon={<Link2 className="w-5 h-5 text-indigo-400" />}
          fields={[
            { label: "Graph API Access Token", placeholder: "EAA...", type: "password" },
            { label: "Graph Application Secret", placeholder: "Enter your Meta App Secret", type: "password" }
          ]}
        />
        
        <GatewayCard 
          title="UAE Property Portals"
          description="Generate mathematically unique, secure webhook URLs to provision directly within Property Finder and Bayut dashboards."
          icon={<Webhook className="w-5 h-5 text-emerald-400" />}
          fields={[
            { label: "Assigned Ingress Webhook Endpoint", placeholder: "https://api.ultimate360.ae/webhook/pf_x92" },
            { label: "Authorization Payload Signature", placeholder: "HMAC Verification Secret", type: "password" }
          ]}
        />
        
        <GatewayCard 
          title="WhatsApp Context Trackers"
          description="Configure pre-seeded agency conversation templates and establish default routing numbers for the zero-cost shortlinks."
          icon={<MessageCircle className="w-5 h-5 text-blue-400" />}
          fields={[
            { label: "Default Forwarding Cell", placeholder: "+971 50 000 0000" },
            { label: "Pre-seeded Agency Conversational Template", placeholder: "Hi [CustomerName], about your inquiry..." }
          ]}
        />
      </div>
    </div>
  );
}

// Inline definition to support the icon inside the local file cleanly
import { Settings } from 'lucide-react';
