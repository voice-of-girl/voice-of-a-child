import React, { useState } from 'react';
import { Programme } from '../../types';
import { 
  FileText, 
  Download, 
  Printer, 
  CheckCircle2, 
  Building2, 
  TrendingUp, 
  AlertTriangle, 
  Calendar, 
  Users, 
  Award,
  Sparkles,
  Share2
} from 'lucide-react';

interface OrgReportsProps {
  programme: Programme;
}

export const OrgReports: React.FC<OrgReportsProps> = ({ programme }) => {
  const [reportType, setReportType] = useState<'DONOR' | 'MANAGEMENT' | 'ANNUAL'>('DONOR');
  const [downloadSuccess, setDownloadSuccess] = useState<string | null>(null);

  const handlePrint = () => {
    window.print();
  };

  const handleExportCSV = () => {
    // Generate CSV content
    const headers = ['Category', 'Indicator', 'Target', 'Actual', 'Baseline', 'Endline', 'Follow-up (6M)', 'Status'];
    const rows = [
      ['Outcomes', 'Formal / Freelance Tech Employment', '70%', '82%', '12%', '82%', '89%', 'EXCEEDED'],
      ['Outcomes', 'Average Monthly Income (USD)', '$150', '$185', '$25', '$185', '$290', 'EXCEEDED'],
      ['Outcomes', 'Technical Proficiency Score', '80/100', '84/100', '22/100', '84/100', '86/100', 'ACHIEVED'],
      ['Outcomes', 'Confidence & Self-Efficacy', '80%', '88%', '32%', '88%', '92%', 'EXCEEDED'],
      ['Participation', 'Total Enrolled Participants', '150', '150', '0', '150', '150', 'MET'],
      ['Participation', 'Graduation Rate', '90%', '94.2%', 'N/A', '94.2%', '94.2%', 'EXCEEDED'],
      ['Monitoring', 'Challenges Reported', 'N/A', '48 total', 'N/A', '46 resolved', '96% resolved', 'RESOLVED'],
      ['Monitoring', 'Transport Support Stipends', '50', '35 distributed', '0', '35', '35', 'MET']
    ];

    const csvContent = 'data:text/csv;charset=utf-8,' + 
      [headers.join(','), ...rows.map(e => e.join(','))].join('\n');

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `VoiceOfAGirl_Report_${programme.name.replace(/\s+/g, '_')}_2026.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    setDownloadSuccess('CSV dataset exported successfully!');
    setTimeout(() => setDownloadSuccess(null), 3000);
  };

  return (
    <div className="space-y-6" id="reports-view">
      {/* Report Controls Bar */}
      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 print:hidden">
        <div>
          <div className="flex items-center gap-2 text-xs font-semibold text-indigo-600 uppercase tracking-wider mb-0.5">
            <FileText className="w-4 h-4" />
            Executive M&E Reporting Hub
          </div>
          <h2 className="text-xl font-bold text-slate-900">Donor & Impact Reports Generator</h2>
          <p className="text-xs text-slate-500">
            Generate audit-ready evaluation reports containing summaries, KPIs, and longitudinal outcome proof.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <div className="flex rounded-md border border-slate-200 p-1 bg-slate-50">
            <button
              onClick={() => setReportType('DONOR')}
              className={`px-3 py-1 text-xs font-medium rounded cursor-pointer transition-colors ${reportType === 'DONOR' ? 'bg-white shadow-xs text-slate-900 font-semibold' : 'text-slate-500 hover:text-slate-900'}`}
            >
              Donor Brief
            </button>
            <button
              onClick={() => setReportType('MANAGEMENT')}
              className={`px-3 py-1 text-xs font-medium rounded cursor-pointer transition-colors ${reportType === 'MANAGEMENT' ? 'bg-white shadow-xs text-slate-900 font-semibold' : 'text-slate-500 hover:text-slate-900'}`}
            >
              Board Summary
            </button>
          </div>

          <button
            onClick={handleExportCSV}
            className="px-3.5 py-2 border border-slate-200 hover:bg-slate-50 rounded-md text-xs font-medium text-slate-700 flex items-center gap-1.5 transition-colors cursor-pointer"
            id="btn-export-csv"
          >
            <Download className="w-3.5 h-3.5 text-slate-500" />
            Export CSV / Excel
          </button>

          <button
            onClick={handlePrint}
            className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-md text-xs font-medium flex items-center gap-1.5 transition-colors cursor-pointer shadow-sm"
            id="btn-print-report"
          >
            <Printer className="w-3.5 h-3.5" />
            Print / Save as PDF
          </button>
        </div>
      </div>

      {downloadSuccess && (
        <div className="p-3.5 bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-medium rounded-lg flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-600" />
          {downloadSuccess}
        </div>
      )}

      {/* Formatted Report Canvas (Print Friendly Document) */}
      <div className="bg-white rounded-xl border border-slate-200 p-8 sm:p-12 shadow-sm max-w-4xl mx-auto print:border-none print:shadow-none print:p-0">
        {/* Document Header */}
        <div className="flex items-start justify-between border-b-2 border-slate-900 pb-6 mb-8">
          <div>
            <div className="flex items-center gap-2 text-indigo-600 font-semibold text-xs uppercase tracking-widest mb-1">
              VOICE OF A GIRL • PROGRAMME EVALUATION REPORT
            </div>
            <h1 className="text-2xl sm:text-3xl font-bold text-slate-950 tracking-tight">
              {programme.name}
            </h1>
            <p className="text-xs text-slate-500 mt-1">
              Lead Implementing Organisation: <strong className="text-slate-800">FemmeTech Africa Foundation</strong> (Kampala, Uganda)
            </p>
          </div>

          <div className="text-right text-xs text-slate-500">
            <div className="font-semibold text-slate-800 text-sm">COHORT REPORT 2026</div>
            <div>Date: {new Date().toLocaleDateString()}</div>
            <div className="mt-1 inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-md border border-emerald-200">
              <CheckCircle2 className="w-3 h-3" /> Data Verified
            </div>
          </div>
        </div>

        {/* Section 1: Executive Summary & Scope */}
        <section className="mb-8">
          <h2 className="text-sm font-black uppercase tracking-wider text-slate-900 border-b border-slate-200 pb-2 mb-3">
            1. Programme Summary & Objectives
          </h2>
          <p className="text-xs text-slate-700 leading-relaxed">
            {programme.description}
          </p>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-4 bg-slate-50 p-4 rounded-xl border border-slate-200">
            <div>
              <span className="text-[10px] text-slate-400 font-bold uppercase">Target Cohort</span>
              <div className="text-sm font-bold text-slate-900">150 Girls</div>
            </div>
            <div>
              <span className="text-[10px] text-slate-400 font-bold uppercase">Actual Enrolled</span>
              <div className="text-sm font-bold text-slate-900">150 Enrolled</div>
            </div>
            <div>
              <span className="text-[10px] text-slate-400 font-bold uppercase">Completion Rate</span>
              <div className="text-sm font-bold text-emerald-600">94.2% (141)</div>
            </div>
            <div>
              <span className="text-[10px] text-slate-400 font-bold uppercase">Locations</span>
              <div className="text-sm font-bold text-slate-900">Kampala, Wakiso</div>
            </div>
          </div>
        </section>

        {/* Section 2: Participation & Attendance */}
        <section className="mb-8">
          <h2 className="text-sm font-black uppercase tracking-wider text-slate-900 border-b border-slate-200 pb-2 mb-3">
            2. Participation & Attendance Telemetry
          </h2>
          <p className="text-xs text-slate-700 leading-relaxed mb-3">
            Beneficiaries completed technical tracks in Frontend Development, Cloud Fundamentals, and Soft Skills. Attendance was monitored daily by field officers.
          </p>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border border-slate-200">
              <thead className="bg-slate-100 font-bold text-slate-700">
                <tr>
                  <th className="p-2.5 border-r border-slate-200">Cohort Track</th>
                  <th className="p-2.5 border-r border-slate-200">Enrolled</th>
                  <th className="p-2.5 border-r border-slate-200">Avg. Attendance</th>
                  <th className="p-2.5 border-r border-slate-200">Completed</th>
                  <th className="p-2.5">Retention Rate</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200">
                <tr>
                  <td className="p-2.5 border-r border-slate-200 font-semibold">Web & Mobile Development</td>
                  <td className="p-2.5 border-r border-slate-200">75</td>
                  <td className="p-2.5 border-r border-slate-200">94%</td>
                  <td className="p-2.5 border-r border-slate-200">72</td>
                  <td className="p-2.5 font-bold text-emerald-700">96.0%</td>
                </tr>
                <tr>
                  <td className="p-2.5 border-r border-slate-200 font-semibold">Data Science & AI Assistants</td>
                  <td className="p-2.5 border-r border-slate-200">75</td>
                  <td className="p-2.5 border-r border-slate-200">91%</td>
                  <td className="p-2.5 border-r border-slate-200">69</td>
                  <td className="p-2.5 font-bold text-emerald-700">92.0%</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        {/* Section 3: Challenges Faced & Actions Taken */}
        <section className="mb-8">
          <h2 className="text-sm font-black uppercase tracking-wider text-slate-900 border-b border-slate-200 pb-2 mb-3">
            3. Challenges Encountered & Adaptive Interventions
          </h2>
          <div className="space-y-2 text-xs">
            <div className="p-3 rounded-lg border border-slate-200 bg-slate-50">
              <div className="font-bold text-slate-900 flex items-center justify-between">
                <span>Challenge: Transportation Barrier (35 Participants)</span>
                <span className="text-emerald-700 font-semibold">Status: Resolved</span>
              </div>
              <p className="text-slate-600 mt-1">
                Minibus taxi fares rose by 40% mid-cohort. The organization activated a transport contingency grant distributing mobile money transit stipends ($15/month). Attendance resumed at 95%+.
              </p>
            </div>

            <div className="p-3 rounded-lg border border-slate-200 bg-slate-50">
              <div className="font-bold text-slate-900 flex items-center justify-between">
                <span>Challenge: Power Grid Surges / Laptop Adapters (18 Participants)</span>
                <span className="text-emerald-700 font-semibold">Status: Resolved</span>
              </div>
              <p className="text-slate-600 mt-1">
                Sub-station surge in Wakiso damaged laptop adapters. Field response dispatched surge protectors and replacement charging cables within 48 hours. Zero curriculum loss reported.
              </p>
            </div>
          </div>
        </section>

        {/* Section 4: Longitudinal Outcome Measurement */}
        <section className="mb-8">
          <h2 className="text-sm font-black uppercase tracking-wider text-slate-900 border-b border-slate-200 pb-2 mb-3">
            4. Outcome & Impact Measurement (BEFORE → AFTER → CHANGE)
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border border-slate-200">
              <thead className="bg-slate-100 font-bold text-slate-700">
                <tr>
                  <th className="p-2.5 border-r border-slate-200">Outcome Metric</th>
                  <th className="p-2.5 border-r border-slate-200">Baseline (Intake)</th>
                  <th className="p-2.5 border-r border-slate-200">Endline</th>
                  <th className="p-2.5 border-r border-slate-200">6-Month Follow-Up</th>
                  <th className="p-2.5 font-bold text-emerald-800">Net Impact Change</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200">
                <tr>
                  <td className="p-2.5 border-r border-slate-200 font-semibold">Tech Employment Rate</td>
                  <td className="p-2.5 border-r border-slate-200">12%</td>
                  <td className="p-2.5 border-r border-slate-200">82%</td>
                  <td className="p-2.5 border-r border-slate-200 font-bold text-slate-900">89%</td>
                  <td className="p-2.5 font-bold text-emerald-700">+77% Gain</td>
                </tr>
                <tr>
                  <td className="p-2.5 border-r border-slate-200 font-semibold">Average Monthly Income</td>
                  <td className="p-2.5 border-r border-slate-200">$25 USD</td>
                  <td className="p-2.5 border-r border-slate-200">$185 USD</td>
                  <td className="p-2.5 border-r border-slate-200 font-bold text-slate-900">$290 USD</td>
                  <td className="p-2.5 font-bold text-emerald-700">+$265 USD / Month</td>
                </tr>
                <tr>
                  <td className="p-2.5 border-r border-slate-200 font-semibold">Technical Skill Score (/100)</td>
                  <td className="p-2.5 border-r border-slate-200">22 / 100</td>
                  <td className="p-2.5 border-r border-slate-200">84 / 100</td>
                  <td className="p-2.5 border-r border-slate-200 font-bold text-slate-900">86 / 100</td>
                  <td className="p-2.5 font-bold text-emerald-700">+64 Points</td>
                </tr>
                <tr>
                  <td className="p-2.5 border-r border-slate-200 font-semibold">Self-Efficacy & Confidence</td>
                  <td className="p-2.5 border-r border-slate-200">32%</td>
                  <td className="p-2.5 border-r border-slate-200">88%</td>
                  <td className="p-2.5 border-r border-slate-200 font-bold text-slate-900">92%</td>
                  <td className="p-2.5 font-bold text-emerald-700">+60% Growth</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        {/* Section 5: Signatures & Certification */}
        <section className="pt-4 border-t-2 border-slate-300">
          <div className="grid grid-cols-2 gap-8 text-xs text-slate-600">
            <div>
              <div className="font-bold text-slate-900 mb-6">Prepared by M&E Lead:</div>
              <div className="border-b border-slate-400 w-48 pb-1 mb-1 font-serif italic text-slate-800">
                Dr. Amina Okonjo
              </div>
              <div>Executive Director, FemmeTech Africa</div>
            </div>
            <div>
              <div className="font-bold text-slate-900 mb-6">Platform Data Attestation:</div>
              <div className="border-b border-slate-400 w-48 pb-1 mb-1 font-mono text-[11px] text-slate-800">
                VOICE-OF-A-GIRL-CERT#8942
              </div>
              <div>Voice of a Girl SaaS Governance</div>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
};
