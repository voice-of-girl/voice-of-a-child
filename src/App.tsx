import React from 'react';
import { BrowserRouter, Navigate, Route, Routes, useLocation } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Header } from './components/Header';
import { OrgWorkspace } from './components/org/OrgWorkspace';
import { FieldOfficerDashboard } from './components/field/FieldOfficerDashboard';
import { PlatformAdminDashboard } from './components/platform/PlatformAdminDashboard';
import { PublicHomePage } from './pages/PublicHomePage';
import { RegistrationPage } from './pages/RegistrationPage';
import { LoginPage } from './pages/LoginPage';
import { PublicSurveyPage } from './pages/PublicSurveyPage';

function DashboardFrame({ children, showHeader = true }: { children: React.ReactNode; showHeader?: boolean }) {
  const [showLanding, setShowLanding] = React.useState(false);
  return <div className={showHeader ? 'app-shell min-h-screen flex flex-col bg-[#F9FAFB] text-slate-900' : 'min-h-screen'}>{showHeader && <Header showLanding={showLanding} setShowLanding={setShowLanding} />}<main className={showHeader ? 'app-main flex-1' : 'flex-1'}>{children}</main>{showHeader && <footer className="bg-white border-t border-slate-200 py-4 text-xs text-slate-500"><div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between gap-3"><span className="font-bold text-slate-800">VOICE OF A GIRL</span><span className="hidden sm:inline">Participant intelligence · Programme delivery · Measurable impact</span></div></footer>}</div>;
}

function ProtectedRoute({ children, allowedRoles }: { children: React.ReactNode; allowedRoles: string[] }) {
  const { user, role } = useAuth();
  const location = useLocation();
  if (!user || !allowedRoles.includes(role)) return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  return <DashboardFrame showHeader={!allowedRoles.includes('ORGANISATION_ADMIN')}>{children}</DashboardFrame>;
}

function AppRoutes() {
  return <Routes>
    <Route path="/" element={<PublicHomePage />} />
    <Route path="/register" element={<RegistrationPage />} />
    <Route path="/login" element={<LoginPage />} />
    <Route path="/survey/:formId" element={<PublicSurveyPage />} />
    <Route path="/organisation/dashboard" element={<ProtectedRoute allowedRoles={['ORGANISATION_ADMIN']}><OrgWorkspace /></ProtectedRoute>} />
    <Route path="/organisation/programmes" element={<ProtectedRoute allowedRoles={['ORGANISATION_ADMIN']}><OrgWorkspace initialTab="programmes" /></ProtectedRoute>} />
    <Route path="/organisation/programmes/:id" element={<ProtectedRoute allowedRoles={['ORGANISATION_ADMIN']}><OrgWorkspace initialTab="programmes" /></ProtectedRoute>} />
    <Route path="/organisation/participants" element={<ProtectedRoute allowedRoles={['ORGANISATION_ADMIN']}><OrgWorkspace initialTab="participants" /></ProtectedRoute>} />
    <Route path="/organisation/surveys" element={<ProtectedRoute allowedRoles={['ORGANISATION_ADMIN']}><OrgWorkspace initialTab="analytics" /></ProtectedRoute>} />
    <Route path="/organisation/surveys/create" element={<ProtectedRoute allowedRoles={['ORGANISATION_ADMIN']}><OrgWorkspace initialTab="programmes" /></ProtectedRoute>} />
    <Route path="/organisation/surveys/:id" element={<ProtectedRoute allowedRoles={['ORGANISATION_ADMIN']}><OrgWorkspace initialTab="analytics" /></ProtectedRoute>} />
    <Route path="/organisation/monitoring" element={<ProtectedRoute allowedRoles={['ORGANISATION_ADMIN']}><OrgWorkspace initialTab="analytics" /></ProtectedRoute>} />
    <Route path="/organisation/impact" element={<ProtectedRoute allowedRoles={['ORGANISATION_ADMIN']}><OrgWorkspace initialTab="analytics" /></ProtectedRoute>} />
    <Route path="/organisation/reports" element={<ProtectedRoute allowedRoles={['ORGANISATION_ADMIN']}><OrgWorkspace initialTab="analytics" /></ProtectedRoute>} />
    <Route path="/organisation/settings" element={<ProtectedRoute allowedRoles={['ORGANISATION_ADMIN']}><OrgWorkspace initialTab="settings" /></ProtectedRoute>} />
    <Route path="/field/dashboard" element={<ProtectedRoute allowedRoles={['FIELD_OFFICER']}><FieldOfficerDashboard /></ProtectedRoute>} />
    <Route path="/admin/dashboard" element={<ProtectedRoute allowedRoles={['PLATFORM_ADMIN']}><PlatformAdminDashboard /></ProtectedRoute>} />
    <Route path="/admin/organisations" element={<ProtectedRoute allowedRoles={['PLATFORM_ADMIN']}><PlatformAdminDashboard /></ProtectedRoute>} />
    <Route path="/admin/participants" element={<ProtectedRoute allowedRoles={['PLATFORM_ADMIN']}><PlatformAdminDashboard /></ProtectedRoute>} />
    <Route path="/admin/programmes" element={<ProtectedRoute allowedRoles={['PLATFORM_ADMIN']}><PlatformAdminDashboard /></ProtectedRoute>} />
    <Route path="/admin/surveys" element={<ProtectedRoute allowedRoles={['PLATFORM_ADMIN']}><PlatformAdminDashboard /></ProtectedRoute>} />
    <Route path="/admin/impact-projects" element={<ProtectedRoute allowedRoles={['PLATFORM_ADMIN']}><PlatformAdminDashboard /></ProtectedRoute>} />
    <Route path="/admin/verification" element={<ProtectedRoute allowedRoles={['PLATFORM_ADMIN']}><PlatformAdminDashboard /></ProtectedRoute>} />
    <Route path="/admin/analytics" element={<ProtectedRoute allowedRoles={['PLATFORM_ADMIN']}><PlatformAdminDashboard /></ProtectedRoute>} />
    <Route path="/admin/reports" element={<ProtectedRoute allowedRoles={['PLATFORM_ADMIN']}><PlatformAdminDashboard /></ProtectedRoute>} />
    <Route path="/admin/settings" element={<ProtectedRoute allowedRoles={['PLATFORM_ADMIN']}><PlatformAdminDashboard /></ProtectedRoute>} />
    <Route path="*" element={<Navigate to="/" replace />} />
  </Routes>;
}

export default function App() {
  const queryClient = new QueryClient();
  return <BrowserRouter><QueryClientProvider client={queryClient}><AuthProvider><AppRoutes /></AuthProvider></QueryClientProvider></BrowserRouter>;
}
