import BudgetFailsafe from '@/components/BudgetFailsafe';
import LiveLeadStream from '@/components/LiveLeadStream';
import IntegrationGateways from '@/components/IntegrationGateways';

export default function DashboardPage() {
  return (
    <div className="max-w-7xl mx-auto space-y-10 pb-12">
      <div className="mb-8">
        <h2 className="text-2xl font-semibold text-white tracking-tight">Platform Operations</h2>
        <p className="text-zinc-400 text-sm mt-1.5 max-w-2xl">
          Real-time engine metrics, active budget gates, and live synchronization status across your multi-tenant environment.
        </p>
      </div>

      <section id="failsafe" className="scroll-mt-24">
        <BudgetFailsafe />
      </section>

      <section id="leads" className="scroll-mt-24">
        <LiveLeadStream />
      </section>

      <section id="gateways" className="scroll-mt-24">
        <IntegrationGateways />
      </section>
    </div>
  );
}
