import { useState } from "react";
import { Link } from "react-router-dom";
import { useList } from "../hooks/useApi";
import { type Programme } from "../types";
import { Button } from "../components/ui/Button";
import { Badge, Spinner } from "../components/ui/Indicators";
import { Modal } from "../components/ui/Table";
import { Input, Select, Textarea, Field } from "../components/ui/Indicator";
import { PageHeader } from "../components/PageHeader";
import { toast } from "../components/ui/Toast";
import { apiPost, apiError } from "../services/api";

export function ProgrammesPage() {
  const { data: list, status, refetch, count } = useList<Programme>("/programmes/");
  const [show, setShow] = useState(false);
  return (
    <div>
      <PageHeader title="Programmes" subtitle={`${count} programme${count === 1 ? "" : "s"} in your organisation`}>
        <Button variant="primary" onClick={() => setShow(true)}>+ New programme</Button>
      </PageHeader>
      <ProgrammeForm open={show} onClose={() => setShow(false)} onSaved={refetch} />
      {status === "loading" ? <Spinner size="lg" /> : null}
      <div className="mt-4 overflow-x-auto rounded-lg border border-slate-200 bg-white">
        <table className="w-full text-sm text-left">
          <thead className="bg-slate-50 text-xs font-medium uppercase text-slate-500">
            <tr><th className="px-4 py-2">Name</th><th className="px-4 py-2">Category</th><th className="px-4 py-2">Status</th><th className="px-4 py-2">Participants</th><th className="px-4 py-2 text-right">Actions</th></tr>
          </thead>
          <tbody>
            {list.map((p) => (
              <tr key={p.id} className="border-t border-slate-100">
                <td className="px-4 py-2 font-medium text-slate-900">{p.name}</td>
                <td className="px-4 py-2">{p.category || "—"}</td>
                <td className="px-4 py-2"><Badge color={p.status === "ACTIVE" ? "emerald" : p.status === "COMPLETED" ? "blue" : "slate"}>{p.status}</Badge></td>
                <td className="px-4 py-2">{p.participant_count ?? 0}</td>
                <td className="px-4 py-2 text-right">
                  <Link to={`/workspace/programmes/${p.id}`} className="text-blue-600 underline">Open</Link>
                </td>
              </tr>
            ))}
            {list.length === 0 && <tr><td colSpan={5} className="px-4 py-6 text-center text-slate-500">No programmes yet. Create one to begin.</td></tr>}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function ProgrammeForm({ open, onClose, onSaved }: { open: boolean; onClose: () => void; onSaved: () => void }) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [category, setCategory] = useState("");
  const [target, setTarget] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await apiPost("/programmes/", { name: title, description, category, target_participants: target ? Number(target) : undefined });
      toast("Programme created.", "success");
      onSaved();
      onClose();
    } catch (e) {
      toast(apiError(e), "error");
    } finally {
      setSubmitting(false);
    }
  };
  return (
    <Modal open={open} title="New programme" onClose={onClose}>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <Field label="Name"><Input value={title} onChange={(e) => setTitle(e.target.value)} required /></Field>
        <Field label="Category">
          <Select value={category} onChange={(e) => setCategory(e.target.value)}>
            <option value="">Select…</option>
            <option value="EDUCATION">Education</option>
            <option value="DIGITAL_SKILLS">Digital skills</option>
            <option value="LEADERSHIP">Leadership</option>
            <option value="OTHER">Other</option>
          </Select>
        </Field>
        <Field label="Target participants"><Input type="number" value={target} onChange={(e) => setTarget(e.target.value)} placeholder="e.g. 200" /></Field>
                <Field label="Description"><Textarea value={description} onChange={(e) => setDescription(e.target.value)} placeholder="What is this programme about?" /></Field>
        <div className="flex justify-end gap-2 pt-2">
          <Button variant="secondary" size="sm" onClick={onClose} disabled={submitting}>Cancel</Button>
          <Button variant="primary" size="sm" disabled={submitting} type="submit">{submitting ? "Saving…" : "Save"}</Button>
        </div>
      </form>
    </Modal>
  );
}
