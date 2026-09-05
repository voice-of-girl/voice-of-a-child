import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { 
  Form, 
  Opportunity, 
  Challenge, 
  Programme, 
  ChallengeCategory, 
  ChallengeSeverity 
} from '../../types';
import { api } from '../../services/api';
import { 
  GraduationCap, 
  FileCheck2, 
  AlertTriangle, 
  Briefcase, 
  Sparkles, 
  CheckCircle2, 
  Clock, 
  Send, 
  MapPin, 
  BookOpen, 
  Award,
  ChevronRight,
  ArrowRight,
  User,
  Star
} from 'lucide-react';

export const BeneficiaryDashboard: React.FC = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState<'PROGRAMMES' | 'FORMS' | 'CHALLENGES' | 'OPPORTUNITIES' | 'PROFILE'>('PROGRAMMES');
  
  // State
  const [forms, setForms] = useState<Form[]>([]);
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [challenges, setChallenges] = useState<Challenge[]>([]);
  const [activeFormModal, setActiveFormModal] = useState<Form | null>(null);
  const [formAnswers, setFormAnswers] = useState<Record<string, any>>({});
  const [submittingForm, setSubmittingForm] = useState(false);
  const [formSuccessMessage, setFormSuccessMessage] = useState<string | null>(null);

  // Challenge modal state
  const [showChallengeModal, setShowChallengeModal] = useState(false);
  const [challengeCategory, setChallengeCategory] = useState<ChallengeCategory>('TRANSPORT');
  const [challengeSeverity, setChallengeSeverity] = useState<ChallengeSeverity>('MEDIUM');
  const [challengeDesc, setChallengeDesc] = useState('');
  const [challengeSubmitted, setChallengeSubmitted] = useState<string | null>(null);

  // Profile state
  const [skills, setSkills] = useState('Python, Web Design, Problem Solving');
  const [interests, setInterests] = useState('Technology, Software, AI Engineering, Social Impact');
  const [education, setEducation] = useState('HIGH_SCHOOL');
  const [district, setDistrict] = useState('Kampala');
  const [profileSaved, setProfileSaved] = useState(false);

  // Load initial beneficiary data
  useEffect(() => {
    const fetchData = async () => {
      try {
        const [fms, opps, chs] = await Promise.all([
          api.getForms('prog_1'),
          api.getOpportunities(),
          api.getChallenges('prog_1')
        ]);
        setForms(fms);
        setOpportunities(opps);
        // Filter challenges reported by this beneficiary
        setChallenges(chs.filter(c => c.beneficiary_id === 'usr_beneficiary'));
      } catch (e) {
        console.error(e);
      }
    };
    fetchData();
  }, []);

  const openFormToAnswer = (f: Form) => {
    setActiveFormModal(f);
    setFormAnswers({});
    setFormSuccessMessage(null);
  };

  const handleAnswerChange = (questionId: string, val: any) => {
    setFormAnswers(prev => ({ ...prev, [questionId]: val }));
  };

  const handleFormSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeFormModal) return;
    setSubmittingForm(true);

    try {
      await api.submitFormResponse(activeFormModal.id, {
        beneficiary_id: user?.id || 'usr_beneficiary',
        beneficiary_name: `${user?.first_name || 'Fatima'} ${user?.last_name || 'Zara'}`,
        answers: formAnswers
      });
      setFormSuccessMessage('Your survey responses have been securely submitted to programme officers!');
      setTimeout(() => {
        setActiveFormModal(null);
        setFormSuccessMessage(null);
      }, 2000);
    } catch (e) {
      console.error(e);
    } finally {
      setSubmittingForm(false);
    }
  };

  const handleReportChallenge = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const newCh = await api.reportChallenge('prog_1', {
        beneficiary_id: user?.id || 'usr_beneficiary',
        beneficiary_name: `${user?.first_name || 'Fatima'} ${user?.last_name || 'Zara'}`,
        category: challengeCategory,
        severity: challengeSeverity,
        description: challengeDesc
      });
      setChallenges([newCh, ...challenges]);
      setShowChallengeModal(false);
      setChallengeDesc('');
      setChallengeSubmitted('Your challenge alert has been logged! A field officer will follow up.');
      setTimeout(() => setChallengeSubmitted(null), 4000);
    } catch (e) {
      console.error(e);
    }
  };

  const handleApplyOpportunity = async (opp: Opportunity) => {
    try {
      await api.applyForOpportunity({
        opportunity_id: opp.id,
        beneficiary_id: user?.id || 'usr_beneficiary',
        status: 'SUBMITTED'
      });
      alert(`Successfully applied for: ${opp.title}! The organisation will review your rule-based score.`);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6" id="beneficiary-dashboard">
      {/* Participant Profile Banner */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-slate-100 border border-slate-200 flex items-center justify-center font-bold text-lg text-slate-800 shadow-xs">
            {user?.first_name?.[0] || 'F'}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold text-slate-900">
                {user?.first_name} {user?.last_name}
              </h1>
              <span className="px-2.5 py-0.5 rounded-md text-[10px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                Active Scholar
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-0.5 flex items-center gap-3">
              <span>{user?.email}</span>
              <span>•</span>
              <span className="flex items-center gap-1">
                <MapPin className="w-3.5 h-3.5 text-slate-400" />
                {district}, Uganda
              </span>
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowChallengeModal(true)}
            className="px-3.5 py-2 rounded-md bg-slate-900 hover:bg-slate-800 text-white text-xs font-medium transition-colors flex items-center gap-1.5 shadow-sm cursor-pointer"
            id="btn-beneficiary-report-challenge"
          >
            <AlertTriangle className="w-3.5 h-3.5" />
            Report a Barrier / Challenge
          </button>
        </div>
      </div>

      {challengeSubmitted && (
        <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-xl text-emerald-900 text-xs font-medium flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-600" />
          {challengeSubmitted}
        </div>
      )}

      {/* Tabs */}
      <div className="border-b border-slate-200 overflow-x-auto">
        <nav className="flex space-x-2 py-1" aria-label="Beneficiary Tabs">
          <button
            onClick={() => setActiveTab('PROGRAMMES')}
            className={`px-3.5 py-2 rounded-md text-xs font-medium transition-colors flex items-center gap-2 cursor-pointer ${
              activeTab === 'PROGRAMMES' ? 'bg-slate-900 text-white shadow-xs' : 'text-slate-500 hover:text-slate-900 hover:bg-slate-100'
            }`}
          >
            <BookOpen className="w-4 h-4" />
            <span>My Enrolled Programme</span>
          </button>

          <button
            onClick={() => setActiveTab('FORMS')}
            className={`px-3.5 py-2 rounded-md text-xs font-medium transition-colors flex items-center gap-2 cursor-pointer ${
              activeTab === 'FORMS' ? 'bg-slate-900 text-white shadow-xs' : 'text-slate-500 hover:text-slate-900 hover:bg-slate-100'
            }`}
          >
            <FileCheck2 className="w-4 h-4" />
            <span>Surveys & Intake ({forms.length})</span>
          </button>

          <button
            onClick={() => setActiveTab('CHALLENGES')}
            className={`px-3.5 py-2 rounded-md text-xs font-medium transition-colors flex items-center gap-2 cursor-pointer ${
              activeTab === 'CHALLENGES' ? 'bg-slate-900 text-white shadow-xs' : 'text-slate-500 hover:text-slate-900 hover:bg-slate-100'
            }`}
          >
            <AlertTriangle className="w-4 h-4" />
            <span>My Reported Challenges ({challenges.length})</span>
          </button>

          <button
            onClick={() => setActiveTab('OPPORTUNITIES')}
            className={`px-3.5 py-2 rounded-md text-xs font-medium transition-colors flex items-center gap-2 cursor-pointer ${
              activeTab === 'OPPORTUNITIES' ? 'bg-slate-900 text-white shadow-xs' : 'text-slate-500 hover:text-slate-900 hover:bg-slate-100'
            }`}
          >
            <Briefcase className="w-4 h-4" />
            <span>Matched Opportunities ({opportunities.length})</span>
          </button>

          <button
            onClick={() => setActiveTab('PROFILE')}
            className={`px-3.5 py-2 rounded-md text-xs font-medium transition-colors flex items-center gap-2 cursor-pointer ${
              activeTab === 'PROFILE' ? 'bg-slate-900 text-white shadow-xs' : 'text-slate-500 hover:text-slate-900 hover:bg-slate-100'
            }`}
          >
            <User className="w-4 h-4" />
            <span>My Profile & Skills</span>
          </button>
        </nav>
      </div>

      {/* Tab 1: Enrolled Programme */}
      {activeTab === 'PROGRAMMES' && (
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-slate-100">
            <div>
              <span className="text-[10px] font-semibold px-2.5 py-0.5 rounded-md bg-indigo-50 text-indigo-700 border border-indigo-200 uppercase">
                Enrolled Cohort
              </span>
              <h2 className="text-xl font-bold text-slate-900 mt-2">
                Girls in Tech & AI Leadership Cohort 2026
              </h2>
              <p className="text-xs text-slate-500 mt-0.5">
                Organised by FemmeTech Africa Foundation • Kampala, Uganda
              </p>
            </div>

            <div className="flex items-center gap-4">
              <div className="text-right">
                <span className="text-[10px] uppercase font-semibold text-slate-400">My Attendance</span>
                <div className="text-xl font-bold text-emerald-700">96%</div>
              </div>
              <div className="text-right">
                <span className="text-[10px] uppercase font-semibold text-slate-400">Match Score</span>
                <div className="text-xl font-bold text-indigo-700">95%</div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
              <span className="font-semibold text-slate-900 block mb-1">Status: Active Participant</span>
              <p className="text-slate-600 leading-relaxed">
                You have satisfied the intake baseline requirements and are actively completing weekly modules.
              </p>
            </div>

            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
              <span className="font-semibold text-slate-900 block mb-1">Assigned Field Officer</span>
              <p className="text-slate-600 leading-relaxed">
                Sarah Kibuuka (Central Region). Available for verification check-ins and learning support.
              </p>
            </div>

            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
              <span className="font-semibold text-slate-900 block mb-1">Upcoming Milestone</span>
              <p className="text-slate-600 leading-relaxed">
                Midline Project Showcase & Endline Career Matchmaking on June 15, 2026.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Tab 2: Forms & Surveys to Complete */}
      {activeTab === 'FORMS' && (
        <div className="space-y-4">
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
            <h2 className="text-lg font-bold text-slate-900">Custom Forms & Surveys to Complete</h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Submit your answers to help programme managers monitor training effectiveness and track outcomes.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {forms.map((f) => (
              <div key={f.id} className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[10px] font-semibold px-2 py-0.5 rounded-md bg-indigo-50 text-indigo-700 border border-indigo-100 uppercase">
                      {f.form_type}
                    </span>
                    <span className="text-xs text-slate-400 font-medium">
                      {f.questions?.length || 0} Questions
                    </span>
                  </div>
                  <h3 className="font-bold text-slate-900 text-base">{f.title}</h3>
                  <p className="text-xs text-slate-600 mt-1 line-clamp-2">{f.description}</p>
                </div>

                <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between">
                  <span className="text-[11px] text-slate-400">Estimated: 3-5 mins</span>
                  <button
                    onClick={() => openFormToAnswer(f)}
                    className="px-3.5 py-1.5 rounded-md bg-slate-900 hover:bg-slate-800 text-white text-xs font-medium transition-colors flex items-center gap-1 cursor-pointer shadow-xs"
                  >
                    <span>Fill & Submit</span>
                    <ChevronRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab 3: Reported Challenges */}
      {activeTab === 'CHALLENGES' && (
        <div className="space-y-4">
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex items-center justify-between">
            <div>
              <h2 className="text-lg font-bold text-slate-900">My Logged Challenges</h2>
              <p className="text-xs text-slate-500">Track issues reported to programme leadership and field responders.</p>
            </div>
            <button
              onClick={() => setShowChallengeModal(true)}
              className="px-3.5 py-2 bg-slate-900 hover:bg-slate-800 text-white text-xs font-medium rounded-md transition-colors cursor-pointer shadow-sm"
            >
              Report New Challenge
            </button>
          </div>

          {challenges.length === 0 ? (
            <div className="bg-white p-8 rounded-xl border border-slate-200 text-center text-xs text-slate-500 shadow-sm">
              You have no active challenges reported. If you encounter barriers with transport, materials, or attendance, click the button above!
            </div>
          ) : (
            <div className="space-y-3">
              {challenges.map((c) => (
                <div key={c.id} className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm text-xs space-y-2">
                  <div className="flex items-center justify-between font-bold">
                    <span className="text-slate-900">{c.category} Barrier</span>
                    <span className={`px-2.5 py-0.5 rounded-md text-[10px] font-semibold ${
                      c.status === 'RESOLVED' ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-amber-50 text-amber-700 border border-amber-200'
                    }`}>
                      {c.status}
                    </span>
                  </div>
                  <p className="text-slate-600">{c.description}</p>
                  {c.resolution_notes && (
                    <div className="p-3 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-900">
                      <strong>Response Team Note:</strong> {c.resolution_notes}
                    </div>
                  )}
                  <div className="text-[10px] text-slate-400">
                    Logged on {new Date(c.reported_at).toLocaleDateString()} • Assigned to: {c.assigned_to_name || 'Pending assignment'}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Tab 4: Matched Opportunities */}
      {activeTab === 'OPPORTUNITIES' && (
        <div className="space-y-4">
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
            <h2 className="text-lg font-bold text-slate-900">Opportunities & Matching Engine</h2>
            <p className="text-xs text-slate-500">
              Scholarships, internships, and grants transparently matched against your profile.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {opportunities.map((opp) => (
              <div key={opp.id} className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm flex flex-col justify-between">
                <div>
                  <div className="flex items-start justify-between gap-2 mb-2">
                    <span className="text-[10px] font-semibold px-2 py-0.5 rounded-md bg-indigo-50 text-indigo-700 border border-indigo-100 uppercase">
                      {opp.opportunity_type}
                    </span>
                    <span className="text-xs font-semibold text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded-md border border-indigo-100 flex items-center gap-1">
                      <Sparkles className="w-3 h-3" />
                      95% Match
                    </span>
                  </div>

                  <h3 className="font-bold text-slate-900 text-base">{opp.title}</h3>
                  <div className="text-xs text-slate-500 font-medium mt-0.5">{opp.organisation_name}</div>
                  <p className="text-xs text-slate-600 mt-2 line-clamp-3">{opp.description}</p>

                  <div className="mt-3 text-xs text-slate-500 space-y-1">
                    <div>📍 Location: {opp.location}</div>
                    <div>📅 Deadline: {opp.deadline ? new Date(opp.deadline).toLocaleDateString() : 'Rolling'}</div>
                  </div>
                </div>

                <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between">
                  <span className="text-[11px] text-slate-500">Criteria Met</span>
                  <button
                    onClick={() => handleApplyOpportunity(opp)}
                    className="px-3.5 py-1.5 bg-slate-900 hover:bg-slate-800 text-white rounded-md text-xs font-medium transition-colors flex items-center gap-1 cursor-pointer shadow-sm"
                  >
                    <span>1-Click Apply</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab 5: Profile & Skills Editor */}
      {activeTab === 'PROFILE' && (
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm max-w-2xl mx-auto space-y-4">
          <h2 className="text-lg font-bold text-slate-900">Participant Profile & Matching Credentials</h2>
          <p className="text-xs text-slate-500">
            Keep your skills and interests up-to-date so our rule-based matching engine pairs you with suitable programmes.
          </p>

          {profileSaved && (
            <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-semibold rounded-lg">
              Profile successfully saved!
            </div>
          )}

          <div className="space-y-3.5 text-xs">
            <div>
              <label className="block font-semibold text-slate-700 mb-1">Education Level</label>
              <select
                value={education}
                onChange={(e) => setEducation(e.target.value)}
                className="w-full p-2.5 border border-slate-200 rounded-lg bg-white focus:ring-2 focus:ring-indigo-500 focus:outline-none"
              >
                <option value="PRIMARY">Primary</option>
                <option value="SECONDARY">Secondary</option>
                <option value="HIGH_SCHOOL">High School</option>
                <option value="VOCATIONAL">Vocational Certificate</option>
                <option value="UNDERGRADUATE">Undergraduate Degree</option>
              </select>
            </div>

            <div>
              <label className="block font-semibold text-slate-700 mb-1">Home District</label>
              <input
                type="text"
                value={district}
                onChange={(e) => setDistrict(e.target.value)}
                className="w-full p-2.5 border border-slate-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="block font-semibold text-slate-700 mb-1">Key Skills (comma separated)</label>
              <input
                type="text"
                value={skills}
                onChange={(e) => setSkills(e.target.value)}
                className="w-full p-2.5 border border-slate-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="block font-semibold text-slate-700 mb-1">Career Interests (comma separated)</label>
              <input
                type="text"
                value={interests}
                onChange={(e) => setInterests(e.target.value)}
                className="w-full p-2.5 border border-slate-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none"
              />
            </div>

            <div className="pt-2">
              <button
                onClick={() => {
                  setProfileSaved(true);
                  setTimeout(() => setProfileSaved(false), 3000);
                }}
                className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white font-medium rounded-md text-xs transition-colors cursor-pointer shadow-sm"
              >
                Save Profile Updates
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Interactive Form Answering Modal (Google Forms Experience) */}
      {activeFormModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/50 p-4 backdrop-blur-xs">
          <div className="bg-white rounded-xl max-w-xl w-full p-6 shadow-xl border border-slate-200 max-h-[90vh] overflow-y-auto relative">
            <button
              onClick={() => setActiveFormModal(null)}
              className="absolute top-4 right-4 text-slate-400 hover:text-slate-600 font-bold p-1 cursor-pointer"
            >
              ✕
            </button>

            <div className="border-b border-slate-100 pb-3 mb-4">
              <span className="text-[10px] font-semibold text-indigo-700 uppercase bg-indigo-50 px-2.5 py-0.5 rounded-md border border-indigo-100">
                {activeFormModal.form_type}
              </span>
              <h3 className="text-xl font-bold text-slate-900 mt-2">{activeFormModal.title}</h3>
              <p className="text-xs text-slate-500 mt-1">{activeFormModal.description}</p>
            </div>

            {formSuccessMessage ? (
              <div className="py-12 text-center space-y-3">
                <CheckCircle2 className="w-12 h-12 text-emerald-600 mx-auto" />
                <h4 className="font-bold text-slate-900 text-base">Thank You!</h4>
                <p className="text-xs text-slate-600">{formSuccessMessage}</p>
              </div>
            ) : (
              <form onSubmit={handleFormSubmit} className="space-y-4 text-xs">
                {(activeFormModal.questions || []).map((q, idx) => (
                  <div key={q.id || idx} className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-2">
                    <div className="font-semibold text-slate-800 flex items-start gap-1">
                      <span>{idx + 1}. {q.question_text}</span>
                      {q.required && <span className="text-rose-500 font-bold">*</span>}
                    </div>

                    {/* Question Input rendering */}
                    {q.question_type === 'SHORT_TEXT' && (
                      <input
                        type="text"
                        required={q.required}
                        value={formAnswers[q.id] || ''}
                        onChange={(e) => handleAnswerChange(q.id, e.target.value)}
                        placeholder="Your short answer"
                        className="w-full p-2.5 border border-slate-200 rounded-lg bg-white focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                      />
                    )}

                    {q.question_type === 'LONG_TEXT' && (
                      <textarea
                        rows={3}
                        required={q.required}
                        value={formAnswers[q.id] || ''}
                        onChange={(e) => handleAnswerChange(q.id, e.target.value)}
                        placeholder="Type your detailed answer here..."
                        className="w-full p-2.5 border border-slate-200 rounded-lg bg-white focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                      />
                    )}

                    {q.question_type === 'NUMBER' && (
                      <input
                        type="number"
                        required={q.required}
                        value={formAnswers[q.id] || ''}
                        onChange={(e) => handleAnswerChange(q.id, e.target.value)}
                        placeholder="Enter number..."
                        className="w-full p-2.5 border border-slate-200 rounded-lg bg-white focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                      />
                    )}

                    {q.question_type === 'YES_NO' && (
                      <div className="flex items-center gap-4 pt-1">
                        <label className="flex items-center gap-1.5 cursor-pointer">
                          <input
                            type="radio"
                            name={q.id}
                            value="Yes"
                            checked={formAnswers[q.id] === 'Yes'}
                            onChange={(e) => handleAnswerChange(q.id, e.target.value)}
                          />
                          <span>Yes</span>
                        </label>
                        <label className="flex items-center gap-1.5 cursor-pointer">
                          <input
                            type="radio"
                            name={q.id}
                            value="No"
                            checked={formAnswers[q.id] === 'No'}
                            onChange={(e) => handleAnswerChange(q.id, e.target.value)}
                          />
                          <span>No</span>
                        </label>
                      </div>
                    )}

                    {q.question_type === 'MULTIPLE_CHOICE' && (
                      <div className="space-y-1.5 pt-1">
                        {(q.options || []).map((opt, oIdx) => (
                          <label key={oIdx} className="flex items-center gap-2 cursor-pointer">
                            <input
                              type="radio"
                              name={q.id}
                              value={opt}
                              checked={formAnswers[q.id] === opt}
                              onChange={(e) => handleAnswerChange(q.id, opt)}
                            />
                            <span>{opt}</span>
                          </label>
                        ))}
                      </div>
                    )}

                    {q.question_type === 'CHECKBOX' && (
                      <div className="space-y-1.5 pt-1">
                        {(q.options || []).map((opt, oIdx) => {
                          const currentArr = formAnswers[q.id] || [];
                          const checked = currentArr.includes(opt);
                          return (
                            <label key={oIdx} className="flex items-center gap-2 cursor-pointer">
                              <input
                                type="checkbox"
                                checked={checked}
                                onChange={(e) => {
                                  if (e.target.checked) {
                                    handleAnswerChange(q.id, [...currentArr, opt]);
                                  } else {
                                    handleAnswerChange(q.id, currentArr.filter((x: string) => x !== opt));
                                  }
                                }}
                              />
                              <span>{opt}</span>
                            </label>
                          );
                        })}
                      </div>
                    )}

                    {q.question_type === 'RATING_SCALE' && (
                      <div className="flex items-center gap-2 pt-1 overflow-x-auto py-1">
                        {[1, 2, 3, 4, 5].map((starVal) => (
                          <button
                            type="button"
                            key={starVal}
                            onClick={() => handleAnswerChange(q.id, starVal)}
                            className={`w-9 h-9 rounded-md font-semibold border transition-colors cursor-pointer ${
                              formAnswers[q.id] === starVal
                                ? 'bg-slate-900 text-white border-slate-900'
                                : 'bg-white border-slate-200 text-slate-700 hover:bg-slate-100'
                            }`}
                          >
                            {starVal}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                ))}

                <div className="pt-2 flex items-center justify-end gap-2">
                  <button
                    type="button"
                    onClick={() => setActiveFormModal(null)}
                    className="px-4 py-2 text-slate-600 hover:bg-slate-100 rounded-md font-medium transition-colors cursor-pointer"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={submittingForm}
                    className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white font-medium rounded-md transition-colors shadow-sm flex items-center gap-1.5 cursor-pointer"
                  >
                    <Send className="w-3.5 h-3.5" />
                    <span>{submittingForm ? 'Submitting...' : 'Submit Answers'}</span>
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}

      {/* Report Challenge Modal */}
      {showChallengeModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/50 p-4 backdrop-blur-xs">
          <div className="bg-white rounded-xl max-w-md w-full p-6 shadow-xl border border-slate-200">
            <h3 className="text-lg font-bold text-slate-900 mb-1">Report a Challenge / Barrier</h3>
            <p className="text-xs text-slate-500 mb-4">
              Facing difficulties attending, commuting, or completing coursework? Let programme leaders know early so we can support you.
            </p>

            <form onSubmit={handleReportChallenge} className="space-y-3.5 text-xs">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Barrier Category</label>
                <select
                  value={challengeCategory}
                  onChange={(e) => setChallengeCategory(e.target.value as ChallengeCategory)}
                  className="w-full p-2.5 border border-slate-200 rounded-lg bg-white focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                >
                  <option value="TRANSPORT">Transport & Commute (e.g. minibus taxi fare increase)</option>
                  <option value="FINANCIAL">Financial / Living Stipend</option>
                  <option value="HEALTH">Health & Well-being</option>
                  <option value="ATTENDANCE">Attendance Conflict / Domestic responsibilities</option>
                  <option value="MATERIALS">Learning Materials / Broken Laptop Adapter</option>
                  <option value="SAFETY">Personal Safety & Commute Route</option>
                  <option value="OTHER">Other Challenge</option>
                </select>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Urgency / Severity</label>
                <select
                  value={challengeSeverity}
                  onChange={(e) => setChallengeSeverity(e.target.value as ChallengeSeverity)}
                  className="w-full p-2.5 border border-slate-200 rounded-lg bg-white focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                >
                  <option value="LOW">Low (Can still participate)</option>
                  <option value="MEDIUM">Medium (Risk of missing sessions)</option>
                  <option value="HIGH">High (Unable to attend current sessions)</option>
                  <option value="CRITICAL">Critical (Risk of dropping out immediately)</option>
                </select>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Describe what you are experiencing</label>
                <textarea
                  rows={3}
                  required
                  value={challengeDesc}
                  onChange={(e) => setChallengeDesc(e.target.value)}
                  placeholder="Please describe your situation in detail..."
                  className="w-full p-2.5 border border-slate-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                />
              </div>

              <div className="pt-2 flex items-center justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setShowChallengeModal(false)}
                  className="px-3.5 py-2 text-slate-600 hover:bg-slate-100 rounded-md font-medium transition-colors cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white font-medium rounded-md transition-colors shadow-sm cursor-pointer"
                >
                  Submit Barrier Report
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
