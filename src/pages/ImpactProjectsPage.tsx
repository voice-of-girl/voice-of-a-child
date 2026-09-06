import { useState } from "react";
import { Link } from "react-router-dom";
import { useList } from "../hooks/useApi";
import type { ImpactProject } from "../types";
import { Button } from "../components/ui/Button";
import { Badge, Spinner } from "../components/ui/Indicators";
import { Modal } from "../components/ui/Table";
import { Input, Textarea, Field } from "../components/ui/Indicator";
import { PageHeader } from "../components/PageHeader";
import { toast } from "../components/ui/Toast";
import { apiPost, apiError } from "../services/api";

export function ImpactProjectsPage() {
  const { data: list, status, refetch, count } = useList<ImpactProject>("/impact-projects/");
  const [show, setShow] = useState(false);
  return (
    <div>
      <PageHeader title="Impact projects" subtitle={`${count} standalone project${count === 1 ? "" : "s"}`}>
        <Button variant="primary" onClick={() => setShow(true)}>+ New project</Button>
      </PageHeader>
      <ProjectForm open={show} onClose={() => setShow(false)} onSaved={refetch} />
      {status === "loading" && <Spinner size="lg" />}
      <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {list.map((p) => (
          <div key={p.id} className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
            <div className="flex items-start justify-between">
              <h3 className="text-lg font-semibold text-slate-900">{p.name}</h3>
              <Badge color={p.status === "ACTIVE" ? "emerald" : p.status === "COMPLETED" ? "blue" : "slate"}>{p.status}</Badge>
            </div>
            {p.description && <p className="mt-2 text-sm text-slate-600 line-clamp-3">{p.description}</p>}
            <div className="mt-3 text-xs text-slate-500">
              {p.start_date && <span>From {p.start_date}</span>}
              {p.end_date && <span> → {p.end_date}</span>}
            </div>
            <div className="mt-4 flex gap-2">
              <a href={`/api/impact-projects/${p.id}/analysis/`} className="text-blue-600 underline text-sm">View analysis</a>
            </div>
          </div>
        ))}
        {list.length === 0 && <p className="py-6 text-center text-slate-500 col-span-full">No impact projects yet. Create a standalone project to measure impact outside a programme.</p>}
      </div>
    </div>
  );
}

function ProjectForm({ open, onClose, onSaved }: { open: boolean; onClose: () => void; onSaved: () => void }) {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await apiPost("/impact-projects/", { name, description, start_date: startDate || undefined, end_date: endDate || undefined });
      toast("Impact project created.", "success");
      onSaved();
      onClose();
    } catch (e) {
      toast(apiError(e), "error");
    } finally {
      setSubmitting(false);
    }
  };
  return (
    <Modal open={open} title="New impact project" onClose={onClose}>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <Field label="Name"><Input value={name} onChange={(e) => setName(e.target.value)} required placeholder="e.g. Community Awareness Campaign" /></Field>
        <Field label="Description"><Textarea value={description} onChange={(e) => setDescription(e.target.value)} placeholder="What impact are you measuring?" /></Field>
        <div className="grid grid-cols-2 gap-4">
          <Field label="Start date"><Input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} /></Field>
          <Field label="End date"><Input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} /></Field>
        </div>
        <div className="flex justify-end gap-2 pt-2">
          <Button variant="secondary" size="sm" onClick={onClose} disabled={submitting}>Cancel</Button>
          <Button variant="primary" size="sm" disabled={submitting} type="submit">{submitting ? "Saving…" : "Save"}</Button>
        </div>
      </form>
    </Modal>
  );
}
