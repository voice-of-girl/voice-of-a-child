import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { UserRole } from '../types';
import { 
  ArrowRight, 
  CheckCircle2, 
  Users, 
  FileSpreadsheet, 
  Activity, 
  TrendingUp, 
  BarChart3, 
  ShieldCheck, 
  Search, 
  AlertTriangle, 
  FileText,
  Building2,
  GraduationCap,
  Sparkles,
  Award
} from 'lucide-react';

interface LandingPageProps {
  onEnterApp: () => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({ onEnterApp }) => {
  const { switchRole, register, login } = useAuth();
  const [showAuthModal, setShowAuthModal] = useState<null | 'ORG' | 'BENEFICIARY' | 'LOGIN'>(null);
  const [authEmail, setAuthEmail] = useState('');
  const [authOrgName, setAuthOrgName] = useState('');
  const [authFirstName, setAuthFirstName] = useState('');
  const [authLastName, setAuthLastName] = useState('');

  const handleAuthSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (showAuthModal === 'LOGIN') {
      login(authEmail);
    } else if (showAuthModal === 'ORG') {
      await register({
        email: authEmail,
        first_name: authFirstName || 'Org',
        last_name: authLastName || 'Director',
        role: 'ORGANISATION_ADMIN',
        organisation_name: authOrgName || 'New Foundation'
      });
    } else if (showAuthModal === 'BENEFICIARY') {
      await register({
        email: authEmail,
        first_name: authFirstName || 'Applicant',
        last_name: authLastName || 'Youth',
        role: 'BENEFICIARY'
      });
    }
    setShowAuthModal(null);
    onEnterApp();
  };

  const selectPersonaAndGo = (role: UserRole) => {
    switchRole(role);
    onEnterApp();
  };

