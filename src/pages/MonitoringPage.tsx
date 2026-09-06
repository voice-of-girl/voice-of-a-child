import { useState } from "react";
import { useList } from "../hooks/useApi";
import type { Challenge, FeedbackItem, SupportRequest } from "../types";
import { Button } from "../components/ui/Button";
import { Badge, Spinner } from "../components/ui/Indicators";
import { PageHeader } from "../components/PageHeader";
import { LogForm } from "../components/monitoring/LogForm";

type Tab = "challenges" | "feedback" | "support";

export function MonitoringPage() {
  const [tab, setTab] = useState<Tab>("challenges");
  const [show, setShow] = useState(false);
  const tabs: { id: Tab; label: string }[] = [
    { id: "challenges", label: "Challenges" },
    { id: "feedback", label: "Feedback" },
    { id: "support", label: "Support" },
  ];
  return (
    <div>
      <PageHeader title="Monitoring" subtitle="Challenges, feedback and support requests">
        <Button variant="primary" onClick={() => setShow(true)}>+ Log item</Button>
      </PageHeader>
      <div className="flex gap-1 flex-wrap border-b border-slate-200 mb-4">
        {tabs.map((t) => (
          <button key={t.id} onClick={() => setTab(t.id)}
            className={`px-4 py-2 text-sm font-medium border-b-2 ${tab === t.id ? "border-blue-600 text-blue-700" : "border-transparent text-slate-600 hover:text-slate-900"}`}>
            {t.label}
          </button>
        ))}
      </div>
      <LogForm open={show} onClose={() => setShow(false)} />
      {tab === "challenges" && <ChallengesTab />}
      {tab === "feedback" && <FeedbackTab />}
      {tab === "support" && <SupportTab />}
    </div>
  );
}

function ChallengesTab() {
  const { data, status } = useList<Challenge>("/monitoring/challenges/");
  if (status === "loading") return <Spinner size="lg" />;
  return (
    <div className="overflow-x-auto rounded-lg border border-slate-200 bg-white">
      <table className="w-full text-sm text-left">
        <thead className="bg-slate-50 text-xs font-medium uppercase text-slate-500">
          <tr><th className="px-4 py-2">Title</th><th className="px-4 py-2">Category</th><th className="px-4 py-2">Priority</th><th className="px-4 py-2">Status</th><th className="px-4 py-2">Programme</th></tr>
        </thead>
        <tbody>
          {data.map((c) => (
            <tr key={c.id} className="border-t border-slate-100">
              <td className="px-4 py-2 font-medium text-slate-900">{c.title}</td>
              <td className="px-4 py-2">{c.category}</td>
              <td className="px-4 py-2"><Badge color={c.priority === "CRITICAL" ? "red" : c.priority === "HIGH" ? "amber" : "slate"}>{c.priority}</Badge></td>
              <td className="px-4 py-2"><Badge color={c.status === "RESOLVED" ? "emerald" : c.status === "IN_PROGRESS" ? "blue" : "slate"}>{c.status}</Badge></td>
              <td className="px-4 py-2">{c.programme_name || "—"}</td>
            </tr>
          ))}
          {data.length === 0 && <tr><td colSpan={5} className="px-4 py-6 text-center text-slate-500">No challenges logged.</td></tr>}
        </tbody>
      </table>
    </div>
  );
}

function FeedbackTab() {
  const { data, status } = useList<FeedbackItem>("/monitoring/feedback/");
  if (status === "loading") return <Spinner size="lg" />;
  return (
    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
      {data.map((f) => (
        <div key={f.id} className="rounded-lg border border-slate-200 bg-white p-4">
          <div className="flex items-center justify-between mb-2">
            <Badge color="blue">{f.category}</Badge>
            <Badge color={f.status === "ACTIONED" ? "emerald" : f.status === "REVIEWED" ? "amber" : "slate"}>{f.status}</Badge>
          </div>
          <p className="text-sm text-slate-700">{f.message}</p>
          <p className="mt-2 text-xs text-slate-500">{f.programme_name || "No programme"}</p>
        </div>
      ))}
      {data.length === 0 && <p className="text-slate-500 col-span-full">No feedback yet.</p>}
    </div>
  );
}

function SupportTab() {
  const { data, status } = useList<SupportRequest>("/monitoring/support-requests/");
  if (status === "loading") return <Spinner size="lg" />;
  return (
    <div className="overflow-x-auto rounded-lg border border-slate-200 bg-white">
      <table className="w-full text-sm text-left">
        <thead className="bg-slate-50 text-xs font-medium uppercase text-slate-500">
          <tr><th className="px-4 py-2">Description</th><th className="px-4 py-2">Category</th><th className="px-4 py-2">Status</th><th className="px-4 py-2">Programme</th></tr>
        </thead>
        <tbody>
          {data.map((s) => (
            <tr key={s.id} className="border-t border-slate-100">
              <td className="px-4 py-2 font-medium text-slate-900">{s.description}</td>
              <td className="px-4 py-2">{s.category}</td>
              <td className="px-4 py-2"><Badge color={s.status === "RESOLVED" || s.status === "CLOSED" ? "emerald" : s.status === "IN_PROGRESS" ? "blue" : "slate"}>{s.status}</Badge></td>
              <td className="px-4 py-2">{s.programme_name || "—"}</td>
            </tr>
          ))}
          {data.length === 0 && <tr><td colSpan={4} className="px-4 py-6 text-center text-slate-500">No support requests.</td></tr>}
        </tbody>
      </table>
    </div>
  );
}
