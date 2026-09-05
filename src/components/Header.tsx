import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { UserRole } from '../types';
import { 
  Building2, 
  GraduationCap, 
  ClipboardCheck, 
  ShieldCheck, 
  Bell, 
  Sparkles, 
  ArrowRight,
  Globe,
  CheckCircle2,
  ChevronDown,
  LogOut
} from 'lucide-react';

interface HeaderProps {
  showLanding: boolean;
  setShowLanding: (show: boolean) => void;
}

export const Header: React.FC<HeaderProps> = ({ showLanding, setShowLanding }) => {
  const { user, role, switchRole, organisation, notificationsCount, logout } = useAuth();
  const [showRoleMenu, setShowRoleMenu] = useState(false);
  const [showNotifMenu, setShowNotifMenu] = useState(false);

  const roleConfig: Record<UserRole, { label: string; icon: any; color: string; desc: string }> = {
    ORGANISATION_ADMIN: {
      label: "Organisation Admin",
      icon: Building2,
      color: "bg-indigo-50 text-indigo-700 border-indigo-200",
      desc: "FemmeTech Africa Foundation"
    },
    BENEFICIARY: {
      label: "Beneficiary / Girl",
      icon: GraduationCap,
      color: "bg-slate-100 text-slate-800 border-slate-200",
      desc: "Fatima Zara (Scholarship Participant)"
    },
    FIELD_OFFICER: {
      label: "Field Officer",
      icon: ClipboardCheck,
      color: "bg-blue-50 text-blue-700 border-blue-200",
      desc: "Sarah Kibuuka (Central Region)"
    },
    PLATFORM_ADMIN: {
      label: "Platform Admin",
      icon: ShieldCheck,
      color: "bg-slate-900 text-white border-slate-800",
      desc: "Voice of a Girl Governance"
    }
  };

  const CurrentIcon = roleConfig[role].icon;

  return (
    <header className="sticky top-0 z-40 bg-white border-b border-slate-200" id="app-header">
      {/* Top Banner: Value Chain Quick Pipeline */}
      <div className="bg-slate-900 text-slate-200 px-4 py-1.5 text-xs flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2 font-medium overflow-x-auto py-0.5">
          <span className="text-indigo-400 font-semibold tracking-wider uppercase text-[10px]">Value Chain:</span>
          <span className="text-slate-100 font-semibold">REACH</span>
          <ArrowRight className="w-3 h-3 text-slate-500 shrink-0" />
          <span className="text-slate-100 font-semibold">MANAGE</span>
          <ArrowRight className="w-3 h-3 text-slate-500 shrink-0" />
          <span className="text-slate-100 font-semibold">COLLECT</span>
          <ArrowRight className="w-3 h-3 text-slate-500 shrink-0" />
          <span className="text-slate-100 font-semibold">MONITOR</span>
          <ArrowRight className="w-3 h-3 text-slate-500 shrink-0" />
          <span className="text-slate-100 font-semibold">RESPOND</span>
          <ArrowRight className="w-3 h-3 text-slate-500 shrink-0" />
          <span className="text-slate-100 font-semibold">MEASURE</span>
          <ArrowRight className="w-3 h-3 text-slate-500 shrink-0" />
          <span className="text-indigo-300 font-bold">REPORT</span>
        </div>
        
        <div className="flex items-center gap-3 text-slate-400 text-xs">
          <button 
            onClick={() => setShowLanding(!showLanding)}
            className="text-slate-300 hover:text-white transition-colors flex items-center gap-1.5 font-medium cursor-pointer"
            id="toggle-landing-btn"
          >
            <Globe className="w-3.5 h-3.5 text-indigo-400" />
            {showLanding ? "Go to Dashboard" : "Public Landing Page"}
          </button>
          <span className="hidden sm:inline text-slate-700">|</span>
          <span className="hidden sm:inline text-[11px] text-slate-400">B2B SaaS Platform</span>
        </div>
      </div>

      {/* Main Header Bar */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-4">
        {/* Brand with Clean Minimalism mark */}
        <div className="flex items-center gap-3 cursor-pointer" onClick={() => setShowLanding(false)}>
          <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center text-white font-bold text-xs shadow-sm">
            VG
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-slate-900 tracking-tight text-lg">
                VOICE OF A GIRL
              </span>
              <span className="hidden md:inline-flex items-center px-2 py-0.5 rounded-md text-[10px] font-medium bg-indigo-50 text-indigo-700 border border-indigo-200">
                MVP
              </span>
            </div>
            <p className="text-xs text-slate-500 hidden sm:block">
              Beneficiary Management & Outcome Measurement
            </p>
          </div>
        </div>

        {/* Right Section: Persona Role Switcher & User Details */}
        <div className="flex items-center gap-2 sm:gap-3">
          {/* Quick Role Switcher Dropdown */}
          <div className="relative">
            <button
              onClick={() => setShowRoleMenu(!showRoleMenu)}
              className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-semibold border transition-colors cursor-pointer ${roleConfig[role].color}`}
              id="role-switcher-dropdown"
              title="Switch user role persona to test all system features"
            >
              <CurrentIcon className="w-4 h-4" />
              <div className="text-left hidden sm:block">
                <div className="text-[10px] text-slate-500 font-normal">Active Role</div>
                <div className="font-bold leading-tight">{roleConfig[role].label}</div>
              </div>
              <ChevronDown className="w-3.5 h-3.5 ml-1 text-slate-500" />
            </button>

            {showRoleMenu && (
              <div className="absolute right-0 mt-2 w-72 bg-white rounded-xl shadow-lg border border-slate-200 py-2 z-50">
                <div className="px-3 py-1.5 text-[10px] font-semibold text-slate-400 uppercase tracking-wider border-b border-slate-100">
                  Switch Active Role Persona
                </div>
                {(Object.keys(roleConfig) as UserRole[]).map((r) => {
                  const Icon = roleConfig[r].icon;
                  const isSelected = role === r;
                  return (
                    <button
                      key={r}
                      onClick={() => {
                        switchRole(r);
                        setShowRoleMenu(false);
                        setShowLanding(false);
                      }}
                      className={`w-full text-left px-3 py-2.5 flex items-start gap-2.5 hover:bg-slate-50 transition-colors cursor-pointer ${
                        isSelected ? 'bg-indigo-50/80 text-indigo-950 font-medium' : 'text-slate-700'
                      }`}
                    >
                      <div className={`p-1.5 rounded-md mt-0.5 ${isSelected ? 'bg-indigo-100 text-indigo-700' : 'bg-slate-100 text-slate-600'}`}>
                        <Icon className="w-4 h-4" />
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center justify-between text-xs font-semibold">
                          <span>{roleConfig[r].label}</span>
                          {isSelected && <CheckCircle2 className="w-3.5 h-3.5 text-indigo-600" />}
                        </div>
                        <div className="text-[11px] text-slate-500 mt-0.5">
                          {roleConfig[r].desc}
                        </div>
                      </div>
                    </button>
                  );
                })}
              </div>
            )}
          </div>

          {/* Notifications Bell */}
          <div className="relative">
            <button
              onClick={() => setShowNotifMenu(!showNotifMenu)}
              className="p-2 text-slate-600 hover:text-slate-900 hover:bg-slate-50 rounded-lg transition-colors relative cursor-pointer border border-slate-200"
              id="notifications-bell"
              title="Notifications"
            >
              <Bell className="w-4 h-4" />
              {notificationsCount > 0 && (
                <span className="absolute top-1 right-1 w-2 h-2 bg-indigo-600 rounded-full" />
              )}
            </button>

            {showNotifMenu && (
              <div className="absolute right-0 mt-2 w-80 bg-white rounded-xl shadow-lg border border-slate-200 py-2 z-50">
                <div className="px-4 py-2 border-b border-slate-100 flex items-center justify-between">
                  <span className="text-xs font-bold text-slate-800">Notifications</span>
                  <span className="text-[10px] text-indigo-700 font-semibold bg-indigo-50 border border-indigo-100 px-2 py-0.5 rounded-full">
                    {notificationsCount} New
                  </span>
                </div>
                <div className="divide-y divide-slate-100 max-h-72 overflow-y-auto">
                  <div className="p-3 text-xs hover:bg-slate-50 transition-colors">
                    <div className="font-semibold text-slate-800">Bi-Weekly Monitoring Survey</div>
                    <p className="text-slate-500 mt-0.5">Response deadline set for April 15, 2026.</p>
                    <span className="text-[10px] text-slate-400 mt-1 block">1 hour ago</span>
                  </div>
                  <div className="p-3 text-xs hover:bg-slate-50 transition-colors">
                    <div className="font-semibold text-slate-800 flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-full bg-rose-500 shrink-0"></span>
                      <span>35 Transport Issues Reported</span>
                    </div>
                    <p className="text-slate-500 mt-0.5">High alert cluster detected along Northern District.</p>
                    <span className="text-[10px] text-slate-400 mt-1 block">Yesterday</span>
                  </div>
                  <div className="p-3 text-xs hover:bg-slate-50 transition-colors">
                    <div className="font-semibold text-slate-800">Scholarship Cohort Verified</div>
                    <p className="text-slate-500 mt-0.5">32 baseline submissions processed successfully.</p>
                    <span className="text-[10px] text-slate-400 mt-1 block">2 days ago</span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* User Info Capsule */}
          <div className="hidden lg:flex items-center gap-2 pl-2 border-l border-slate-200 text-xs">
            <div className="w-8 h-8 rounded-full bg-slate-100 border border-slate-200 flex items-center justify-center font-bold text-slate-700">
              {user?.first_name?.[0] || 'U'}
            </div>
            <div className="leading-tight">
              <div className="font-semibold text-slate-900">{user?.first_name} {user?.last_name}</div>
              <div className="text-[11px] text-slate-500 truncate max-w-[140px]">{user?.email}</div>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};
