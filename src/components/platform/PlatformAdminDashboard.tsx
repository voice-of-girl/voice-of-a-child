import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { Organisation } from '../../types';
import { api } from '../../services/api';
import { 
  ShieldCheck, 
  Building2, 
  Users, 
  CheckCircle2, 
  XCircle, 
  TrendingUp, 
  Globe, 
  Activity,
  Search,
  Filter,
  ArrowUpRight
} from 'lucide-react';

export const PlatformAdminDashboard: React.FC = () => {
  const { user } = useAuth();
  const [organisations, setOrganisations] = useState<Organisation[]>([]);
  const [filterStatus, setFilterStatus] = useState<string>('ALL');
  const [loading, setLoading] = useState(false);
  const [interestSubmissions, setInterestSubmissions] = useState<any[]>([]);

  const loadOrgs = async () => {
    try {
      const orgs = await api.getOrganisations();
      setOrganisations(orgs);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    loadOrgs();
    api.getBeneficiaryInterests().then(setInterestSubmissions).catch(() => setInterestSubmissions([]));
  }, []);

  const handleVerify = async (orgId: string, status: string) => {
    await api.verifyOrganisation(orgId, status);
    loadOrgs();
  };

  const filteredOrgs = organisations.filter(o => {
    if (filterStatus !== 'ALL' && o.verification_status !== filterStatus) return false;
    return true;
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6" id="platform-admin-dashboard">
      {/* Governance Banner */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <span className="px-2.5 py-0.5 rounded-md text-[10px] font-semibold bg-indigo-50 text-indigo-700 border border-indigo-100 uppercase tracking-wide">
              Platform Administration
            </span>
            <span className="text-xs text-slate-400">Voice of a Girl Global Network</span>
          </div>
          <h1 className="text-xl sm:text-2xl font-bold text-slate-900">
            System Governance & Organisation Verification
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Approve implementing partners, audit data integrity, and inspect aggregate impact telemetry.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="px-3 py-1.5 rounded-md bg-slate-50 text-xs font-semibold text-slate-700 border border-slate-200 flex items-center gap-1.5">
            <ShieldCheck className="w-4 h-4 text-indigo-600" />
            Security & Tenant Isolation Enforced
          </span>
        </div>
      </div>

      {/* Aggregate Global Analytics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <span className="text-xs font-medium text-slate-500">Total Girls Reached</span>
          <div className="text-2xl font-bold text-slate-900 mt-1">1,480</div>
          <div className="text-[11px] text-emerald-600 font-medium mt-1 flex items-center gap-1">
            <ArrowUpRight className="w-3.5 h-3.5" /> +24% Year over Year
          </div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <span className="text-xs font-medium text-slate-500">Active Programmes</span>
          <div className="text-2xl font-bold text-slate-900 mt-1">18</div>
          <div className="text-[11px] text-slate-500 mt-1">Across 6 African districts</div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <span className="text-xs font-medium text-slate-500">Challenge Resolution Rate</span>
          <div className="text-2xl font-bold text-slate-900 mt-1">96.4%</div>
          <div className="text-[11px] text-slate-500 mt-1">Average 48hr response time</div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <span className="text-xs font-medium text-slate-500">Average Income Multiplier</span>
          <div className="text-2xl font-bold text-slate-900 mt-1">11.6x</div>
          <div className="text-[11px] text-slate-500 mt-1">Baseline $25 → Endline $290</div>
        </div>
      </div>

      {/* Organisation Approval Pipeline */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-100">
          <div>
            <h2 className="text-base font-bold text-slate-900">Implementing Organisation Verification Pipeline</h2>
            <p className="text-xs text-slate-500">
              Review institutional registration documents before provisioning SaaS tenant workspaces.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="text-xs border border-slate-200 rounded-lg px-3 py-1.5 bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 cursor-pointer"
            >
              <option value="ALL">All Verification Statuses</option>
              <option value="VERIFIED">Verified</option>
              <option value="PENDING">Pending Review</option>
              <option value="REJECTED">Rejected</option>
            </select>
          </div>
        </div>

        <div className="overflow-x-auto">
          {filteredOrgs.length === 0 ? (
            <div className="p-10 text-center border border-dashed border-slate-300 rounded-lg">
              <Building2 className="w-9 h-9 mx-auto text-slate-300" />
              <h3 className="mt-3 text-sm font-bold text-slate-800">No organisations match this filter</h3>
              <p className="mt-1 text-xs text-slate-500">Try another verification status or check back when a partner submits registration.</p>
            </div>
          ) : <table className="w-full text-left text-xs text-slate-700">
            <thead className="bg-slate-50 text-slate-500 font-semibold border-y border-slate-200">
              <tr>
                <th className="py-3 px-3">Organisation Name</th>
                <th className="py-3 px-3">Type</th>
                <th className="py-3 px-3">Location</th>
                <th className="py-3 px-3">Contact</th>
                <th className="py-3 px-3">Status</th>
                <th className="py-3 px-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filteredOrgs.map((org) => (
                <tr key={org.id} className="hover:bg-slate-50/70 transition-colors">
                  <td className="py-3 px-3">
                    <div className="font-semibold text-slate-900">{org.name}</div>
                    <div className="text-[11px] text-slate-500 line-clamp-1">{org.description}</div>
                  </td>
                  <td className="py-3 px-3">
                    <span className="px-2 py-0.5 rounded-md bg-slate-100 font-medium text-[11px] text-slate-700 border border-slate-200">
                      {org.organisation_type}
                    </span>
                  </td>
                  <td className="py-3 px-3">
                    <div>{org.district}, {org.country}</div>
                    <div className="text-[11px] text-slate-400">{org.address}</div>
                  </td>
                  <td className="py-3 px-3">
                    <div>{org.email}</div>
                    <div className="text-[11px] text-slate-400">{org.phone_number}</div>
                  </td>
                  <td className="py-3 px-3">
                    <span className={`px-2.5 py-0.5 rounded-md text-[11px] font-semibold ${
                      org.verification_status === 'VERIFIED' ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' :
                      org.verification_status === 'REJECTED' ? 'bg-red-50 text-red-700 border border-red-200' :
                      'bg-amber-50 text-amber-700 border border-amber-200'
                    }`}>
                      {org.verification_status}
                    </span>
                  </td>
                  <td className="py-3 px-3 text-right space-x-1.5 whitespace-nowrap">
                    {org.verification_status !== 'VERIFIED' && (
                      <button
                        onClick={() => handleVerify(org.id, 'VERIFIED')}
                        className="px-3 py-1.5 bg-slate-900 hover:bg-slate-800 text-white font-medium rounded-md text-xs transition-colors cursor-pointer shadow-xs"
                      >
                        Approve & Verify
                      </button>
                    )}
                    {org.verification_status !== 'REJECTED' && (
                      <button
                        onClick={() => handleVerify(org.id, 'REJECTED')}
                        className="px-3 py-1.5 border border-slate-200 text-slate-700 hover:bg-slate-100 font-medium rounded-md text-xs transition-colors cursor-pointer"
                      >
                        Reject
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>}
        </div>
      </div>

      {/* Public applicant intake */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
        <div className="flex items-center justify-between gap-3 mb-4 pb-3 border-b border-slate-100">
          <div>
            <h2 className="text-base font-bold text-slate-900">New opportunity enquiries</h2>
            <p className="text-xs text-slate-500">Public submissions awaiting review before a managed profile is created.</p>
          </div>
          <span className="px-2.5 py-1 rounded-full bg-blue-50 border border-blue-200 text-blue-700 text-[11px] font-bold">{interestSubmissions.length} New</span>
        </div>
        {interestSubmissions.length === 0 ? (
          <div className="py-8 text-center border border-dashed border-slate-300 rounded-lg">
            <Users className="w-8 h-8 mx-auto text-slate-300" />
            <p className="mt-2 text-xs text-slate-500">No new public enquiries yet.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-700">
              <thead className="bg-slate-50 text-slate-500 font-semibold border-y border-slate-200">
                <tr><th className="py-2.5 px-3">Applicant</th><th className="py-2.5 px-3">Contact</th><th className="py-2.5 px-3">Location</th><th className="py-2.5 px-3">Interest</th><th className="py-2.5 px-3">Received</th></tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {interestSubmissions.map((submission) => (
                  <tr key={submission.id} className="hover:bg-slate-50/70">
                    <td className="py-3 px-3"><div className="font-semibold text-slate-900">{submission.first_name} {submission.last_name}</div><div className="text-[11px] text-slate-500">{submission.education_level}</div></td>
                    <td className="py-3 px-3"><div>{submission.email}</div><div className="text-[11px] text-slate-400">{submission.phone_number}</div></td>
                    <td className="py-3 px-3">{submission.district}</td>
                    <td className="py-3 px-3">{submission.interest_area}</td>
                    <td className="py-3 px-3 text-slate-500">{new Date(submission.submitted_at).toLocaleDateString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
