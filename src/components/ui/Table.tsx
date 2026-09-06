import { ReactNode } from "react";
import { classNames } from "../../services/utils";

export function Table({ children, className }: { children: ReactNode; className?: string }) {
  return (
    <div className={classNames("w-full overflow-hidden rounded-lg border border-slate-200 bg-white", className)}>
      <table className="w-full text-sm text-left">{children}</table>
    </div>
  );
}

export function Modal({
  open,
  title,
  onClose,
  children,
  size = "md",
}: {
  open: boolean;
  title?: string;
  onClose: () => void;
  children: ReactNode;
  size?: "sm" | "md" | "lg" | "xl";
}) {
  if (!open) return null;
  const sizeClass = { sm: "max-w-sm", md: "max-w-lg", lg: "max-w-2xl", xl: "max-w-4xl" }[size];
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4" onClick={onClose}>
      <div
        className={`w-full ${sizeClass} rounded-lg bg-white p-6 shadow-xl`}
        onClick={(e) => e.stopPropagation()}
      >
        {title && <h2 className="text-lg font-bold text-slate-800 mb-4">{title}</h2>}
        {children}
      </div>
    </div>
  );
}

export function Tabs({ tabs, value, onChange }: {
  tabs: { id: string; label: string; icon?: ReactNode }[];
  value: string;
  onChange: (id: string) => void;
}) {
  return (
    <div className="flex gap-1 flex-wrap border-b border-slate-200">
      {tabs.map((t) => (
        <button
          key={t.id}
          onClick={() => onChange(t.id)}
          className={classNames(
            "flex items-center gap-2 px-4 py-2 text-sm font-medium border-b-2 transition",
            t.id === value
              ? "border-blue-600 text-blue-700"
              : "border-transparent text-slate-600 hover:text-slate-900 hover:bg-slate-50"
          )}
        >
          {t.icon} {t.label}
        </button>
      ))}
    </div>
  );
}
