import React, { useState } from 'react';
import { BeneficiaryParticipation, ParticipationStatus } from '../../types';
import { api } from '../../services/api';
import { 
  Users, 
  Search, 
  Filter, 
  UserPlus, 
  CheckCircle2, 
  XCircle, 
  Sparkles, 
  AlertCircle, 
  Calculator, 
  Info,
  ArrowRight,
  Phone,
  Mail,
  MapPin,
  Clock
} from 'lucide-react';

interface OrgParticipantsProps {
  programmeId: string;
  participants: BeneficiaryParticipation[];
  onRefresh: () => void;
}

export const OrgParticipants: React.FC<OrgParticipantsProps> = ({ programmeId, participants, onRefresh }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState<string>('ALL');
  const [selectedParticipant, setSelectedParticipant] = useState<BeneficiaryParticipation | null>(null);
  const [showMatchTester, setShowMatchTester] = useState(false);
  const [enrollModal, setEnrollModal] = useState(false);

  // Match tester state
  const [testAge, setTestAge] = useState<number>(21);
  const [testDistrict, setTestDistrict] = useState('Kampala');
  const [testEducation, setTestEducation] = useState('HIGH_SCHOOL');
  const [testSkills, setTestSkills] = useState('Python, Data Entry');
  const [testInterests, setTestInterests] = useState('Technology, Software, AI');
  const [matchResult, setMatchResult] = useState<any>(null);
  const [isCalculating, setIsCalculating] = useState(false);

  // New Participant Enrollment Form
  const [newFirstName, setNewFirstName] = useState('');
  const [newLastName, setNewLastName] = useState('');
  const [newEmail, setNewEmail] = useState('');
  const [newPhone, setNewPhone] = useState('');
  const [newDistrict, setNewDistrict] = useState('Kampala');

  const filtered = participants.filter(p => {
    if (filterStatus !== 'ALL' && p.status !== filterStatus) return false;
    if (searchTerm.trim()) {
      const q = searchTerm.toLowerCase();
      const name = `${p.beneficiary?.first_name || ''} ${p.beneficiary?.last_name || ''}`.toLowerCase();
      return name.includes(q) || (p.beneficiary?.email || '').toLowerCase().includes(q);
    }
    return true;
  });

  const handleStatusChange = async (participationId: string, newStatus: ParticipationStatus) => {
    await api.updateParticipationStatus(participationId, { status: newStatus });
    onRefresh();
  };

  const runMatchCalculation = async () => {
    setIsCalculating(true);
    const profile = {
      age: testAge,
      district: testDistrict,
      education_level: testEducation,
      skills: testSkills.split(',').map(s => s.trim()).filter(Boolean),
      interests: testInterests.split(',').map(s => s.trim()).filter(Boolean)
    };

    const requirements = {
      min_age: 18,
      max_age: 25,
      allowed_districts: ['Kampala', 'Wakiso', 'Mukono'],
      min_education_level: 'HIGH_SCHOOL',
      preferred_interests: ['Technology', 'AI', 'Software'],
      required_skills: ['Python']
    };

    try {
      const result = await api.calculateMatch(profile, requirements);
      setMatchResult(result);
    } catch (e) {
      console.error(e);
    } finally {
      setIsCalculating(false);
    }
  };

  const handleEnrollSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await api.enrollParticipant(programmeId, {
      first_name: newFirstName,
      last_name: newLastName,
      email: newEmail,
      phone_number: newPhone,
      district: newDistrict,
      status: 'SELECTED'
    });
    setEnrollModal(false);
    setNewFirstName('');
    setNewLastName('');
    setNewEmail('');
    setNewPhone('');
    onRefresh();
  };

  const statusBadge = (s: ParticipationStatus) => {
    switch (s) {
      case 'SELECTED':
        return <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-blue-50 text-blue-700 border border-blue-200">Selected</span>;
      case 'ACTIVE':
        return <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">Active</span>;
      case 'COMPLETED':
        return <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-purple-50 text-purple-700 border border-purple-200">Completed</span>;
      case 'DROPPED_OUT':
        return <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-rose-50 text-rose-700 border border-rose-200">Dropped Out</span>;
    }
  };

  return (
    <div className="space-y-6" id="participants-view">
      {/* Top Banner: Rule-Based Matcher & Participant Counts */}
      <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-xs font-bold text-rose-700 uppercase tracking-wider mb-1">
            <Sparkles className="w-3.5 h-3.5 text-rose-600" />
            Beneficiary Management & Transparent Matching
          </div>
          <h2 className="text-xl font-bold text-slate-900">Enrolled Participants & Candidate Roster</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Every candidate evaluated with transparent rule-based match scores, attendance telemetry, and status transitions.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => { setShowMatchTester(true); runMatchCalculation(); }}
            className="px-3.5 py-2 rounded-lg border border-slate-300 hover:bg-slate-50 text-slate-700 text-xs font-bold transition flex items-center gap-1.5 cursor-pointer"
            id="btn-open-match-tester"
          >
            <Calculator className="w-4 h-4 text-rose-600" />
            Rule-Based Match Engine
          </button>
          <button
            onClick={() => setEnrollModal(true)}
            className="px-3.5 py-2 rounded-lg bg-rose-600 hover:bg-rose-700 text-white text-xs font-bold transition flex items-center gap-1.5 shadow-xs cursor-pointer"
            id="btn-enroll-participant"
          >
            <UserPlus className="w-4 h-4" />
            Add Participant
          </button>
        </div>
      </div>

      {/* Funnel Metrics Bar */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-2xs">
          <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">Total Enrolled</span>
          <div className="text-2xl font-black text-slate-900 mt-1">{participants.length}</div>
          <div className="text-[11px] text-slate-500 mt-0.5">Assigned to programme cohort</div>
        </div>
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-2xs">
          <span className="text-[11px] font-bold uppercase tracking-wider text-emerald-600">Active Attending</span>
          <div className="text-2xl font-black text-emerald-700 mt-1">
            {participants.filter(p => p.status === 'ACTIVE').length}
          </div>
          <div className="text-[11px] text-slate-500 mt-0.5">Regularly logging attendance</div>
        </div>
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-2xs">
          <span className="text-[11px] font-bold uppercase tracking-wider text-blue-600">Avg. Attendance</span>
          <div className="text-2xl font-black text-blue-700 mt-1">
            {participants.length ? Math.round(participants.reduce((acc, p) => acc + (p.attendance_rate || 0), 0) / participants.length) : 0}%
          </div>
          <div className="text-[11px] text-slate-500 mt-0.5">Across all learning modules</div>
        </div>
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-2xs">
          <span className="text-[11px] font-bold uppercase tracking-wider text-purple-600">Avg. Match Score</span>
          <div className="text-2xl font-black text-purple-700 mt-1">
            {participants.length ? Math.round(participants.reduce((acc, p) => acc + (p.match_score || 0), 0) / participants.length) : 0}%
          </div>
          <div className="text-[11px] text-slate-500 mt-0.5">Cohort criteria alignment</div>
        </div>
      </div>

      {/* Participants Table Container */}
      <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-2xs">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4 pb-3 border-b border-slate-100">
          <div className="flex items-center gap-2 flex-1 max-w-sm">
            <div className="relative w-full">
              <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-2.5" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search by participant name or email..."
                className="w-full pl-8 pr-3 py-1.5 text-xs border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-rose-500"
              />
            </div>
          </div>

          <div className="flex items-center gap-2">
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="text-xs border border-slate-300 rounded-lg px-2.5 py-1.5 bg-white text-slate-700"
            >
              <option value="ALL">All Statuses</option>
              <option value="SELECTED">Selected</option>
              <option value="ACTIVE">Active</option>
              <option value="COMPLETED">Completed</option>
              <option value="DROPPED_OUT">Dropped Out</option>
            </select>
          </div>
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-700">
            <thead className="bg-slate-50 text-slate-500 font-bold border-y border-slate-200">
              <tr>
                <th className="py-2.5 px-3">Beneficiary</th>
                <th className="py-2.5 px-3">Location</th>
                <th className="py-2.5 px-3">Status</th>
                <th className="py-2.5 px-3">Match Score</th>
                <th className="py-2.5 px-3">Attendance</th>
                <th className="py-2.5 px-3">Forms Done</th>
                <th className="py-2.5 px-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filtered.map((p) => {
                const b = p.beneficiary;
                return (
                  <tr key={p.id} className="hover:bg-slate-50/70 transition">
                    <td className="py-3 px-3">
                      <div className="font-bold text-slate-900">{b?.first_name} {b?.last_name}</div>
                      <div className="text-[11px] text-slate-500">{b?.email} • {b?.phone_number}</div>
                    </td>
                    <td className="py-3 px-3">
                      <div className="flex items-center gap-1 text-slate-700">
                        <MapPin className="w-3 h-3 text-slate-400" />
                        <span>{b?.district || 'Kampala'}, {b?.country || 'Uganda'}</span>
                      </div>
                    </td>
                    <td className="py-3 px-3 whitespace-nowrap">
                      {statusBadge(p.status)}
                    </td>
                    <td className="py-3 px-3 whitespace-nowrap">
                      <button
                        onClick={() => setSelectedParticipant(p)}
                        className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md font-bold text-xs bg-purple-50 text-purple-700 hover:bg-purple-100 transition cursor-pointer"
                        title="Click to view transparent matching explanation"
                      >
                        <Sparkles className="w-3 h-3 text-purple-600" />
                        <span>{p.match_score || 95}%</span>
                      </button>
                    </td>
                    <td className="py-3 px-3 whitespace-nowrap">
                      <div className="flex items-center gap-2">
                        <div className="w-16 bg-slate-100 rounded-full h-2 overflow-hidden">
                          <div
                            className="bg-emerald-500 h-2 rounded-full"
                            style={{ width: `${p.attendance_rate || 0}%` }}
                          />
                        </div>
                        <span className="font-semibold text-slate-800">{p.attendance_rate || 0}%</span>
                      </div>
                    </td>
                    <td className="py-3 px-3 whitespace-nowrap font-medium text-slate-600">
                      {p.completed_surveys_count || 0} forms
                    </td>
                    <td className="py-3 px-3 text-right whitespace-nowrap space-x-1">
                      <select
                        value={p.status}
                        onChange={(e) => handleStatusChange(p.id, e.target.value as ParticipationStatus)}
                        className="text-[11px] font-semibold border border-slate-300 rounded px-1.5 py-1 bg-white text-slate-700"
                      >
                        <option value="SELECTED">Set Selected</option>
                        <option value="ACTIVE">Set Active</option>
                        <option value="COMPLETED">Set Completed</option>
                        <option value="DROPPED_OUT">Set Dropped Out</option>
                      </select>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Transparent Match Score Details Modal */}
      {selectedParticipant && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/60 p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-xl border border-slate-200">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-purple-600">
                  Transparent Rule-Based Match Explanation
                </span>
                <h3 className="text-base font-bold text-slate-900">
                  {selectedParticipant.beneficiary?.first_name} {selectedParticipant.beneficiary?.last_name}
                </h3>
              </div>
              <button onClick={() => setSelectedParticipant(null)} className="text-slate-400 hover:text-slate-600 font-bold">✕</button>
            </div>

            <div className="space-y-4">
              <div className="p-4 rounded-xl bg-purple-50 border border-purple-200 flex items-center justify-between">
                <div>
                  <div className="text-xs text-purple-700 font-bold uppercase">Calculated Match Score</div>
                  <div className="text-3xl font-black text-purple-900 mt-0.5">{selectedParticipant.match_score}%</div>
                </div>
                <div className="text-right text-xs text-purple-800">
                  <div className="font-semibold">Evaluated Against:</div>
                  <div>Girls in Tech 2026 Criteria</div>
                </div>
              </div>

              <div>
                <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  Matching Reasons (Why this participant qualifies):
                </h4>
                <div className="space-y-1.5">
                  {(selectedParticipant.matching_reasons || [
                    "Age is 21, within target range (18-25)",
                    "Resident of Kampala district (priority area)",
                    "Education level High School meets minimum requirements",
                    "Demonstrated interest in Technology & Software"
                  ]).map((reason, i) => (
                    <div key={i} className="text-xs p-2 rounded-lg bg-slate-50 border border-slate-200 text-slate-700 flex items-start gap-2">
                      <span className="text-emerald-600 font-bold">✓</span>
                      <span>{reason}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                  <AlertCircle className="w-4 h-4 text-amber-500" />
                  Missing Requirements / Gaps:
                </h4>
                {(selectedParticipant.missing_requirements || []).length === 0 ? (
                  <div className="text-xs p-2 rounded-lg bg-emerald-50 text-emerald-800 font-medium">
                    No critical gaps. Candidate satisfies 100% of core criteria.
                  </div>
                ) : (
                  <div className="space-y-1.5">
                    {selectedParticipant.missing_requirements?.map((gap, i) => (
                      <div key={i} className="text-xs p-2 rounded-lg bg-amber-50 border border-amber-200 text-amber-900 flex items-start gap-2">
                        <span className="text-amber-600 font-bold">!</span>
                        <span>{gap}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Rule-Based Match Tester Modal */}
      {showMatchTester && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/60 p-4">
          <div className="bg-white rounded-2xl max-w-2xl w-full p-6 shadow-2xl max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
              <div>
                <div className="text-xs font-bold text-rose-600 uppercase tracking-wider">
                  Interactive Matching Engine Simulator
                </div>
                <h3 className="text-lg font-bold text-slate-900">
                  Transparent Rule-Based Eligibility Engine
                </h3>
              </div>
              <button onClick={() => setShowMatchTester(false)} className="text-slate-400 hover:text-slate-600 font-bold">✕</button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-5">
              <div className="space-y-3 bg-slate-50 p-4 rounded-xl border border-slate-200">
                <span className="text-xs font-bold text-slate-800 block">Candidate Parameters</span>
                <div>
                  <label className="block text-[11px] font-semibold text-slate-600 mb-1">Age</label>
                  <input
                    type="number"
                    value={testAge}
                    onChange={(e) => setTestAge(Number(e.target.value))}
                    className="w-full text-xs p-2 border border-slate-300 rounded bg-white"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-semibold text-slate-600 mb-1">District / Location</label>
                  <input
                    type="text"
                    value={testDistrict}
                    onChange={(e) => setTestDistrict(e.target.value)}
                    className="w-full text-xs p-2 border border-slate-300 rounded bg-white"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-semibold text-slate-600 mb-1">Education Level</label>
                  <select
                    value={testEducation}
                    onChange={(e) => setTestEducation(e.target.value)}
                    className="w-full text-xs p-2 border border-slate-300 rounded bg-white"
                  >
                    <option value="PRIMARY">Primary</option>
                    <option value="SECONDARY">Secondary</option>
                    <option value="HIGH_SCHOOL">High School</option>
                    <option value="VOCATIONAL">Vocational Certificate</option>
                    <option value="UNDERGRADUATE">Undergraduate Degree</option>
                  </select>
                </div>
                <div>
                  <label className="block text-[11px] font-semibold text-slate-600 mb-1">Skills (comma separated)</label>
                  <input
                    type="text"
                    value={testSkills}
                    onChange={(e) => setTestSkills(e.target.value)}
                    className="w-full text-xs p-2 border border-slate-300 rounded bg-white"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-semibold text-slate-600 mb-1">Interests (comma separated)</label>
                  <input
                    type="text"
                    value={testInterests}
                    onChange={(e) => setTestInterests(e.target.value)}
                    className="w-full text-xs p-2 border border-slate-300 rounded bg-white"
                  />
                </div>

                <button
                  onClick={runMatchCalculation}
                  disabled={isCalculating}
                  className="w-full py-2 bg-rose-600 hover:bg-rose-700 text-white font-bold text-xs rounded transition cursor-pointer"
                >
                  {isCalculating ? 'Evaluating Rules...' : 'Re-Run Rule Engine'}
                </button>
              </div>

              {/* Engine Output */}
              <div className="bg-slate-900 text-slate-100 p-5 rounded-xl flex flex-col justify-between">
                <div>
                  <span className="text-[11px] font-bold text-rose-400 uppercase tracking-wider block mb-2">
                    Engine Determination
                  </span>
                  
                  {matchResult ? (
                    <div className="space-y-4">
                      <div className="bg-slate-800 p-3 rounded-lg border border-slate-700 flex items-center justify-between">
                        <div>
                          <div className="text-[10px] text-slate-400 uppercase">Match Score</div>
                          <div className="text-3xl font-black text-rose-400">{matchResult.score}%</div>
                        </div>
                        <span className={`px-2 py-1 rounded text-xs font-bold ${
                          matchResult.score >= 80 ? 'bg-emerald-500/20 text-emerald-300' : 'bg-amber-500/20 text-amber-300'
                        }`}>
                          {matchResult.score >= 80 ? 'HIGH ELIGIBILITY' : 'MODERATE FIT'}
                        </span>
                      </div>

                      <div>
                        <div className="text-xs font-bold text-slate-300 mb-1">Matching Reasons:</div>
                        <div className="space-y-1">
                          {matchResult.reasons?.map((r: string, idx: number) => (
                            <div key={idx} className="text-xs text-emerald-400 flex items-start gap-1.5">
                              <span>✓</span> <span>{r}</span>
                            </div>
                          ))}
                        </div>
                      </div>

                      <div>
                        <div className="text-xs font-bold text-slate-300 mb-1">Missing Requirements:</div>
                        {matchResult.missing_requirements?.length > 0 ? (
                          <div className="space-y-1">
                            {matchResult.missing_requirements.map((m: string, idx: number) => (
                              <div key={idx} className="text-xs text-amber-400 flex items-start gap-1.5">
                                <span>!</span> <span>{m}</span>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <div className="text-xs text-slate-400">All mandatory requirements met.</div>
                        )}
                      </div>
                    </div>
                  ) : (
                    <div className="text-xs text-slate-400">Calculating...</div>
                  )}
                </div>

                <div className="text-[10px] text-slate-500 pt-3 border-t border-slate-800">
                  Rules engine enforces deterministic constraints (no AI hallucinations in matching outcomes).
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Manual Participant Enrollment Modal */}
      {enrollModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/60 p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-xl border border-slate-200">
            <h3 className="text-base font-bold text-slate-900 mb-1">Add Participant to Programme</h3>
            <p className="text-xs text-slate-500 mb-4">Enroll a new beneficiary directly into this active cohort.</p>

            <form onSubmit={handleEnrollSubmit} className="space-y-3">
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-[11px] font-semibold text-slate-700 mb-1">First Name</label>
                  <input
                    type="text"
                    required
                    value={newFirstName}
                    onChange={(e) => setNewFirstName(e.target.value)}
                    placeholder="Aisha"
                    className="w-full text-xs p-2 border border-slate-300 rounded"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-semibold text-slate-700 mb-1">Last Name</label>
                  <input
                    type="text"
                    required
                    value={newLastName}
                    onChange={(e) => setNewLastName(e.target.value)}
                    placeholder="Namagembe"
                    className="w-full text-xs p-2 border border-slate-300 rounded"
                  />
                </div>
              </div>

              <div>
                <label className="block text-[11px] font-semibold text-slate-700 mb-1">Email</label>
                <input
                  type="email"
                  required
                  value={newEmail}
                  onChange={(e) => setNewEmail(e.target.value)}
                  placeholder="aisha.n@example.com"
                  className="w-full text-xs p-2 border border-slate-300 rounded"
                />
              </div>

              <div>
                <label className="block text-[11px] font-semibold text-slate-700 mb-1">Phone</label>
                <input
                  type="text"
                  required
                  value={newPhone}
                  onChange={(e) => setNewPhone(e.target.value)}
                  placeholder="+256 701 234567"
                  className="w-full text-xs p-2 border border-slate-300 rounded"
                />
              </div>

              <div>
                <label className="block text-[11px] font-semibold text-slate-700 mb-1">District</label>
                <input
                  type="text"
                  required
                  value={newDistrict}
                  onChange={(e) => setNewDistrict(e.target.value)}
                  placeholder="Kampala"
                  className="w-full text-xs p-2 border border-slate-300 rounded"
                />
              </div>

              <div className="flex items-center justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setEnrollModal(false)}
                  className="px-3 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-100 rounded"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-rose-600 hover:bg-rose-700 text-white text-xs font-bold rounded shadow-xs"
                >
                  Enroll Participant
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
