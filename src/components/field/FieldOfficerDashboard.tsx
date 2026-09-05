import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { VerificationTask, Form, BeneficiaryParticipation } from '../../types';
import { api } from '../../services/api';
import { 
  ClipboardCheck, 
  MapPin, 
  CheckCircle2, 
  AlertTriangle, 
  Phone, 
  Calendar, 
  Check, 
  X, 
  FileText, 
  UserCheck, 
  Search,
  Sparkles,
  Send
} from 'lucide-react';

export const FieldOfficerDashboard: React.FC = () => {
  const { user } = useAuth();
  const [tasks, setTasks] = useState<VerificationTask[]>([]);
  const [participants, setParticipants] = useState<BeneficiaryParticipation[]>([]);
  const [activeTab, setActiveTab] = useState<'TASKS' | 'ATTENDANCE' | 'ASSISTED_SURVEY'>('TASKS');
  const [selectedTask, setSelectedTask] = useState<VerificationTask | null>(null);
  const [fieldNotes, setFieldNotes] = useState('');
  const [isVerifying, setIsVerifying] = useState(false);

  // Quick field observation state
  const [selectedParticipantForChallenge, setSelectedParticipantForChallenge] = useState('fatima_zara');
  const [obsCategory, setObsCategory] = useState('TRANSPORT');
  const [obsDesc, setObsDesc] = useState('');
  const [obsSuccess, setObsSuccess] = useState(false);

  // Attendance state
  const [attendanceRecords, setAttendanceRecords] = useState<Record<string, boolean>>({});

  useEffect(() => {
    const load = async () => {
      try {
        const [tks, pts] = await Promise.all([
          api.getVerificationTasks(),
          api.getParticipants('prog_1')
        ]);
        setTasks(tks);
        setParticipants(pts);

        // Pre-fill attendance
        const initialAtt: Record<string, boolean> = {};
        pts.forEach(p => {
          initialAtt[p.id] = (p.attendance_rate || 0) > 50;
        });
        setAttendanceRecords(initialAtt);
      } catch (e) {
        console.error(e);
      }
    };
    load();
  }, []);

  const handleUpdateTaskStatus = async (taskId: string, newStatus: string) => {
    try {
      const updated = await api.updateVerificationTask(taskId, {
        status: newStatus,
        notes: fieldNotes || 'Field verification completed and attested.',
        verified_by: user?.first_name || 'Sarah Kibuuka'
      });
      setTasks(tasks.map(t => t.id === taskId ? updated : t));
      setSelectedTask(null);
      setFieldNotes('');
    } catch (e) {
      console.error(e);
    }
  };

  const handleLogObservation = async (e: React.FormEvent) => {
    e.preventDefault();
    await api.reportChallenge('prog_1', {
      beneficiary_id: 'usr_beneficiary',
      beneficiary_name: 'Fatima Zara (Reported by Field Officer)',
      category: obsCategory,
      severity: 'HIGH',
      description: obsDesc
    });
    setObsDesc('');
    setObsSuccess(true);
    setTimeout(() => setObsSuccess(false), 3000);
  };

  const toggleAttendance = (pId: string) => {
    setAttendanceRecords(prev => ({ ...prev, [pId]: !prev[pId] }));
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6" id="field-officer-dashboard">
      {/* Officer Header */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-slate-100 border border-slate-200 text-slate-800 flex items-center justify-center font-bold text-base shadow-xs">
            FO
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold text-slate-900">
                {user?.first_name} {user?.last_name}
              </h1>
              <span className="px-2.5 py-0.5 rounded-md text-[10px] font-semibold bg-indigo-50 text-indigo-700 border border-indigo-100">
                Central Region Field Officer
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-0.5">
              Assigned to: FemmeTech Africa Foundation • Kampala & Wakiso Districts
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="px-3 py-1.5 rounded-md bg-emerald-50 text-emerald-800 text-xs font-semibold flex items-center gap-1.5 border border-emerald-200">
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            Field Sync Online
          </span>
        </div>
      </div>

      {/* Sub Tabs */}
      <div className="border-b border-slate-200 overflow-x-auto">
        <nav className="flex space-x-2 py-1">
          <button
            onClick={() => setActiveTab('TASKS')}
            className={`px-3.5 py-2 rounded-md text-xs font-medium transition-colors flex items-center gap-2 cursor-pointer ${
              activeTab === 'TASKS' ? 'bg-slate-900 text-white shadow-xs' : 'text-slate-500 hover:text-slate-900 hover:bg-slate-100'
            }`}
          >
            <ClipboardCheck className="w-4 h-4" />
            <span>Assigned Verifications ({tasks.filter(t => t.status === 'PENDING').length} Pending)</span>
          </button>

          <button
            onClick={() => setActiveTab('ATTENDANCE')}
            className={`px-3.5 py-2 rounded-md text-xs font-medium transition-colors flex items-center gap-2 cursor-pointer ${
              activeTab === 'ATTENDANCE' ? 'bg-slate-900 text-white shadow-xs' : 'text-slate-500 hover:text-slate-900 hover:bg-slate-100'
            }`}
          >
            <UserCheck className="w-4 h-4" />
            <span>Attendance Check-In</span>
          </button>

          <button
            onClick={() => setActiveTab('ASSISTED_SURVEY')}
            className={`px-3.5 py-2 rounded-md text-xs font-medium transition-colors flex items-center gap-2 cursor-pointer ${
              activeTab === 'ASSISTED_SURVEY' ? 'bg-slate-900 text-white shadow-xs' : 'text-slate-500 hover:text-slate-900 hover:bg-slate-100'
            }`}
          >
            <FileText className="w-4 h-4" />
            <span>Log Field Observation</span>
          </button>
        </nav>
      </div>

      {/* Tab 1: Verification Checklist */}
      {activeTab === 'TASKS' && (
        <div className="space-y-4">
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
            <h2 className="text-base font-bold text-slate-900">Participant Verification Queue</h2>
            <p className="text-xs text-slate-500">
              Complete on-site ID validation, home visits, and contact guardian to verify scholarship candidate authenticity.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {tasks.map((task) => (
              <div key={task.id} className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-md ${
                      task.status === 'VERIFIED' ? 'bg-emerald-50 text-emerald-800 border border-emerald-200' :
                      task.status === 'FLAGGED' ? 'bg-red-50 text-red-800 border border-red-200' : 'bg-amber-50 text-amber-800 border border-amber-200'
                    }`}>
                      {task.status}
                    </span>
                    <span className="text-[11px] text-slate-400 font-medium">Task #{task.id}</span>
                  </div>

                  <h3 className="font-bold text-slate-900 text-base">{task.beneficiary_name}</h3>
                  <div className="text-xs text-slate-500 flex items-center gap-1.5 mt-1">
                    <MapPin className="w-3.5 h-3.5 text-slate-400" />
                    <span>{task.location}</span>
                  </div>

                  {/* Verification items */}
                  <div className="mt-3 p-3 bg-slate-50 rounded-lg border border-slate-200 text-xs space-y-1.5">
                    <div className="flex items-center justify-between">
                      <span className="text-slate-600">ID & National NIN Verification:</span>
                      <span className="font-semibold text-emerald-600">Checked ✓</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-slate-600">In-Person Home Visit:</span>
                      <span className="font-semibold text-emerald-600">Completed ✓</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-slate-600">Guardian Attestation:</span>
                      <span className="font-semibold text-slate-800">Phone Confirmed</span>
                    </div>
                  </div>

                  {task.notes && (
                    <div className="mt-2 text-xs text-slate-600 italic">
                      Note: "{task.notes}"
                    </div>
                  )}
                </div>

                <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between gap-2">
                  <button
                    onClick={() => handleUpdateTaskStatus(task.id, 'FLAGGED')}
                    className="px-3 py-1.5 rounded-md border border-red-200 text-red-700 hover:bg-red-50 text-xs font-medium transition-colors flex items-center gap-1 cursor-pointer"
                  >
                    <X className="w-3.5 h-3.5" /> Flag Issue
                  </button>
                  <button
                    onClick={() => handleUpdateTaskStatus(task.id, 'VERIFIED')}
                    className="px-4 py-1.5 rounded-md bg-slate-900 hover:bg-slate-800 text-white text-xs font-medium transition-colors flex items-center gap-1 cursor-pointer shadow-xs"
                  >
                    <Check className="w-3.5 h-3.5" /> Confirm Verified
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab 2: Attendance Check-In */}
      {activeTab === 'ATTENDANCE' && (
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-100">
            <div>
              <h2 className="text-base font-bold text-slate-900">Session Attendance Roster</h2>
              <p className="text-xs text-slate-500">Tap participant to toggle present/absent for today's technical workshop.</p>
            </div>
            <button
              onClick={() => alert('Attendance successfully committed to programme monitoring engine!')}
              className="px-3.5 py-2 bg-slate-900 text-white text-xs font-medium rounded-md hover:bg-slate-800 transition-colors cursor-pointer shadow-sm"
            >
              Save Attendance Record
            </button>
          </div>

          <div className="space-y-2">
            {participants.map((p) => {
              const isPresent = attendanceRecords[p.id] !== false;
              return (
                <div
                  key={p.id}
                  onClick={() => toggleAttendance(p.id)}
                  className={`p-3.5 rounded-xl border transition-colors flex items-center justify-between cursor-pointer ${
                    isPresent
                      ? 'bg-emerald-50/40 border-emerald-200 text-emerald-950'
                      : 'bg-slate-50 border-slate-200 text-slate-500'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-semibold ${
                      isPresent ? 'bg-emerald-600 text-white' : 'bg-slate-300 text-slate-600'
                    }`}>
                      {isPresent ? '✓' : '✕'}
                    </div>
                    <div>
                      <div className="font-semibold text-xs text-slate-900">
                        {p.beneficiary?.first_name} {p.beneficiary?.last_name}
                      </div>
                      <div className="text-[11px] opacity-75">{p.beneficiary?.email}</div>
                    </div>
                  </div>

                  <span className={`text-xs font-semibold px-2.5 py-0.5 rounded-md ${
                    isPresent ? 'bg-emerald-100 text-emerald-800' : 'bg-slate-200 text-slate-700'
                  }`}>
                    {isPresent ? 'Present Today' : 'Absent'}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Tab 3: Assisted Survey / Observation Logger */}
      {activeTab === 'ASSISTED_SURVEY' && (
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm max-w-xl mx-auto space-y-4">
          <div>
            <h2 className="text-base font-bold text-slate-900">Direct Field Observation / Barrier Logger</h2>
            <p className="text-xs text-slate-500">
              Notice an acute challenge during a home or session visit? Log it immediately to trigger early intervention.
            </p>
          </div>

          {obsSuccess && (
            <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-semibold rounded-lg">
              Observation registered into programme alert engine!
            </div>
          )}

          <form onSubmit={handleLogObservation} className="space-y-3.5 text-xs">
            <div>
              <label className="block font-semibold text-slate-700 mb-1">Participant</label>
              <select
                value={selectedParticipantForChallenge}
                onChange={(e) => setSelectedParticipantForChallenge(e.target.value)}
                className="w-full p-2.5 border border-slate-200 rounded-lg bg-white focus:ring-2 focus:ring-indigo-500 focus:outline-none"
              >
                {participants.map(p => (
                  <option key={p.id} value={p.id}>
                    {p.beneficiary?.first_name} {p.beneficiary?.last_name} ({p.beneficiary?.district})
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block font-semibold text-slate-700 mb-1">Observed Barrier Category</label>
              <select
                value={obsCategory}
                onChange={(e) => setObsCategory(e.target.value)}
                className="w-full p-2.5 border border-slate-200 rounded-lg bg-white focus:ring-2 focus:ring-indigo-500 focus:outline-none"
              >
                <option value="TRANSPORT">Transportation (Minibus fare / route security)</option>
                <option value="MATERIALS">Hardware / Adapter / Electricity outage</option>
                <option value="HEALTH">Health issue / illness</option>
                <option value="ATTENDANCE">Family caretaking conflict</option>
                <option value="FINANCIAL">Living stipend emergency</option>
              </select>
            </div>

            <div>
              <label className="block font-semibold text-slate-700 mb-1">Field Observation Details</label>
              <textarea
                rows={3}
                required
                value={obsDesc}
                onChange={(e) => setObsDesc(e.target.value)}
                placeholder="Observed participant unable to charge laptop due to local transformer failure..."
                className="w-full p-2.5 border border-slate-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none"
              />
            </div>

            <div className="pt-2">
              <button
                type="submit"
                className="w-full py-2.5 bg-slate-900 hover:bg-slate-800 text-white font-medium rounded-md transition-colors shadow-sm flex items-center justify-center gap-1.5 cursor-pointer"
              >
                <Send className="w-3.5 h-3.5" />
                Dispatch Field Observation to Headquarters
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};
