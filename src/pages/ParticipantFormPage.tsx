import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useList } from "../hooks/useApi";
import { type Programme } from "../types";
import { Button } from "../components/ui/Button";
import { Input, Select, Field } from "../components/ui/Indicator";
import { PageHeader } from "../components/PageHeader";
import { toast } from "../components/ui/Toast";
import { apiPost, apiError } from "../services/api";

export function ParticipantFormPage() {
  const navigate = useNavigate();
  const { id } = useParams();
  const { data: programmes } = useList<Programme>("/programmes/");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [age, setAge] = useState("");
  const [gender, setGender] = useState("");
  const [district, setDistrict] = useState("");
  const [programmeId, setProgrammeId] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!programmeId) {
      toast("Please select a programme.", "error");
      return;
    }
    setSubmitting(true);
    try {
      await apiPost("/participants/", {
        name,
        email: email || undefined,
        phone: phone || undefined,
        age: age ? Number(age) : undefined,
        gender: gender || undefined,
        district: district || undefined,
        programme: programmeId,
      });
      toast("Participant added.", "success");
      navigate("/workspace/participants");
    } catch (e) {
      toast(apiError(e), "error");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div>
      <PageHeader title="Add participant" subtitle="Enrol someone into a programme" />
      <form onSubmit={handleSubmit} className="max-w-2xl space-y-4 rounded-lg border border-slate-200 bg-white p-6">
        <Field label="Full name"><Input value={name} onChange={(e) => setName(e.target.value)} required /></Field>
        <Field label="Programme">
          <Select value={programmeId} onChange={(e) => setProgrammeId(e.target.value)} required>
            <option value="">Select a programme…</option>
            {programmes.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
          </Select>
        </Field>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <Field label="Email"><Input type="email" value={email} onChange={(e) => setEmail(e.target.value)} /></Field>
          <Field label="Phone"><Input value={phone} onChange={(e) => setPhone(e.target.value)} /></Field>
          <Field label="Age"><Input type="number" value={age} onChange={(e) => setAge(e.target.value)} /></Field>
          <Field label="Gender">
            <Select value={gender} onChange={(e) => setGender(e.target.value)}>
              <option value="">Select…</option>
              <option value="FEMALE">Female</option>
              <option value="MALE">Male</option>
              <option value="NON_BINARY">Non-binary</option>
              <option value="PREFER_NOT_TO_SAY">Prefer not to say</option>
            </Select>
          </Field>
          <Field label="District"><Input value={district} onChange={(e) => setDistrict(e.target.value)} /></Field>
        </div>
        <div className="flex justify-end gap-2 pt-2">
          <Button variant="secondary" onClick={() => navigate(-1)} disabled={submitting}>Cancel</Button>
          <Button variant="primary" disabled={submitting} type="submit">{submitting ? "Saving…" : "Save"}</Button>
        </div>
      </form>
    </div>
  );
}
