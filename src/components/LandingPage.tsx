import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';
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
  , MapPin
  , Phone
  , Menu
} from 'lucide-react';

interface LandingPageProps {
  onEnterApp: () => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({ onEnterApp }) => {
  const { login } = useAuth();
  const [showAuthModal, setShowAuthModal] = useState<null | 'INTEREST' | 'LOGIN'>(null);
  const [authEmail, setAuthEmail] = useState('');
  const [authFirstName, setAuthFirstName] = useState('');
  const [authLastName, setAuthLastName] = useState('');
  const [authPhone, setAuthPhone] = useState('');
  const [authDistrict, setAuthDistrict] = useState('Kampala');
  const [authEducation, setAuthEducation] = useState('HIGH_SCHOOL');
  const [authInterest, setAuthInterest] = useState('Technology and digital skills');
  const [formMessage, setFormMessage] = useState<string | null>(null);
  const [formError, setFormError] = useState<string | null>(null);

  const handleAuthSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);
    setFormMessage(null);
    if (showAuthModal === 'LOGIN') {
      if (await login(authEmail, '')) {
        setShowAuthModal(null);
        onEnterApp();
      } else {
        setFormError('We could not find an authorised workspace for that email. Please contact the Voice of a Girl team.');
      }
      return;
    }

