import React from "react";
import { BrowserRouter, Navigate, Route, Routes, useLocation } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AuthProvider, useAuth } from "./context/AuthContext";
import { ToastContainer } from "./components/ui/Toast";

import { PublicHomePage } from "./pages/PublicHomePage";
import { LoginPage } from "./pages/LoginPage";
import { PublicSurveyPage } from "./pages/PublicSurveyPage";

import { WorkspaceDashboard } from "./pages/WorkspaceDashboard";
import { ProgrammesPage } from "./pages/ProgrammesPage";
import { ProgrammeFormPage } from "./pages/ProgrammeFormPage";
import { ProgrammeDetailPage } from "./pages/ProgrammeDetailPage";
import { ParticipantsPage } from "./pages/ParticipantsPage";
import { ParticipantFormPage } from "./pages/ParticipantFormPage";
import { SurveysPage } from "./pages/SurveysPage";
import { SurveyBuilderPage } from "./pages/SurveyBuilderPage";
import { SurveyDetailPage } from "./pages/SurveyDetailPage";
import { ResponsesPage } from "./pages/ResponsesPage";
import { MonitoringPage } from "./pages/MonitoringPage";
import { ImpactPage } from "./pages/ImpactPage";
import { ReportsPage } from "./pages/ReportsPage";
import { ReportDetailPage } from "./pages/ReportDetailPage";
import { ImpactProjectsPage } from "./pages/ImpactProjectsPage";
import { AdminPage } from "./pages/AdminPage";

import { AppShell } from "./components/layout/AppShell";

const queryClient = new QueryClient();

function RequireAuth({ allowedRoles }: { allowedRoles?: string[] }) {
  const { user, role, isLoading } = useAuth();
  const location = useLocation();
  if (isLoading) return <div className="p-8">Loading…</div>;
  if (!user) return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  if (allowedRoles && !allowedRoles.includes(role))
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  return null;
}

function Protected({ children, allowedRoles }: { children: React.ReactNode; allowedRoles?: string[] }) {
  const unauth = RequireAuth(allowedRoles ? { allowedRoles } : {});
  if (unauth) return unauth;
  return <AppShell>{children}</AppShell>;
}

function AdminProtected({ children }: { children: React.ReactNode }) {
  const unauth = RequireAuth({ allowedRoles: ["PLATFORM_ADMIN"] });
  if (unauth) return unauth;
  return children;
}

function AppRoutes() {
  return (
    <Routes>
      {/* Public */}
      <Route path="/" element={<PublicHomePage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/survey/:token" element={<PublicSurveyPage />} />

      {/* Workspace (organisation-scoped) */}
      <Route path="/workspace" element={<Protected><WorkspaceDashboard /></Protected>} />
      <Route path="/workspace/programmes" element={<Protected><ProgrammesPage /></Protected>} />
      <Route path="/workspace/programmes/create" element={<Protected><ProgrammeFormPage /></Protected>} />
      <Route path="/workspace/programmes/:id/edit" element={<Protected><ProgrammeFormPage /></Protected>} />
      <Route path="/workspace/programmes/:id" element={<Protected><ProgrammeDetailPage /></Protected>} />
      <Route path="/workspace/participants" element={<Protected><ParticipantsPage /></Protected>} />
      <Route path="/workspace/participants/create" element={<Protected><ParticipantFormPage /></Protected>} />
      <Route path="/workspace/surveys" element={<Protected><SurveysPage /></Protected>} />
      <Route path="/workspace/surveys/create" element={<Protected><SurveyBuilderPage /></Protected>} />
      <Route path="/workspace/surveys/:id/edit" element={<Protected><SurveyBuilderPage /></Protected>} />
      <Route path="/workspace/surveys/:id" element={<Protected><SurveyDetailPage /></Protected>} />
      <Route path="/workspace/surveys/:id/responses" element={<Protected><ResponsesPage /></Protected>} />
      <Route path="/workspace/monitoring" element={<Protected><MonitoringPage /></Protected>} />
      <Route path="/workspace/impact" element={<Protected><ImpactPage /></Protected>} />
      <Route path="/workspace/reports" element={<Protected><ReportsPage /></Protected>} />
      <Route path="/workspace/reports/generate" element={<Protected><ReportDetailPage createOnly /></Protected>} />
      <Route path="/workspace/reports/:id" element={<Protected><ReportDetailPage /></Protected>} />
      <Route path="/workspace/projects" element={<Protected><ImpactProjectsPage /></Protected>} />

      {/* Platform admin */}
      <Route path="/admin/*" element={<AdminProtected><AdminPage /></AdminProtected>} />

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <BrowserRouter>
          <AppRoutes />
        </BrowserRouter>
      </AuthProvider>
    </QueryClientProvider>
  );
}
