import React, { useState, useEffect } from 'react';
import { Challenge, ChallengeSeverity, ChallengeStatus } from '../../types';
import { api } from '../../services/api';
import { 
  AlertTriangle, 
  CheckCircle2, 
  Clock, 
  UserCheck, 
  Filter, 
  Plus, 
  Send, 
  ShieldAlert, 
  TrendingDown, 
  Bus, 
  Laptop, 
  HeartHandshake, 
  ArrowRight,
  Sparkles,
  History
} from 'lucide-react';

interface OrgMonitoringProps {
  programmeId: string;
  challenges: Challenge[];
  onRefresh: () => void;
}

export const OrgMonitoring: React.FC<OrgMonitoringProps> = ({ programmeId, challenges, onRefresh }) => {
  const [challengeAnalytics, setChallengeAnalytics] = useState<any>(null);
  const [selectedChallenge, setSelectedChallenge] = useState<Challenge | null>(null);
  const [assignModal, setAssignModal] = useState<Challenge | null>(null);
  const [resolveModal, setResolveModal] = useState<Challenge | null>(null);
  const [assignedOfficerName, setAssignedOfficerName] = useState('Sarah Kibuuka (Field Officer)');
  const [assignNotes, setAssignNotes] = useState('');
  const [resolutionNotes, setResolutionNotes] = useState('');
  const [filterSeverity, setFilterSeverity] = useState<string>('ALL');
  const [filterStatus, setFilterStatus] = useState<string>('ALL');

  useEffect(() => {
    api.getChallengeAnalytics(programmeId).then(data => setChallengeAnalytics(data)).catch(() => {});
  }, [programmeId]);

  const handleAssign = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!assignModal) return;
    await api.assignChallenge(assignModal.id, {
      assigned_to: 'usr_field_officer',
      assigned_to_name: assignedOfficerName,
      notes: assignNotes
    });
    setAssignModal(null);
    setAssignNotes('');
    onRefresh();
  };

  const handleResolve = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!resolveModal) return;
    await api.resolveChallenge(resolveModal.id, resolutionNotes);
    setResolveModal(null);
    setResolutionNotes('');
    onRefresh();
  };

  const filtered = challenges.filter(c => {
    if (filterSeverity !== 'ALL' && c.severity !== filterSeverity) return false;
    if (filterStatus !== 'ALL' && c.status !== filterStatus) return false;
    return true;
  });

  const severityBadge = (s: ChallengeSeverity) => {
    switch (s) {
      case 'CRITICAL':
        return <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-red-100 text-red-800 border border-red-200">CRITICAL</span>;
      case 'HIGH':
        return <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-rose-100 text-rose-800 border border-rose-200">HIGH</span>;
      case 'MEDIUM':
        return <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-amber-100 text-amber-800 border border-amber-200">MEDIUM</span>;
      default:
        return <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-blue-100 text-blue-800 border border-blue-200">LOW</span>;
    }
  };

  const statusBadge = (st: ChallengeStatus) => {
    switch (st) {
      case 'OPEN':
        return <span className="px-2 py-0.5 rounded-full text-[11px] font-semibold bg-red-50 text-red-700 border border-red-200">Open Alert</span>;
      case 'IN_PROGRESS':
        return <span className="px-2 py-0.5 rounded-full text-[11px] font-semibold bg-amber-50 text-amber-700 border border-amber-200">Field In Progress</span>;
      case 'RESOLVED':
        return <span className="px-2 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">Resolved</span>;
    }
  };

  return (
    <div className="space-y-6" id="monitoring-view">
      {/* 🚨 Urgent Challenges Aggregated Alert Banner */}
      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm relative overflow-hidden">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 text-xs font-semibold text-rose-600 uppercase tracking-wider mb-1">
              <ShieldAlert className="w-4 h-4" />
              Automated Early Challenge Detection Engine
            </div>
            <h2 className="text-xl font-bold tracking-tight text-slate-900">
              Urgent Clustered Challenges Requiring Immediate Intervention
            </h2>
            <p className="text-xs text-slate-500 mt-1 max-w-2xl">
              Survey answers and field alerts are aggregated continuously. Intervene before issues cause participant dropouts.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <div className="bg-rose-50 px-4 py-2.5 rounded-xl border border-rose-100 text-center min-w-[100px]">
              <div className="text-2xl font-bold text-rose-700">35</div>
              <div className="text-[10px] text-rose-600 uppercase font-semibold">Transport Alerts</div>
            </div>
            <div className="bg-amber-50 px-4 py-2.5 rounded-xl border border-amber-100 text-center min-w-[100px]">
              <div className="text-2xl font-bold text-amber-700">18</div>
              <div className="text-[10px] text-amber-600 uppercase font-semibold">Power / Materials</div>
            </div>
          </div>
        </div>

        {/* Highlighted Recurring Clusters */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mt-5 pt-4 border-t border-slate-100">
          <div className="bg-slate-50 p-3.5 rounded-lg border border-slate-100">
            <div className="flex items-center gap-2 text-xs font-semibold text-rose-700 mb-1">
              <Bus className="w-3.5 h-3.5 text-rose-500" />
              35 Transport Submissions
            </div>
            <p className="text-xs text-slate-600 leading-snug">
              Minibus fare inflation along Northern route. Recommended: weekly transit top-up stipend.
            </p>
          </div>

          <div className="bg-slate-50 p-3.5 rounded-lg border border-slate-100">
            <div className="flex items-center gap-2 text-xs font-semibold text-amber-700 mb-1">
              <Laptop className="w-3.5 h-3.5 text-amber-500" />
              18 Device Power Issues
            </div>
            <p className="text-xs text-slate-600 leading-snug">
              Power grid surge in Wakiso. Recommended: dispatch replacement surge-protected packs.
            </p>
          </div>

          <div className="bg-slate-50 p-3.5 rounded-lg border border-slate-100">
            <div className="flex items-center gap-2 text-xs font-semibold text-indigo-700 mb-1">
              <HeartHandshake className="w-3.5 h-3.5 text-indigo-500" />
              12 Family Care Demands
            </div>
            <p className="text-xs text-slate-600 leading-snug">
              Daytime domestic chores or childcare obligations. Recommended: asynchronous study sessions.
            </p>
          </div>
        </div>
      </div>

      {/* Response Workflow Diagram Capsule */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 text-xs flex flex-wrap items-center justify-between gap-3 shadow-sm">
        <div className="flex items-center gap-2 font-semibold text-slate-800">
          <Sparkles className="w-4 h-4 text-indigo-600" />
          <span>Closed-Loop Response Workflow:</span>
        </div>
        <div className="flex items-center gap-2 text-slate-600 overflow-x-auto py-1">
          <span className="bg-slate-100 px-2 py-0.5 rounded-md font-medium text-[11px]">1. Participant Reports</span>
          <ArrowRight className="w-3 h-3 text-slate-400 shrink-0" />
          <span className="bg-rose-50 text-rose-700 px-2 py-0.5 rounded-md font-semibold text-[11px]">2. Cluster Detected</span>
          <ArrowRight className="w-3 h-3 text-slate-400 shrink-0" />
          <span className="bg-amber-50 text-amber-700 px-2 py-0.5 rounded-md font-semibold text-[11px]">3. Field Officer Assigned</span>
          <ArrowRight className="w-3 h-3 text-slate-400 shrink-0" />
          <span className="bg-indigo-50 text-indigo-700 px-2 py-0.5 rounded-md font-semibold text-[11px]">4. On-site Action</span>
          <ArrowRight className="w-3 h-3 text-slate-400 shrink-0" />
          <span className="bg-emerald-50 text-emerald-700 px-2 py-0.5 rounded-md font-semibold text-[11px]">5. Resolved & Audited</span>
        </div>
      </div>

      {/* Filter and Challenge List */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4 pb-3 border-b border-slate-100">
          <div>
            <h3 className="font-bold text-slate-800 text-base">Active Programme Challenges Log</h3>
            <p className="text-xs text-slate-500">Track and assign specific individual or group barriers.</p>
          </div>

          <div className="flex items-center gap-2">
            <select
              value={filterSeverity}
              onChange={(e) => setFilterSeverity(e.target.value)}
              className="text-xs border border-slate-200 rounded-md px-2.5 py-1.5 bg-white text-slate-700 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            >
              <option value="ALL">All Severities</option>
              <option value="CRITICAL">Critical Only</option>
              <option value="HIGH">High</option>
              <option value="MEDIUM">Medium</option>
              <option value="LOW">Low</option>
            </select>

            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="text-xs border border-slate-200 rounded-md px-2.5 py-1.5 bg-white text-slate-700 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            >
              <option value="ALL">All Statuses</option>
              <option value="OPEN">Open Only</option>
              <option value="IN_PROGRESS">In Progress</option>
              <option value="RESOLVED">Resolved</option>
            </select>
          </div>
        </div>

        {/* Challenges Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-700">
            <thead className="bg-slate-50 text-slate-500 font-semibold border-y border-slate-200">
              <tr>
                <th className="py-2.5 px-3 font-medium">Participant</th>
                <th className="py-2.5 px-3 font-medium">Category</th>
                <th className="py-2.5 px-3 font-medium">Severity</th>
                <th className="py-2.5 px-3 font-medium">Description</th>
                <th className="py-2.5 px-3 font-medium">Status</th>
                <th className="py-2.5 px-3 font-medium">Assigned To</th>
                <th className="py-2.5 px-3 text-right font-medium">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filtered.map((c) => (
                <tr key={c.id} className="hover:bg-slate-50/80 transition-colors">
                  <td className="py-3 px-3 font-semibold text-slate-900 whitespace-nowrap">
                    {c.beneficiary_name || 'Participant'}
                  </td>
                  <td className="py-3 px-3">
                    <span className="font-semibold text-slate-800">{c.category}</span>
                  </td>
                  <td className="py-3 px-3 whitespace-nowrap">
                    {severityBadge(c.severity)}
                  </td>
                  <td className="py-3 px-3 max-w-xs">
                    <p className="line-clamp-2 text-slate-600">{c.description}</p>
                    {c.resolution_notes && (
                      <p className="text-[11px] text-emerald-700 font-medium mt-1">
                        Resolution: {c.resolution_notes}
                      </p>
                    )}
                  </td>
                  <td className="py-3 px-3 whitespace-nowrap">
                    {statusBadge(c.status)}
                  </td>
                  <td className="py-3 px-3 whitespace-nowrap text-slate-600 font-medium">
                    {c.assigned_to_name || 'Unassigned'}
                  </td>
                  <td className="py-3 px-3 text-right whitespace-nowrap space-x-1.5">
                    {c.status !== 'RESOLVED' && (
                      <>
                        <button
                          onClick={() => setAssignModal(c)}
                          className="px-2.5 py-1 rounded-md bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium text-xs transition-colors cursor-pointer"
                        >
                          {c.assigned_to ? 'Reassign' : 'Assign'}
                        </button>
                        <button
                          onClick={() => setResolveModal(c)}
                          className="px-2.5 py-1 rounded-md bg-slate-900 hover:bg-slate-800 text-white font-medium text-xs transition-colors cursor-pointer shadow-xs"
                        >
                          Resolve
                        </button>
                      </>
                    )}
                    <button
                      onClick={() => setSelectedChallenge(c)}
                      className="px-2 py-1 text-slate-400 hover:text-slate-700 font-medium text-xs cursor-pointer"
                      title="View Audit Trail"
                    >
                      <History className="w-3.5 h-3.5 inline" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Assign Field Officer Modal */}
      {assignModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/50 p-4 backdrop-blur-xs">
          <div className="bg-white rounded-xl max-w-md w-full p-6 shadow-xl border border-slate-200">
            <h3 className="text-lg font-bold text-slate-900 mb-1">Assign Challenge to Response Team</h3>
            <p className="text-xs text-slate-500 mb-4">
              Dispatch a localized field officer to verify and implement support for {assignModal.beneficiary_name}.
            </p>

            <form onSubmit={handleAssign} className="space-y-3.5">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Field Officer / Responder</label>
                <select
                  value={assignedOfficerName}
                  onChange={(e) => setAssignedOfficerName(e.target.value)}
                  className="w-full text-xs p-2.5 border border-slate-200 rounded-lg bg-white font-medium focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                >
                  <option value="Sarah Kibuuka (Field Officer - Central)">Sarah Kibuuka (Field Officer - Central Region)</option>
                  <option value="David Ocen (Field Responder - North)">David Ocen (Field Responder - Northern Region)</option>
                  <option value="Grace Atuhaire (Welfare Coordinator)">Grace Atuhaire (Welfare Coordinator)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Instruction & Action Mandate</label>
                <textarea
                  rows={3}
                  required
                  value={assignNotes}
                  onChange={(e) => setAssignNotes(e.target.value)}
                  placeholder="e.g. Conduct in-person visit to deliver transport voucher stipend..."
                  className="w-full text-xs p-2.5 border border-slate-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                />
              </div>

              <div className="flex items-center justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setAssignModal(null)}
                  className="px-3.5 py-2 text-xs font-medium text-slate-600 hover:bg-slate-100 rounded-md transition-colors cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white text-xs font-medium rounded-md transition-colors shadow-sm cursor-pointer"
                >
                  Assign & Notify Responder
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Resolve Challenge Modal */}
      {resolveModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/50 p-4 backdrop-blur-xs">
          <div className="bg-white rounded-xl max-w-md w-full p-6 shadow-xl border border-slate-200">
            <h3 className="text-lg font-bold text-slate-900 mb-1">Record Challenge Resolution</h3>
            <p className="text-xs text-slate-500 mb-4">
              Close this challenge and record the outcome for donor and audit reporting.
            </p>

            <form onSubmit={handleResolve} className="space-y-3.5">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Resolution Summary</label>
                <textarea
                  rows={3}
                  required
                  value={resolutionNotes}
                  onChange={(e) => setResolutionNotes(e.target.value)}
                  placeholder="e.g. Disbursed weekly transport subsidy; participant confirmed attendance resumed without barrier."
                  className="w-full text-xs p-2.5 border border-slate-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                />
              </div>

              <div className="flex items-center justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setResolveModal(null)}
                  className="px-3.5 py-2 text-xs font-medium text-slate-600 hover:bg-slate-100 rounded-md transition-colors cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-medium rounded-md transition-colors shadow-sm cursor-pointer"
                >
                  Mark as Resolved
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Audit Trail Modal */}
      {selectedChallenge && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/50 p-4 backdrop-blur-xs">
          <div className="bg-white rounded-xl max-w-lg w-full p-6 shadow-xl border border-slate-200 max-h-[80vh] overflow-y-auto">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
              <h3 className="text-base font-bold text-slate-900">Challenge Audit Trail & Timeline</h3>
              <button onClick={() => setSelectedChallenge(null)} className="text-slate-400 hover:text-slate-600 font-bold p-1 cursor-pointer">✕</button>
            </div>

            <div className="space-y-3">
              <div className="text-xs bg-slate-50 p-3.5 rounded-lg border border-slate-200">
                <div className="font-semibold text-slate-900">{selectedChallenge.beneficiary_name} — {selectedChallenge.category}</div>
                <p className="text-slate-600 mt-1">{selectedChallenge.description}</p>
              </div>

              <div className="border-l-2 border-slate-200 pl-4 space-y-3 py-2">
                {(selectedChallenge.audit_history || []).map((entry, idx) => (
                  <div key={idx} className="relative text-xs">
                    <span className="absolute -left-[21px] top-0.5 w-2.5 h-2.5 rounded-full bg-indigo-600 ring-4 ring-white" />
                    <div className="font-semibold text-slate-800">{entry.action} by {entry.actor}</div>
                    <div className="text-[11px] text-slate-400">{new Date(entry.timestamp).toLocaleString()}</div>
                    {entry.note && <div className="text-slate-600 mt-0.5">{entry.note}</div>}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