  return (
    <div className="min-h-screen bg-[#F9FAFB] text-slate-900 flex flex-col justify-between" id="landing-page">
      {/* Hero Section */}
      <section className="relative overflow-hidden pt-16 pb-20 lg:pt-24 lg:pb-28 bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="text-center max-w-4xl mx-auto">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-md text-xs font-semibold bg-indigo-50 text-indigo-700 border border-indigo-100 mb-6">
              <Sparkles className="w-3.5 h-3.5" />
              B2B SaaS for Beneficiary Management & Outcome Measurement
            </div>

            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-black text-slate-900 tracking-tight leading-[1.15]">
              Reach the right people. <br className="hidden sm:inline" />
              <span className="text-indigo-600">Monitor your programmes.</span> <br />
              Measure what changes.
            </h1>

            <p className="mt-6 text-base sm:text-lg text-slate-500 max-w-2xl mx-auto leading-relaxed">
              The purpose-built data platform for NGOs, foundations, training institutions, and donors supporting girls and young women.
            </p>

            {/* Action Buttons */}
            <div className="mt-8 flex flex-wrap items-center justify-center gap-3 sm:gap-4">
              <button
                onClick={() => setShowAuthModal('ORG')}
                className="px-5 py-2.5 rounded-md bg-slate-900 hover:bg-slate-800 text-white font-medium text-sm shadow-sm transition-colors cursor-pointer flex items-center gap-2"
                id="btn-register-org"
              >
                <Building2 className="w-4 h-4" />
                Register Organisation
              </button>

              <button
                onClick={() => setShowAuthModal('BENEFICIARY')}
                className="px-5 py-2.5 rounded-md bg-white hover:bg-slate-50 text-slate-700 font-medium text-sm border border-slate-200 shadow-xs transition-colors cursor-pointer flex items-center gap-2"
                id="btn-join-participant"
              >
                <GraduationCap className="w-4 h-4" />
                Join as Participant
              </button>

              <button
                onClick={() => setShowAuthModal('LOGIN')}
                className="px-5 py-2.5 rounded-md bg-slate-100 hover:bg-slate-200 text-slate-800 font-medium text-sm transition-colors cursor-pointer"
                id="btn-login"
              >
                Sign In
              </button>
            </div>

            {/* Instant Demo Role Personas (Quick Preview) */}
            <div className="mt-12 pt-8 border-t border-slate-100 max-w-3xl mx-auto">
              <div className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-3">
                Or jump straight in with an interactive role persona:
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
                <button
                  onClick={() => selectPersonaAndGo('ORGANISATION_ADMIN')}
                  className="p-3 rounded-lg bg-slate-50 hover:bg-indigo-50/50 border border-slate-200 hover:border-indigo-200 transition-colors text-left cursor-pointer group"
                >
                  <div className="text-xs font-semibold text-slate-900 group-hover:text-indigo-700 flex items-center justify-between">
                    <span>Org Admin</span>
                    <ArrowRight className="w-3 h-3 text-slate-400 group-hover:text-indigo-600" />
                  </div>
                  <div className="text-[11px] text-slate-500 mt-0.5 truncate">FemmeTech Africa</div>
                </button>

                <button
                  onClick={() => selectPersonaAndGo('BENEFICIARY')}
                  className="p-3 rounded-lg bg-slate-50 hover:bg-emerald-50/50 border border-slate-200 hover:border-emerald-200 transition-colors text-left cursor-pointer group"
                >
                  <div className="text-xs font-semibold text-slate-900 group-hover:text-emerald-700 flex items-center justify-between">
                    <span>Beneficiary</span>
                    <ArrowRight className="w-3 h-3 text-slate-400 group-hover:text-emerald-600" />
                  </div>
                  <div className="text-[11px] text-slate-500 mt-0.5 truncate">Fatima (Scholarship)</div>
                </button>

                <button
                  onClick={() => selectPersonaAndGo('FIELD_OFFICER')}
                  className="p-3 rounded-lg bg-slate-50 hover:bg-blue-50/50 border border-slate-200 hover:border-blue-200 transition-colors text-left cursor-pointer group"
                >
                  <div className="text-xs font-semibold text-slate-900 group-hover:text-blue-700 flex items-center justify-between">
                    <span>Field Officer</span>
                    <ArrowRight className="w-3 h-3 text-slate-400 group-hover:text-blue-600" />
                  </div>
                  <div className="text-[11px] text-slate-500 mt-0.5 truncate">Sarah (Field Visits)</div>
                </button>

                <button
                  onClick={() => selectPersonaAndGo('PLATFORM_ADMIN')}
                  className="p-3 rounded-lg bg-slate-50 hover:bg-amber-50/50 border border-slate-200 hover:border-amber-200 transition-colors text-left cursor-pointer group"
                >
                  <div className="text-xs font-semibold text-slate-900 group-hover:text-amber-700 flex items-center justify-between">
                    <span>Platform Admin</span>
                    <ArrowRight className="w-3 h-3 text-slate-400 group-hover:text-amber-600" />
                  </div>
                  <div className="text-[11px] text-slate-500 mt-0.5 truncate">System Governance</div>
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Core Value Chain Section */}
      <section className="py-16 bg-slate-900 text-white" id="value-chain-section">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-12">
            <span className="text-indigo-400 text-xs font-semibold tracking-widest uppercase">The Platform Journey</span>
            <h2 className="text-2xl sm:text-3xl font-bold mt-1 tracking-tight">
              REACH → MANAGE → COLLECT → MONITOR → RESPOND → MEASURE → REPORT
            </h2>
            <p className="text-slate-400 text-sm mt-3">
              A unified lifecycle connecting participant recruitment, custom Google Forms-style data collection, early challenge intervention, and longitudinal impact proof.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* New Programme Track */}
            <div className="p-6 rounded-xl bg-slate-800/80 border border-slate-700">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-md text-xs font-semibold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 mb-4">
                Track A: For a New Programme
              </div>
              <ol className="space-y-3 text-xs sm:text-sm text-slate-300">
                <li className="flex items-start gap-3">
                  <span className="w-6 h-6 rounded-full bg-slate-700 text-indigo-300 flex items-center justify-center font-bold text-xs shrink-0">1</span>
                  <div><strong>Create Programme:</strong> Set criteria, target cohort numbers, and geographic focus.</div>
                </li>
                <li className="flex items-start gap-3">
                  <span className="w-6 h-6 rounded-full bg-slate-700 text-indigo-300 flex items-center justify-center font-bold text-xs shrink-0">2</span>
                  <div><strong>Find & Select:</strong> Transparent rule-based match scores compare age, education, and skills.</div>
                </li>
                <li className="flex items-start gap-3">
                  <span className="w-6 h-6 rounded-full bg-slate-700 text-indigo-300 flex items-center justify-center font-bold text-xs shrink-0">3</span>
                  <div><strong>Baseline Intake:</strong> Document participant starting point before activities commence.</div>
                </li>
                <li className="flex items-start gap-3">
                  <span className="w-6 h-6 rounded-full bg-slate-700 text-indigo-300 flex items-center justify-center font-bold text-xs shrink-0">4</span>
                  <div><strong>Monitor & Respond:</strong> Real-time pulse checks detect transport or resource challenges early.</div>
                </li>
                <li className="flex items-start gap-3">
                  <span className="w-6 h-6 rounded-full bg-slate-700 text-indigo-300 flex items-center justify-center font-bold text-xs shrink-0">5</span>
                  <div><strong>Measure & Report:</strong> Compare Baseline vs. Endline vs. 6-Month Follow-Up and export for donors.</div>
                </li>
              </ol>
            </div>

            {/* Existing Programme Track */}
            <div className="p-6 rounded-xl bg-slate-800/80 border border-slate-700">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-md text-xs font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 mb-4">
                Track B: For an Existing Programme
              </div>
              <ol className="space-y-3 text-xs sm:text-sm text-slate-300">
                <li className="flex items-start gap-3">
                  <span className="w-6 h-6 rounded-full bg-slate-700 text-emerald-400 flex items-center justify-center font-bold text-xs shrink-0">1</span>
                  <div><strong>Register Existing Programme:</strong> Digitize ongoing cohorts and historical targets.</div>
                </li>
                <li className="flex items-start gap-3">
                  <span className="w-6 h-6 rounded-full bg-slate-700 text-emerald-400 flex items-center justify-center font-bold text-xs shrink-0">2</span>
                  <div><strong>Add Participants:</strong> Bulk upload or link registered girls with field officer verification.</div>
                </li>
                <li className="flex items-start gap-3">
                  <span className="w-6 h-6 rounded-full bg-slate-700 text-emerald-400 flex items-center justify-center font-bold text-xs shrink-0">3</span>
                  <div><strong>Collect Active Data:</strong> Deploy custom monitoring surveys and record weekly attendance.</div>
                </li>
                <li className="flex items-start gap-3">
                  <span className="w-6 h-6 rounded-full bg-slate-700 text-emerald-400 flex items-center justify-center font-bold text-xs shrink-0">4</span>
                  <div><strong>Identify Challenges:</strong> Aggregate recurring issues (e.g. 35 participants reporting transport issues).</div>
                </li>
                <li className="flex items-start gap-3">
                  <span className="w-6 h-6 rounded-full bg-slate-700 text-emerald-400 flex items-center justify-center font-bold text-xs shrink-0">5</span>
                  <div><strong>Measure Results:</strong> Quantify employment gains, digital skills rise, and generate executive reports.</div>
                </li>
              </ol>
            </div>
          </div>
        </div>
      </section>

      {/* Key Feature Pillars */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-12">
            <h2 className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
              Built Specifically for Purpose-Driven Organisations
            </h2>
            <p className="text-slate-500 text-sm mt-2">
              Everything required to manage participants, monitor in real-time, and prove measurable outcomes.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="p-6 rounded-xl bg-white border border-slate-200 shadow-sm">
              <div className="w-10 h-10 rounded-lg bg-indigo-50 border border-indigo-100 text-indigo-700 flex items-center justify-center mb-4">
                <FileSpreadsheet className="w-5 h-5" />
              </div>
              <h3 className="font-bold text-slate-900 text-base">Google Forms-Style Custom Builder</h3>
              <p className="text-slate-500 text-xs sm:text-sm mt-2 leading-relaxed">
                Build Baseline, Monitoring, Endline, and Follow-Up surveys with 10 question types. No code required.
              </p>
            </div>

            <div className="p-6 rounded-xl bg-white border border-slate-200 shadow-sm">
              <div className="w-10 h-10 rounded-lg bg-amber-50 border border-amber-100 text-amber-700 flex items-center justify-center mb-4">
                <AlertTriangle className="w-5 h-5" />
              </div>
              <h3 className="font-bold text-slate-900 text-base">Early Challenge Detection</h3>
              <p className="text-slate-500 text-xs sm:text-sm mt-2 leading-relaxed">
                Automatically aggregate participant hurdles during active programmes so response teams can intervene early.
              </p>
            </div>

            <div className="p-6 rounded-xl bg-white border border-slate-200 shadow-sm">
              <div className="w-10 h-10 rounded-lg bg-emerald-50 border border-emerald-100 text-emerald-700 flex items-center justify-center mb-4">
                <TrendingUp className="w-5 h-5" />
              </div>
              <h3 className="font-bold text-slate-900 text-base">BEFORE → AFTER → CHANGE</h3>
              <p className="text-slate-500 text-xs sm:text-sm mt-2 leading-relaxed">
                Rigorous outcome tracking across employment, skills, income, and business establishment with 1-click PDF/Excel export.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Auth / Register Modal */}
      {showAuthModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/40 backdrop-blur-xs p-4">
          <div className="bg-white rounded-xl max-w-md w-full p-6 shadow-xl border border-slate-200 relative">
            <button
              onClick={() => setShowAuthModal(null)}
              className="absolute top-4 right-4 text-slate-400 hover:text-slate-600 text-sm font-semibold cursor-pointer"
            >
              ✕
            </button>

            <h3 className="text-xl font-bold text-slate-900 mb-1">
              {showAuthModal === 'ORG' && 'Register Your Organisation'}
              {showAuthModal === 'BENEFICIARY' && 'Join as a Participant'}
              {showAuthModal === 'LOGIN' && 'Sign In to Voice of a Girl'}
            </h3>
            <p className="text-xs text-slate-500 mb-5">
              {showAuthModal === 'ORG' && 'Manage programmes, deploy surveys, and generate impact reports.'}
              {showAuthModal === 'BENEFICIARY' && 'Access scholarship opportunities and complete surveys.'}
              {showAuthModal === 'LOGIN' && 'Enter your registered email address to access your dashboard.'}
            </p>

            <form onSubmit={handleAuthSubmit} className="space-y-3.5">
              {showAuthModal === 'ORG' && (
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Organisation Name</label>
                  <input
                    type="text"
                    required
                    value={authOrgName}
                    onChange={(e) => setAuthOrgName(e.target.value)}
                    placeholder="e.g. Hope Empowerment Foundation"
                    className="w-full px-3 py-2 text-xs border border-slate-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                  />
                </div>
              )}

              {showAuthModal !== 'LOGIN' && (
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">First Name</label>
                    <input
                      type="text"
                      required
                      value={authFirstName}
                      onChange={(e) => setAuthFirstName(e.target.value)}
                      placeholder="Jane"
                      className="w-full px-3 py-2 text-xs border border-slate-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">Last Name</label>
                    <input
                      type="text"
                      required
                      value={authLastName}
                      onChange={(e) => setAuthLastName(e.target.value)}
                      placeholder="Doe"
                      className="w-full px-3 py-2 text-xs border border-slate-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                    />
                  </div>
                </div>
              )}

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Email Address</label>
                <input
                  type="email"
                  required
                  value={authEmail}
                  onChange={(e) => setAuthEmail(e.target.value)}
                  placeholder="name@example.org"
                  className="w-full px-3 py-2 text-xs border border-slate-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                />
              </div>

              <div className="pt-2">
                <button
                  type="submit"
                  className="w-full py-2.5 rounded-md bg-slate-900 hover:bg-slate-800 text-white font-medium text-xs shadow-sm transition-colors cursor-pointer"
                >
                  {showAuthModal === 'LOGIN' ? 'Sign In Now' : 'Create Account & Enter'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Footer */}
      <footer className="py-8 bg-white text-slate-500 text-xs border-t border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div>
            <span className="font-semibold text-slate-900">VOICE OF A GIRL</span> — Beneficiary Management & Outcome Measurement SaaS.
          </div>
          <div className="flex items-center gap-4">
            <span>Built with Django REST Architecture & React</span>
            <span>•</span>
            <button onClick={() => selectPersonaAndGo('ORGANISATION_ADMIN')} className="hover:text-slate-900 underline cursor-pointer">
              Launch App
            </button>
          </div>
        </div>
      </footer>
    </div>
  );
};
