import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useList } from "../hooks/useApi";
import { type Participant, type ProgrammeSummary } from "../types";
import { Button } from "../components/ui/Button";
import { Badge, Spinner } from "../components/ui/Indicators";
import { Modal } from "../components/ui/Table";
import { Input, Select, Field } from "../components/ui/Indicator";
import { PageHeader } from "../components/PageHeader";
import { toast } from "../components/ui/Toast";
import { apiPost, apiError } from "../services/api";

export function ParticipantsPage() {
  const { id: progParam } = useParams<{ id: string }>();
  const [qs] = useState(progParam ? { programme: progParam } : {});
  const { data: list, status, refetch, count } = useList<Participant>("/participants/", qs);
  const [show, setShow] = useState(false);
  const [selected, setSelected] = useState<string | null>(null);
  return (
    <div>
      <PageHeader title="Participants" subtitle={`${count} participants`}>
        <Button variant="primary" onClick={() => setShow(true)}>+ Add participant</Button>
      </PageHeader>
      <ParticipantForm open={show} onClose={() => setShow(false)} onSaved={refetch} />
      {status === "loading" ? <Spinner size="lg" /> : null}
      <div className="mt-4 overflow-x-auto rounded-lg border border-slate-200 bg-white">
        <table className="w-full text-sm text-left">
          <thead className="bg-slate-50 text-xs font-medium uppercase text-slate-500">
            <tr><th className="px-4 py-2">Name</th><th className="px-4 py-2">Programme</th><th className="px-4 py-2">Status</th><th className="px-4 py-2">Actions</th></tr>
          </thead>
          <tbody>
            {list.map((p) => (
              <tr key={p.id} className="border-t border-slate-100">
                <td className="px-4 py-2 font-medium text-slate-900">{p.name || "—"}</td>
                <td className="px-4 py-2">{p.programme_name || "—"}</td>
                <td className="px-4 py-2"><Badge color="slate">{p.status}</Badge></td>
                <td className="px-4 py-2"><Button size="sm" variant="secondary" onClick={() => setSelected(p.id)}>View</Button></td>
              </tr>
            ))}
            {list.length === 0 && <tr><td colSpan={4} className="px-4 py-6 text-center text-slate-500">No participants yet.</td></tr>}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function ParticipantForm({ open, onClose, onSaved }: { open: boolean; onClose: () => void; onSaved: () => void }) {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [programme, setProgramme] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await apiPost("/participants/", { name, email, phone, programme: programme || undefined });
      toast("Participant added.", "success");
      onSaved();
      onClose();
    } catch (e) {
      toast(apiError(e), "error");
    } finally { setSubmitting(false); }
  };
  return (
    <Modal open={open} title="Add participant" onClose={onClose}>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <Field label="Full name"><Input value={name} onChange={(e) => setName(e.target.value)} required /></Field>
        <Field label="Email"><Input type="email" value={email} onChange={(e) => setEmail(e.target.value)} /></Field>
        <Field label="Phone"><Input value={phone} onChange={(e) => setPhone(e.target.value)} /></Field>
        <div className="flex justify-end gap-2 pt-2">
          <Button variant="secondary" size="sm" onClick={onClose} disabled={submitting}>Cancel</Button>
          <Button variant="primary" size="sm" type="submit" disabled={submitting}>{submitting ? "Saving…" : "Save"}</Button>
        </div>
      </form>
    </Modal>
  );
}

export function ParticipantFormPage() {
  const { id } = useParams<{ id: string }>();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [programme, setProgramme] = useState("");
  const navigate = useNavigate();
  const [submitting, setSubmitting] = useState(false);
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await apiPost("/participants/", { name, email, phone, programme: programme || undefined });
      toast("Participant added.", "success");
      navigate("/workspace/participants");
    } catch (e) {
      toast(apiError(e), "error");
    } finally { setSubmitting(false); }
  };
  return (
    <div>
      <PageHeader title="Add participant" subtitle="Create a new participant record" />
      <div className="rounded-lg border border-slate-200 bg-white p-6 shadow">
        <form onSubmit={handleSubmit} className="grid gap-4 md:grid-cols-2">
          <Field label="Full name"><Input value={name} onChange={(e) => setName(e.target.value)} required /></Field>
          <Field label="Email"><Input type="email" value={email} onChange={(e) => setEmail(e.target.value)} /></Field>
          <Field label="Phone"><Input value={phone} onChange={(e) => setPhone(e.target.value)} /></Field>
          <div className="md:col-span-2 flex justify-end gap-2 pt-2">
            <Button variant="secondary" size="sm" onClick={() => navigate("/workspace/participants")} disabled={submitting}>Cancel</Button>
            <Button variant="primary" size="sm" type="submit" disabled={submitting}>{submitting ? "Saving…" : "Save"}</Button>
          </div>
        </form>
      </div>
    </div>
  );
}
