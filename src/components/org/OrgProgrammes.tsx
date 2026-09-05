import React, { useState } from 'react';
import { Programme, ProgrammeStatus } from '../../types';
import { api } from '../../services/api';
import { 
  Plus, 
  Calendar, 
  MapPin, 
  Users, 
  Target, 
  FolderPlus, 
  CheckCircle2, 
  Clock, 
  ArrowRight,
  Filter,
  Sparkles
} from 'lucide-react';

interface OrgProgrammesProps {
  programmes: Programme[];
  activeProgrammeId: string;
  onSelectProgramme: (id: string) => void;
  onRefresh: () => void;
}

export const OrgProgrammes: React.FC<OrgProgrammesProps> = ({ 
  programmes, 
  activeProgrammeId, 
  onSelectProgramme,
  onRefresh 
}) => {
  const [showCreateModal, setShowCreateModal] = useState<null | 'NEW' | 'EXISTING'>(null);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState('EDUCATION');
  const [targetParticipants, setTargetParticipants] = useState<number>(100);
  const [startDate, setStartDate] = useState('2026-03-01');
  const [endDate, setEndDate] = useState('2026-09-01');
  const [locations, setLocations] = useState('Kampala, Wakiso');
  const [minAge, setMinAge] = useState<number>(18);
  const [maxAge, setMaxAge] = useState<number>(25);
  const [minEducation, setMinEducation] = useState('HIGH_SCHOOL');
  const [outcomes, setOutcomes] = useState('Tech employment, $150+ monthly earnings, digital literacy');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await api.createProgramme({
      name,
      description,
      category: category as any,
      target_participants: Number(targetParticipants),
      start_date: startDate,
      end_date: endDate,
      locations: locations.split(',').map(l => l.trim()),
      eligibility_criteria: {
        min_age: Number(minAge),
        max_age: Number(maxAge),
        min_education_level: minEducation,
        allowed_districts: locations.split(',').map(l => l.trim())
      },
      outcomes_aimed: outcomes.split(',').map(o => o.trim()),
      status: showCreateModal === 'EXISTING' ? 'ACTIVE' : 'DRAFT'
    });

    setShowCreateModal(null);
    setName('');
    setDescription('');
    onRefresh();
  };

  const handleStatusChange = async (progId: string, newStatus: ProgrammeStatus) => {
    await api.updateProgramme(progId, { status: newStatus });
    onRefresh();
  };

  const statusBadge = (s: ProgrammeStatus) => {
    switch (s) {
      case 'ACTIVE':
        return <span className="px-2.5 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">Active</span>;
      case 'DRAFT':
        return <span className="px-2.5 py-0.5 rounded-full text-[10px] font-semibold bg-slate-100 text-slate-700 border border-slate-200">Draft Setup</span>;
      case 'PAUSED':
        return <span className="px-2.5 py-0.5 rounded-full text-[10px] font-semibold bg-amber-50 text-amber-700 border border-amber-200">Paused</span>;
      case 'COMPLETED':
        return <span className="px-2.5 py-0.5 rounded-full text-[10px] font-semibold bg-indigo-50 text-indigo-700 border border-indigo-200">Completed</span>;
    }
  };

  return (
    <div className="space-y-6" id="programmes-view">
      {/* Header & Dual Track CTA */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-xs font-semibold text-indigo-600 uppercase tracking-wider mb-1">
            <Target className="w-4 h-4" />
            Programme Lifecycle Architecture
          </div>
          <h2 className="text-xl font-bold text-slate-900">Programmes Directory & Setup Tracks</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Create greenfield cohorts or register existing on-the-ground interventions to digitize M&E.
          </p>
        </div>

        <div className="flex items-center gap-2 flex-wrap">
          <button
            onClick={() => setShowCreateModal('EXISTING')}
            className="px-4 py-2 rounded-md border border-slate-200 hover:bg-slate-50 text-slate-700 text-xs font-medium transition-colors flex items-center gap-1.5 cursor-pointer shadow-sm"
            id="btn-register-existing-prog"
          >
            <FolderPlus className="w-4 h-4 text-slate-500" />
            Register Existing Programme
          </button>
          <button
            onClick={() => setShowCreateModal('NEW')}
            className="px-4 py-2 rounded-md bg-slate-900 hover:bg-slate-800 text-white text-xs font-medium transition-colors flex items-center gap-1.5 shadow-sm cursor-pointer"
            id="btn-create-new-prog"
          >
            <Plus className="w-4 h-4" />
            Create New Programme
          </button>
        </div>
      </div>

      {/* Programme Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {programmes.map((p) => {
          const isSelected = p.id === activeProgrammeId;
          return (
            <div
              key={p.id}
              className={`bg-white rounded-xl border p-6 transition-all flex flex-col justify-between ${
                isSelected ? 'border-indigo-600 ring-2 ring-indigo-100 shadow-sm' : 'border-slate-200 hover:border-slate-300 shadow-sm'
              }`}
            >
              <div>
                <div className="flex items-start justify-between gap-3 mb-2">
                  <span className="text-[10px] font-semibold px-2 py-0.5 rounded-md bg-slate-100 text-slate-700 uppercase tracking-wider">
                    {p.category}
                  </span>
                  {statusBadge(p.status)}
                </div>

                <h3 className="text-lg font-bold text-slate-900 leading-snug">{p.name}</h3>
                <p className="text-xs text-slate-600 mt-2 line-clamp-3 leading-relaxed">{p.description}</p>

                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 my-4 py-3 border-y border-slate-100 text-xs">
                  <div>
                    <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-400 block">Participants</span>
                    <div className="font-bold text-slate-900 mt-0.5 flex items-center gap-1">
                      <Users className="w-3.5 h-3.5 text-slate-400" />
                      <span>{p.target_participants} Target</span>
                    </div>
                  </div>

                  <div>
                    <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-400 block">Date Range</span>
                    <div className="font-bold text-slate-900 mt-0.5 flex items-center gap-1">
                      <Calendar className="w-3.5 h-3.5 text-slate-400" />
                      <span className="truncate">{new Date(p.start_date).toLocaleDateString()}</span>
                    </div>
                  </div>

                  <div>
                    <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-400 block">Target Age</span>
                    <div className="font-bold text-slate-900 mt-0.5">
                      {p.eligibility_criteria?.min_age || 18} - {p.eligibility_criteria?.max_age || 25} yrs
                    </div>
                  </div>
                </div>

                <div className="text-xs text-slate-600">
                  <span className="font-semibold text-slate-700">Locations: </span>
                  {(p.locations || ['Kampala']).join(', ')}
                </div>
              </div>

              <div className="mt-5 pt-3 border-t border-slate-100 flex items-center justify-between gap-2">
                <select
                  value={p.status}
                  onChange={(e) => handleStatusChange(p.id, e.target.value as ProgrammeStatus)}
                  className="text-xs font-medium border border-slate-200 rounded-md px-2.5 py-1.5 bg-white text-slate-700 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                >
                  <option value="DRAFT">Status: Draft</option>
                  <option value="ACTIVE">Status: Active</option>
                  <option value="PAUSED">Status: Paused</option>
                  <option value="COMPLETED">Status: Completed</option>
                </select>

                <button
                  onClick={() => onSelectProgramme(p.id)}
                  className={`px-3 py-1.5 rounded-md text-xs font-medium transition-colors flex items-center gap-1 cursor-pointer ${
                    isSelected ? 'bg-indigo-50 text-indigo-700 border border-indigo-200 font-semibold' : 'bg-slate-900 hover:bg-slate-800 text-white'
                  }`}
                >
                  {isSelected ? 'Active Selection' : 'Manage Cohort'}
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Modal for Creating / Registering Programme */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/50 p-4 backdrop-blur-xs">
          <div className="bg-white rounded-xl max-w-xl w-full p-6 shadow-xl border border-slate-200 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
              <div>
                <span className="text-[10px] font-semibold uppercase tracking-wider text-indigo-600">
                  {showCreateModal === 'NEW' ? 'Track A: Create New Programme' : 'Track B: Register Existing Programme'}
                </span>
                <h3 className="text-lg font-bold text-slate-900">
                  {showCreateModal === 'NEW' ? 'Set Up New Cohort & Criteria' : 'Digitize Active / Ongoing Programme'}
                </h3>
              </div>
              <button onClick={() => setShowCreateModal(null)} className="text-slate-400 hover:text-slate-600 font-bold p-1 cursor-pointer">✕</button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-3.5">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Programme Name</label>
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g. Young Women in Clean Energy Leadership 2026"
                  className="w-full text-xs p-2.5 border border-slate-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Description & Scope</label>
                <textarea
                  rows={3}
                  required
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Provide background, planned learning modules, and intended impact..."
                  className="w-full text-xs p-2.5 border border-slate-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Category</label>
                  <select
                    value={category}
                    onChange={(e) => setCategory(e.target.value)}
                    className="w-full text-xs p-2 border border-slate-200 rounded-lg bg-white focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                  >
                    <option value="EDUCATION">Education & Scholarships</option>
                    <option value="SKILLS_TRAINING">Skills & Tech Training</option>
                    <option value="MENTORSHIP">Mentorship & Leadership</option>
                    <option value="HEALTH">Health & Well-being</option>
                    <option value="ENTREPRENEURSHIP">Entrepreneurship & Grants</option>
                    <option value="LIVELIHOOD">Livelihoods & Jobs</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Target Participant Count</label>
                  <input
                    type="number"
                    required
                    value={targetParticipants}
                    onChange={(e) => setTargetParticipants(Number(e.target.value))}
                    className="w-full text-xs p-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Start Date</label>
                  <input
                    type="date"
                    required
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                    className="w-full text-xs p-2 border border-slate-200 rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">End Date</label>
                  <input
                    type="date"
                    required
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                    className="w-full text-xs p-2 border border-slate-200 rounded-lg"
                  />
                </div>
              </div>

              <div className="bg-slate-50 p-4 rounded-xl border border-slate-100 space-y-3">
                <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-400 block">
                  Eligibility & Matching Criteria
                </span>

                <div className="grid grid-cols-3 gap-2">
                  <div>
                    <label className="block text-[11px] font-medium text-slate-600 mb-1">Min Age</label>
                    <input
                      type="number"
                      value={minAge}
                      onChange={(e) => setMinAge(Number(e.target.value))}
                      className="w-full text-xs p-1.5 border border-slate-200 rounded bg-white"
                    />
                  </div>
                  <div>
                    <label className="block text-[11px] font-medium text-slate-600 mb-1">Max Age</label>
                    <input
                      type="number"
                      value={maxAge}
                      onChange={(e) => setMaxAge(Number(e.target.value))}
                      className="w-full text-xs p-1.5 border border-slate-200 rounded bg-white"
                    />
                  </div>
                  <div>
                    <label className="block text-[11px] font-medium text-slate-600 mb-1">Min Education</label>
                    <select
                      value={minEducation}
                      onChange={(e) => setMinEducation(e.target.value)}
                      className="w-full text-xs p-1.5 border border-slate-200 rounded bg-white"
                    >
                      <option value="PRIMARY">Primary</option>
                      <option value="SECONDARY">Secondary</option>
                      <option value="HIGH_SCHOOL">High School</option>
                      <option value="VOCATIONAL">Vocational</option>
                      <option value="UNDERGRADUATE">Degree</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-[11px] font-medium text-slate-600 mb-1">Eligible Districts / Locations</label>
                  <input
                    type="text"
                    value={locations}
                    onChange={(e) => setLocations(e.target.value)}
                    placeholder="Kampala, Wakiso, Mukono"
                    className="w-full text-xs p-2 border border-slate-200 rounded bg-white"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Target Outcomes & Metrics</label>
                <input
                  type="text"
                  value={outcomes}
                  onChange={(e) => setOutcomes(e.target.value)}
                  placeholder="e.g. 80% tech employment, $150 average income"
                  className="w-full text-xs p-2 border border-slate-200 rounded-lg"
                />
              </div>

              <div className="flex items-center justify-end gap-2 pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(null)}
                  className="px-3 py-2 text-xs font-medium text-slate-600 hover:bg-slate-50 rounded-md transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white text-xs font-medium rounded-md transition-colors shadow-sm"
                >
                  {showCreateModal === 'NEW' ? 'Create Programme' : 'Register Ongoing Programme'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
