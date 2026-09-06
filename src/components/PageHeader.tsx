import { ReactNode } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "./ui/Button";
import { ErrorState, EmptyState } from "./ui/Indicators";

export function PageHeader({
  title,
  subtitle,
  action,
  children,
}: {
  title: string;
  subtitle?: string;
  action?: ReactNode;
  children?: ReactNode;
}) {
  return (
    <div className="mb-6 flex flex-wrap items-end justify-between gap-4">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">{title}</h1>
        {subtitle && <p className="mt-1 text-sm text-slate-500">{subtitle}</p>}
      </div>
      <div className="flex items-center gap-3">
        {children}
        {action}
      </div>
    </div>
  );
}

export function ApiState<T>({
  status,
  error,
  onRetry,
  empty,
  children,
}: {
  status: "idle" | "loading" | "error" | "success";
  error?: string | null;
  onRetry?: () => void;
  empty?: boolean;
  children: ReactNode;
}) {
  if (status === "loading")
    return (
      <div className="py-12 text-center">
        <div className="inline-block animate-spin rounded-full border-2 border-slate-300 border-t-blue-600 h-6 w-6"></div>
        <span className="ml-2 text-slate-500">Loading…</span>
      </div>
    );
  if (status === "error") {
    return <ErrorState error={error || "Failed to load."} onRetry={onRetry} />;
  }
  if (empty) {
    return <EmptyState title="Nothing here yet." description="No records match your filter." />;
  }
  return <>{children}</>;
}

export function BackButton() {
  const navigate = useNavigate();
  return (
    <Button variant="ghost" size="sm" onClick={() => navigate(-1)} className="mb-4">
      ← Back
    </Button>
  );
}
