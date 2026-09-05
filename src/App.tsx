/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Header } from './components/Header';
import { LandingPage } from './components/LandingPage';
import { OrgDashboard } from './components/org/OrgDashboard';
import { BeneficiaryDashboard } from './components/beneficiary/BeneficiaryDashboard';
import { FieldOfficerDashboard } from './components/field/FieldOfficerDashboard';
import { PlatformAdminDashboard } from './components/platform/PlatformAdminDashboard';

const MainAppContent: React.FC = () => {
  const { role } = useAuth();
  const [showLanding, setShowLanding] = useState<boolean>(false);

  if (showLanding) {
    return (
      <div className="min-h-screen flex flex-col bg-[#F9FAFB]">
        <Header showLanding={showLanding} setShowLanding={setShowLanding} />
        <LandingPage onEnterApp={() => setShowLanding(false)} />
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col bg-[#F9FAFB] text-slate-900 font-sans">
      <Header showLanding={showLanding} setShowLanding={setShowLanding} />
      
      <main className="flex-1">
        {role === 'ORGANISATION_ADMIN' && <OrgDashboard />}
        {role === 'BENEFICIARY' && <BeneficiaryDashboard />}
        {role === 'FIELD_OFFICER' && <FieldOfficerDashboard />}
        {role === 'PLATFORM_ADMIN' && <PlatformAdminDashboard />}
      </main>

      {/* Global Status Footer */}
      <footer className="bg-white border-t border-slate-200 py-4 text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <span className="font-bold text-slate-800">VOICE OF A GIRL</span>
            <span className="text-slate-300">•</span>
            <span>B2B Beneficiary Management & Impact Measurement</span>
          </div>
          <div className="flex items-center gap-4 text-[11px] text-slate-400">
            <span>Modular Backend</span>
            <span className="text-slate-300">•</span>
            <span>Rule-Based Matching Active</span>
            <span className="text-slate-300">•</span>
            <button 
              onClick={() => setShowLanding(true)}
              className="text-indigo-600 font-semibold hover:text-indigo-700 cursor-pointer transition-colors"
            >
              Show Public Landing Page
            </button>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default function App() {
  return (
    <AuthProvider>
      <MainAppContent />
    </AuthProvider>
  );
}