    try {
      await api.submitBeneficiaryInterest({
        first_name: authFirstName,
        last_name: authLastName,
        email: authEmail,
        phone_number: authPhone,
        district: authDistrict,
        education_level: authEducation,
        interest_area: authInterest
      });
      setFormMessage('Thank you. Your information has been securely sent to our programme team for review.');
      setAuthFirstName('');
      setAuthLastName('');
      setAuthEmail('');
      setAuthPhone('');
    } catch (error) {
      setFormError('We could not submit your information right now. Please check your connection and try again.');
    }
  };

  return (
    <div className="min-h-screen bg-[#F9FAFB] text-slate-900 flex flex-col justify-between" id="landing-page">
      <header className="public-nav">
        <div className="public-nav__inner">
          <button className="public-brand" onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })} aria-label="Voice of a Girl home">
            <span className="public-brand__mark">VG</span>
            <span>
              <strong>Voice of a Girl</strong>
              <small>Opportunity, measured.</small>
            </span>
          </button>
          <nav className="public-nav__links" aria-label="Public navigation">
            <a href="#how-it-works">How it works</a>
            <a href="#for-organisations">For organisations</a>
            <button onClick={() => setShowAuthModal('LOGIN')}>Team sign in <ArrowRight className="h-3.5 w-3.5" /></button>
          </nav>
          <button className="public-nav__menu" onClick={() => setShowAuthModal('LOGIN')} aria-label="Open team sign in">
            <Menu className="h-5 w-5" />
          </button>
        </div>
      </header>
      {/* Hero Section */}
      <section className="relative overflow-hidden pt-16 pb-20 lg:pt-24 lg:pb-28 bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="text-center max-w-4xl mx-auto">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-md text-xs font-semibold bg-indigo-50 text-indigo-700 border border-indigo-100 mb-6">
              <Sparkles className="w-3.5 h-3.5" />
              B2B SaaS for Beneficiary Management & Outcome Measurement
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-[1.05fr_0.95fr] items-center gap-10 text-left">
              <div>
                <h1 className="text-4xl sm:text-5xl lg:text-6xl font-black text-slate-900 tracking-tight leading-[1.08]">
                  A clearer path to <span className="text-indigo-600">her next opportunity.</span>
                </h1>
                <p className="mt-6 text-base sm:text-lg text-slate-500 max-w-2xl leading-relaxed">
                  Voice of a Girl helps our team connect young women with meaningful programmes while giving partners one trusted place to manage delivery and prove impact.
                </p>
              </div>
              <div className="relative overflow-hidden rounded-2xl border border-slate-200 bg-slate-100 shadow-xl">
                <img
                  src="https://images.unsplash.com/photo-1529156069898-49953e39b3ac?auto=format&fit=crop&w=1200&q=85"
                  alt="Young women learning together"
                  className="h-72 w-full object-cover sm:h-80"
                />
                <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-slate-950/75 to-transparent p-5 pt-16 text-white">
                  <p className="text-sm font-semibold">Opportunities begin with being heard.</p>
                  <p className="mt-1 text-xs text-white/80">Submit your details and our team will help you find the right fit.</p>
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="mt-8 flex flex-wrap items-center justify-center gap-3 sm:gap-4">
              <button
                onClick={() => setShowAuthModal('LOGIN')}
                className="px-5 py-2.5 rounded-md bg-slate-900 hover:bg-slate-800 text-white font-medium text-sm shadow-sm transition-colors cursor-pointer flex items-center gap-2"
                id="btn-organisation-login"
              >
                <Building2 className="w-4 h-4" />
                Organisation sign in
              </button>

              <button
                onClick={() => setShowAuthModal('INTEREST')}
                className="px-5 py-2.5 rounded-md bg-white hover:bg-slate-50 text-slate-700 font-medium text-sm border border-slate-200 shadow-xs transition-colors cursor-pointer flex items-center gap-2"
                id="btn-join-participant"
              >
                <GraduationCap className="w-4 h-4" />
                Find your opportunity
              </button>

              <button
                onClick={() => setShowAuthModal('LOGIN')}
                className="px-5 py-2.5 rounded-md bg-slate-100 hover:bg-slate-200 text-slate-800 font-medium text-sm transition-colors cursor-pointer"
                id="btn-login"
              >
                Sign In
              </button>
            </div>

            {/* Public intake promise */}
            <div className="mt-12 pt-8 border-t border-slate-100 max-w-3xl mx-auto">
              <div className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-3">
                A simple, supported journey
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-left">
                {['Tell us about yourself', 'Our team reviews your fit', 'We connect you to the right programme'].map((step, index) => (
                  <div key={step} className="flex gap-3 rounded-lg bg-slate-50 border border-slate-200 p-3">
                    <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-indigo-600 text-xs font-bold text-white">{index + 1}</span>
                    <span className="text-xs font-semibold text-slate-700">{step}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Core Value Chain Section */}
      <section className="py-16 bg-slate-900 text-white" id="how-it-works">
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
      <section className="py-16 bg-white" id="for-organisations">
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

      {/* Public intake and controlled sign-in */}
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
              {showAuthModal === 'INTEREST' && 'Tell us where you want to go'}
              {showAuthModal === 'LOGIN' && 'Sign In to Voice of a Girl'}
            </h3>
            <p className="text-xs text-slate-500 mb-5">
              {showAuthModal === 'INTEREST' && 'Share a few details. Our programme team will review your information and contact you about a suitable opportunity.'}
              {showAuthModal === 'LOGIN' && 'This sign-in is for authorised organisation, field, and platform team members.'}
            </p>

            {formMessage && <div className="mb-4 rounded-lg border border-emerald-200 bg-emerald-50 p-3 text-xs font-medium text-emerald-800"><CheckCircle2 className="mr-1 inline h-4 w-4" />{formMessage}</div>}
            {formError && <div className="mb-4 rounded-lg border border-rose-200 bg-rose-50 p-3 text-xs font-medium text-rose-800">{formError}</div>}

            <form onSubmit={handleAuthSubmit} className="space-y-3.5">
              {showAuthModal === 'INTEREST' && (
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

              {showAuthModal === 'INTEREST' && (
                <>
                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <label className="block text-xs font-semibold text-slate-700 mb-1"><Phone className="mr-1 inline h-3.5 w-3.5" />Phone number</label>
                      <input type="tel" required value={authPhone} onChange={(e) => setAuthPhone(e.target.value)} placeholder="+256 700 000000" className="w-full px-3 py-2 text-xs border border-slate-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none" />
                    </div>
                    <div>
                      <label className="block text-xs font-semibold text-slate-700 mb-1"><MapPin className="mr-1 inline h-3.5 w-3.5" />District</label>
                      <input type="text" required value={authDistrict} onChange={(e) => setAuthDistrict(e.target.value)} placeholder="Kampala" className="w-full px-3 py-2 text-xs border border-slate-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none" />
                    </div>
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">Highest education level</label>
                    <select value={authEducation} onChange={(e) => setAuthEducation(e.target.value)} className="w-full px-3 py-2 text-xs border border-slate-200 rounded-lg bg-white focus:ring-2 focus:ring-indigo-500 focus:outline-none">
                      <option value="PRIMARY">Primary</option>
                      <option value="SECONDARY">Secondary</option>
                      <option value="HIGH_SCHOOL">High school</option>
                      <option value="VOCATIONAL">Vocational certificate</option>
                      <option value="UNDERGRADUATE">Undergraduate degree</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">What are you interested in?</label>
                    <select value={authInterest} onChange={(e) => setAuthInterest(e.target.value)} className="w-full px-3 py-2 text-xs border border-slate-200 rounded-lg bg-white focus:ring-2 focus:ring-indigo-500 focus:outline-none">
                      <option>Technology and digital skills</option>
                      <option>Entrepreneurship and business</option>
                      <option>Scholarships and education</option>
                      <option>Leadership and mentorship</option>
                      <option>Creative and vocational skills</option>
                    </select>
                  </div>
                </>
              )}

              <div className="pt-2">
                <button
                  type="submit"
                  className="w-full py-2.5 rounded-md bg-slate-900 hover:bg-slate-800 text-white font-medium text-xs shadow-sm transition-colors cursor-pointer"
                >
                  {showAuthModal === 'LOGIN' ? 'Sign in securely' : 'Submit my information'}
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
            <button onClick={() => setShowAuthModal('LOGIN')} className="hover:text-slate-900 underline cursor-pointer">
              Team sign in
            </button>
          </div>
        </div>
      </footer>
    </div>
  );
};
