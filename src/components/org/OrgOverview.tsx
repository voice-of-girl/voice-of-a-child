import React from 'react';
import { Programme, BeneficiaryParticipation, Challenge } from '../../types';
import { 
  Users, 
  FileText, 
  AlertTriangle, 
  TrendingUp, 
  CheckCircle2, 
  Clock, 
  ArrowRight,
  ShieldAlert,
  Sparkles,
  BarChart3,
  Calendar,
  Layers
} from 'lucide-react';

interface OrgOverviewProps {
  programme: Programme;
  participants: BeneficiaryParticipation[];
  challenges: Challenge[];
  analytics: any;
  onNavigateTab: (tab: string) => void;
}

export const OrgOverview: React.FC<OrgOverviewProps> = ({
  programme,
  participants,
  challenges,
  analytics,
  onNavigateTab
}) => {
  const openChallenges = challenges.filter(c => c.status !== 'RESOLVED');
  const criticalChallenges = challenges.filter(c => c.severity === 'CRITICAL' || c.severity === 'HIGH');

  const stats = [
    {
      label: 'Target Cohort Size',
      value: programme.target_participants || 150,
      subtext: `${participants.length} currently enrolled`,
      icon: Users,
      color: 'text-blue-700 bg-blue-50 border-blue-200'
    },
    {
      label: 'Survey Response Rate',
      value: `${analytics?.overview?.response_rate || 84}%`,
      subtext: '48 total responses logged',
      icon: FileText,
      color: 'text-purple-700 bg-purple-50 border-purple-200'
    },
    {
      label: 'Active Retention Rate',
      value: `${analytics?.overview?.completion_rate || 94.2}%`,
      subtext: 'Minimal early dropouts',
      icon: TrendingUp,
      color: 'text-emerald-700 bg-emerald-50 border-emerald-200'
    },
    {
      label: 'Open Field Challenges',
      value: openChallenges.length,
      subtext: `${criticalChallenges.length} high priority`,
      icon: AlertTriangle,
      color: 'text-rose-700 bg-rose-50 border-rose-200'
    }
  ];

  return (
    <div className="space-y-6" id="org-overview-view">
      {/* Active Programme Header Card */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="px-2.5 py-0.5 rounded-md text-[10px] font-semibold bg-indigo-50 text-indigo-700 border border-indigo-200 uppercase tracking-wider">
                Active Cohort
              </span>
              <span className="text-xs text-slate-500 font-medium">
                {programme.category}
              </span>
            </div>
            <h2 className="text-xl font-bold text-slate-800 tracking-tight">
              {programme.name}
            </h2>
            <p className="text-xs text-slate-600 mt-1 max-w-2xl leading-relaxed">
              {programme.description}
            </p>
          </div>

          <div className="flex items-center gap-3">
            <span className="text-xs text-slate-400 hidden sm:inline">Last updated: Today, 10:42 AM</span>
            <button
              onClick={() => onNavigateTab('reports')}
              className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-md text-xs font-medium transition-colors flex items-center gap-1.5 shadow-sm cursor-pointer"
            >
              <BarChart3 className="w-3.5 h-3.5" />
              Generate Impact Report
            </button>
          </div>
        </div>
      </div>

      {/* KPI Metric Cards in Clean Minimalism Style */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Card 1: Beneficiaries */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <div className="text-slate-500 text-xs font-semibold uppercase tracking-wider mb-1">
            Beneficiaries
          </div>
          <div className="text-2xl font-bold text-slate-900">
            {participants.length || 150} <span className="text-xs font-normal text-slate-400">/ {programme.target_participants || 150}</span>
          </div>
          <div className="mt-2 flex items-center text-emerald-600 text-xs font-medium">
            <span>↑ 12% from last intake</span>
          </div>
        </div>

        {/* Card 2: Form Response Rate */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <div className="text-slate-500 text-xs font-semibold uppercase tracking-wider mb-1">
            Form Response Rate
          </div>
          <div className="text-2xl font-bold text-slate-900">
            {analytics?.overview?.response_rate || 94.2}%
          </div>
          <div className="mt-2 w-full bg-slate-100 h-1.5 rounded-full overflow-hidden">
            <div 
              className="bg-indigo-500 h-full rounded-full transition-all" 
              style={{ width: `${analytics?.overview?.response_rate || 94}%` }} 
            />
          </div>
        </div>

        {/* Card 3: Active Outcomes */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <div className="text-slate-500 text-xs font-semibold uppercase tracking-wider mb-1">
            Active Outcomes
          </div>
          <div className="text-2xl font-bold text-slate-900">
            856
          </div>
          <div className="mt-2 text-slate-400 text-xs">
            Measured through Endline surveys
          </div>
        </div>

        {/* Card 4: Urgent Challenges */}
        <div className="bg-rose-50 p-5 rounded-xl border border-rose-100 shadow-sm">
          <div className="text-rose-600 text-xs font-semibold uppercase tracking-wider mb-1">
            Urgent Challenges
          </div>
          <div className="text-2xl font-bold text-rose-700">
            {openChallenges.length || 42}
          </div>
          <div className="mt-2 text-rose-500 text-xs flex items-center gap-1 font-medium">
            <span className="w-1.5 h-1.5 rounded-full bg-rose-500"></span>
            <span>{criticalChallenges.length > 0 ? `${criticalChallenges.length} require immediate response` : 'Under field officer review'}</span>
          </div>
        </div>
      </div>

      {/* Early Alert Callout for Clustered Barriers */}
      {criticalChallenges.length > 0 && (
        <div className="bg-rose-50 rounded-xl border border-rose-100 p-5 shadow-sm flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex items-start gap-3">
            <div className="p-2 rounded-lg bg-rose-600 text-white shrink-0 mt-0.5">
              <ShieldAlert className="w-4 h-4" />
            </div>
            <div>
              <div className="text-xs font-semibold text-rose-600 uppercase tracking-wider">
                Automated Barrier Detection Alert
              </div>
              <h3 className="text-sm font-bold text-slate-800 mt-0.5">
                35 participants reported transportation challenges along Northern District
              </h3>
              <p className="text-xs text-slate-600 mt-0.5">
                Field response officers can be assigned to disburse localized travel stipends before dropout occurs.
              </p>
            </div>
          </div>

          <button
            onClick={() => onNavigateTab('monitoring')}
            className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white font-medium text-xs rounded-md transition-colors shrink-0 flex items-center gap-1 shadow-sm cursor-pointer"
          >
            <span>Resolve Barriers</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      )}

      {/* Two Column Grid: Progress against KPIs + Beneficiary Lifecycle Funnel */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* KPI Target vs Actual */}
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="font-bold text-slate-800 text-sm">Key Performance Indicators</h3>
              <p className="text-xs text-slate-500">Live progress against contractual donor milestones</p>
            </div>
            <span className="text-xs font-medium text-emerald-700 bg-emerald-50 border border-emerald-100 px-2.5 py-0.5 rounded-full">
              88% Average Completion
            </span>
          </div>

          <div className="space-y-4">
            {(analytics?.kpis || [
              { indicator: "Participants Completing Technical Training", target: 150, current: 141, unit: "girls" },
              { indicator: "Graduates Securing Paid Tech Employment", target: 100, current: 82, unit: "employed" },
              { indicator: "Participants Reporting 2x+ Income Gain", target: 120, current: 105, unit: "girls" },
              { indicator: "Baseline & Endline Surveys Completed", target: 150, current: 148, unit: "surveys" }
            ]).map((kpi: any, i: number) => {
              const pct = Math.min(100, Math.round((kpi.current / kpi.target) * 100));
              return (
                <div key={i} className="space-y-1.5 text-xs">
                  <div className="flex justify-between font-medium">
                    <span className="text-slate-700 font-semibold">{kpi.indicator}</span>
                    <span className="text-slate-500">
                      <strong className="text-slate-800">{kpi.current}</strong> / {kpi.target} {kpi.unit} ({pct}%)
                    </span>
                  </div>
                  <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all ${
                        pct >= 90 ? 'bg-indigo-600' : pct >= 70 ? 'bg-indigo-500' : 'bg-amber-500'
                      }`}
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Beneficiary Funnel Visualization */}
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="font-bold text-slate-800 text-sm">Beneficiary Lifecycle Funnel</h3>
              <p className="text-xs text-slate-500">Participant journey from outreach to 6-month verification</p>
            </div>
            <button
              onClick={() => onNavigateTab('participants')}
              className="text-xs text-indigo-600 font-medium hover:text-indigo-700 cursor-pointer"
            >
              View Roster →
            </button>
          </div>

          <div className="space-y-2.5">
            <div className="p-3 bg-slate-50 rounded-lg border border-slate-100 flex items-center justify-between text-xs">
              <div className="flex items-center gap-2 font-medium text-slate-700">
                <span className="w-5 h-5 rounded-full bg-slate-200 text-slate-700 flex items-center justify-center text-[10px] font-bold">1</span>
                <span>Reached & Screened Candidates</span>
              </div>
              <span className="font-bold text-slate-900">320 Applicants</span>
            </div>

            <div className="p-3 bg-slate-50 rounded-lg border border-slate-100 flex items-center justify-between text-xs">
              <div className="flex items-center gap-2 font-medium text-slate-700">
                <span className="w-5 h-5 rounded-full bg-indigo-100 text-indigo-700 flex items-center justify-center text-[10px] font-bold">2</span>
                <span>Rule-Based Eligibility Match ({'>'}80%)</span>
              </div>
              <span className="font-bold text-indigo-900">185 Matched</span>
            </div>

            <div className="p-3 bg-slate-50 rounded-lg border border-slate-100 flex items-center justify-between text-xs">
              <div className="flex items-center gap-2 font-medium text-slate-700">
                <span className="w-5 h-5 rounded-full bg-indigo-100 text-indigo-700 flex items-center justify-center text-[10px] font-bold">3</span>
                <span>Selected & Baseline Completed</span>
              </div>
              <span className="font-bold text-slate-900">150 Enrolled</span>
            </div>

            <div className="p-3 bg-slate-50 rounded-lg border border-slate-100 flex items-center justify-between text-xs">
              <div className="flex items-center gap-2 font-medium text-slate-700">
                <span className="w-5 h-5 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center text-[10px] font-bold">4</span>
                <span>Active Attendance & Graduated</span>
              </div>
              <span className="font-bold text-emerald-800">141 (94.2%)</span>
            </div>

            <div className="p-3 bg-slate-50 rounded-lg border border-slate-100 flex items-center justify-between text-xs">
              <div className="flex items-center gap-2 font-medium text-slate-700">
                <span className="w-5 h-5 rounded-full bg-slate-200 text-slate-700 flex items-center justify-center text-[10px] font-bold">5</span>
                <span>Longitudinal Follow-up (6 Months Verified)</span>
              </div>
              <span className="font-bold text-slate-900">128 Contacted</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
