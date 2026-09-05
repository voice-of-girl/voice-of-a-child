import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { Programme, BeneficiaryParticipation, Form, Challenge } from '../../types';
import { api } from '../../services/api';
import { OrgOverview } from './OrgOverview';
import { OrgProgrammes } from './OrgProgrammes';
import { OrgParticipants } from './OrgParticipants';
import { OrgFormBuilder } from './OrgFormBuilder';
import { OrgMonitoring } from './OrgMonitoring';
import { OrgImpact } from './OrgImpact';
import { OrgReports } from './OrgReports';
import { 
  BarChart3, 
  Target, 
  Users, 
  FileSpreadsheet, 
  Activity, 
  TrendingUp, 
  FileText, 
  ChevronDown, 
  Plus,
  RefreshCw,
  Sparkles
} from 'lucide-react';

export const OrgDashboard: React.FC = () => {
  const { organisation } = useAuth();
  const [programmes, setProgrammes] = useState<Programme[]>([]);
  const [selectedProgrammeId, setSelectedProgrammeId] = useState<string>('prog_1');
  const [activeTab, setActiveTab] = useState<string>('overview');

  // Programme state
  const [participants, setParticipants] = useState<BeneficiaryParticipation[]>([]);
  const [forms, setForms] = useState<Form[]>([]);
  const [challenges, setChallenges] = useState<Challenge[]>([]);
  const [analytics, setAnalytics] = useState<any>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const progs = await api.getProgrammes();
      setProgrammes(progs);
      const currId = selectedProgrammeId || progs[0]?.id || 'prog_1';
      setSelectedProgrammeId(currId);

      const [pts, fms, chs, anls] = await Promise.all([
        api.getParticipants(currId),
        api.getForms(currId),
        api.getChallenges(currId),
        api.getAnalytics(currId)
      ]);

      setParticipants(pts);
      setForms(fms);
      setChallenges(chs);
      setAnalytics(anls);
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [selectedProgrammeId]);

  const activeProgramme = programmes.find(p => p.id === selectedProgrammeId) || programmes[0];

  const tabs = [
    { id: 'overview', label: 'Overview', icon: BarChart3 },
    { id: 'programmes', label: 'Programmes', icon: Target },
    { id: 'participants', label: 'Participants & Matching', icon: Users },
    { id: 'forms', label: 'Forms & Surveys', icon: FileSpreadsheet },
    { id: 'monitoring', label: 'Monitoring & Challenges', icon: Activity },
    { id: 'impact', label: 'Impact & Outcomes', icon: TrendingUp },
    { id: 'reports', label: 'Reports', icon: FileText }
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6" id="org-admin-dashboard">
      {/* Organisation Banner & Active Programme Switcher */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-[10px] font-semibold px-2 py-0.5 rounded-md bg-indigo-50 text-indigo-700 border border-indigo-200 uppercase tracking-wider">
              {organisation?.organisation_type || 'NGO'}
            </span>
            <span className="text-xs font-medium text-emerald-600 flex items-center gap-1">
              ✓ Verified Organisation
            </span>
          </div>
          <h1 className="text-xl sm:text-2xl font-bold text-slate-900 mt-1">
            {organisation?.name || 'FemmeTech Africa Foundation'}
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            {organisation?.address || 'Plot 14 Innovation Way, Bugolobi'}, {organisation?.district || 'Kampala'}, Uganda
          </p>
        </div>

        <div className="flex items-center gap-3 w-full md:w-auto">
          {/* Active Programme Dropdown */}
          <div className="relative flex-1 md:w-72">
            <label className="block text-[10px] font-semibold uppercase tracking-wider text-slate-400 mb-1">
              Active Programme Workspace
            </label>
            <div className="relative">
              <select
                value={selectedProgrammeId}
                onChange={(e) => setSelectedProgrammeId(e.target.value)}
                className="w-full text-xs font-semibold text-slate-900 bg-slate-50 border border-slate-200 rounded-lg p-2.5 pr-8 appearance-none focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white cursor-pointer transition-colors"
                id="programme-switcher-select"
              >
                {programmes.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.name}
                  </option>
                ))}
              </select>
              <ChevronDown className="w-4 h-4 text-slate-400 absolute right-2.5 top-3 pointer-events-none" />
            </div>
          </div>

          <button
            onClick={loadData}
            className="p-2.5 mt-5 text-slate-400 hover:text-slate-700 hover:bg-slate-50 rounded-lg transition-colors border border-slate-200 cursor-pointer"
            title="Refresh Data"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin text-indigo-600' : ''}`} />
          </button>
        </div>
      </div>

      {/* Navigation Sub-Tabs */}
      <div className="border-b border-slate-200 overflow-x-auto">
        <nav className="flex space-x-1 py-1 min-w-max" aria-label="Tabs">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isCurrent = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-3.5 py-2.5 rounded-lg text-xs font-medium transition-colors cursor-pointer ${
                  isCurrent
                    ? 'bg-indigo-50 text-indigo-700 font-semibold border border-indigo-100'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                }`}
                id={`tab-${tab.id}`}
              >
                <Icon className={`w-4 h-4 shrink-0 ${isCurrent ? 'text-indigo-600' : 'text-slate-400'}`} />
                <span>{tab.label}</span>
                {tab.id === 'monitoring' && challenges.filter(c => c.status !== 'RESOLVED').length > 0 && (
                  <span className={`px-1.5 py-0.2 rounded-full text-[10px] font-bold ${
                    isCurrent ? 'bg-indigo-200 text-indigo-800' : 'bg-rose-100 text-rose-700'
                  }`}>
                    {challenges.filter(c => c.status !== 'RESOLVED').length}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Active Tab View Rendering */}
      {activeProgramme ? (
        <div>
          {activeTab === 'overview' && (
            <OrgOverview
              programme={activeProgramme}
              participants={participants}
              challenges={challenges}
              analytics={analytics}
              onNavigateTab={(tab) => setActiveTab(tab)}
            />
          )}

          {activeTab === 'programmes' && (
            <OrgProgrammes
              programmes={programmes}
              activeProgrammeId={selectedProgrammeId}
              onSelectProgramme={(id) => {
                setSelectedProgrammeId(id);
                setActiveTab('overview');
              }}
              onRefresh={loadData}
            />
          )}

          {activeTab === 'participants' && (
            <OrgParticipants
              programmeId={selectedProgrammeId}
              participants={participants}
              onRefresh={loadData}
            />
          )}

          {activeTab === 'forms' && (
            <OrgFormBuilder
              forms={forms}
              programmeId={selectedProgrammeId}
              onRefresh={loadData}
            />
          )}

          {activeTab === 'monitoring' && (
            <OrgMonitoring
              programmeId={selectedProgrammeId}
              challenges={challenges}
              onRefresh={loadData}
            />
          )}

          {activeTab === 'impact' && (
            <OrgImpact programmeId={selectedProgrammeId} />
          )}

          {activeTab === 'reports' && (
            <OrgReports programme={activeProgramme} />
          )}
        </div>
      ) : (
        <div className="bg-white p-12 text-center rounded-xl border border-slate-200">
          <p className="text-sm text-slate-500">No programmes found. Please create one to begin.</p>
        </div>
      )}
    </div>
  );
};
