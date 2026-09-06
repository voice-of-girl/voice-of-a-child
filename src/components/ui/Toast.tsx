import { ReactNode, useEffect, useState } from "react";
import { classNames } from "../../services/utils";

export function ToastContainer() {
  const [toasts, setToasts] = useState<{ id: number; msg: string; type: "info" | "success" | "error" }[]>([]);
  useEffect(() => {
    (window as unknown as { voiceToast?: (msg: string, type?: "info" | "success" | "error") => void }).voiceToast = (
      msg: string, type: "info" | "success" | "error" = "info"
    ) => {
      const id = Date.now();
      setToasts((t) => [...t, { id, msg, type }]);
      setTimeout(() => setToasts((t) => t.filter((x) => x.id !== id)), 3600);
    };
  }, []);
  return (
    <div className="fixed bottom-left ml-6 mb-6 z-[100] flex flex-col gap-2">
      {toasts.map((t) => (
        <div
          key={t.id}
          className={classNames(
            "max-w-sm rounded-md border px-4 py-3 text-sm shadow-lg",
            t.type === "success"
              ? "border-emerald-200 bg-emerald-50 text-emerald-800"
              : t.type === "error"
              ? "border-red-200 bg-red-50 text-red-800"
              : "border-slate-200 bg-slate-50 text-slate-800"
          )}
        >
          {t.msg}
        </div>
      ))}
    </div>
  );
}

export function toast(msg: string, type: "info" | "success" | "error" = "info") {
  (window as unknown as { voiceToast?: (msg: string, type?: "info" | "success" | "error") => void }).voiceToast?.(msg, type);
}
