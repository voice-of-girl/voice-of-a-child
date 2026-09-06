import { ReactNode } from "react";
import { classNames } from "../../services/utils";

export function Badge({
  children,
  color = "slate",
  size = "sm",
}: { children: ReactNode; color?: "slate" | "blue" | "emerald" | "amber" | "red" | "purple"; size?: "sm" | "md" }) {
  const colorMap = {
    slate: "bg-slate-100 text-slate-700",
    blue: "bg-blue-100 text-blue-800",
    emerald: "bg-emerald-100 text-emerald-800",
    amber: "bg-amber-100 text-amber-800",
    red: "bg-red-100 text-red-800",
    purple: "bg-purple-100 text-purple-800",
  };
  return (
    <span
      className={classNames(
        "inline-flex items-center rounded-full font-medium",
        size === "sm" ? "px-2 py-0.5 text-xs" : "px-2.5 py-1 text-sm",
        colorMap[color]
      )}
    >
      {children}
    </span>
  );
}

export function Chip({ children, color = "slate" }: { children: ReactNode; color?: BadgeProps["color"] }) {
  return <Badge color={color}>{children}</Badge>;
}

type BadgeProps = { color?: "slate" | "blue" | "emerald" | "amber" | "red" | "purple"; children: ReactNode };

export function StatCard({
  label,
  value,
  sub,
  icon,
  trend,
}: { label: string; value: string | number; sub?: string; icon?: ReactNode; trend?: "up" | "down" | "flat" }) {
  const trendColor = trend === "up" ? "text-emerald-600" : trend === "down" ? "text-red-600" : "text-slate-500";
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4">
      <div className="flex items-center justify-between gap-2 text-slate-500">
        <span className="text-xs font-semibold uppercase">{label}</span>
        {icon}
      </div>
      <div className="mt-1 text-2xl font-bold text-slate-900">{value}</div>
      {sub && <div className="text-xs text-slate-500 mt-0.5">{sub}</div>}
      {trend && <div className={`text-xs font-medium ${trendColor} mt-1`}>{trend === "up" ? "↑" : trend === "down" ? "↓" : "→"} vs baseline</div>}
    </div>
  );
}

export function Spinner({ size = "md" }: { size?: "sm" | "md" | "lg" }) {
  const sz = size === "sm" ? "h-4 w-4" : size === "lg" ? "h-8 w-8" : "h-6 w-6";
  return <div className={`animate-spin rounded-full border-2 border-slate-300 border-t-blue-600 ${sz}`} />;
}

export function EmptyState({
  title,
  description,
  action,
}: { title: string; description?: string; action?: ReactNode }) {
  return (
    <div className="flex flex-col items-center justify-center py-14 text-center">
      <div className="text-slate-300 mb-3">{/* icon */}</div>
      <h3 className="text-lg font-semibold text-slate-800">{title}</h3>
      {description && <p className="mt-1 max-w-sm text-sm text-slate-500">{description}</p>}
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}

export function ErrorState({ error, onRetry }: { error?: string; onRetry?: () => void }) {
  return (
    <div className="rounded-lg border border-red-200 bg-red-50 p-5 text-sm text-red-800">
      {error || "Something went wrong."}
      {onRetry && (
        <button onClick={onRetry} className="ml-3 underline">
          Retry
        </button>
      )}
    </div>
  );
}
