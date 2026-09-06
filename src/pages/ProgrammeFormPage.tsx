import { useNavigate, useParams } from "react-router-dom";
import { useApi } from "../hooks/useApi";
import { type Programme } from "../types";
import { Button } from "../components/ui/Button";
import { Spinner } from "../components/ui/Indicators";
import { Input, Select, Field } from "../components/ui/Indicator";
import { PageHeader, BackButton } from "../components/PageHeader";
import { toast } from "../components/ui/Toast";
import { apiPost, apiPatch, apiError } from "../services/api";

export function ProgrammeFormPage() {
  const { id } = useParams<{ id: string }>();
  const isEdit = Boolean(id);
  const navigate = useNavigate();
  const api = useApi<Programme>(isEdit ? `/programmes/${id}/` : null);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [category, setCategory] = useState("");
  const [target, setTarget] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (api.data) {
      setName(api.data.name || "");
      setDescription(api.data.description || "");
      setCategory(api.data.category || "");
      setTarget(api.data.target_participants?.toString() ?? "");
    }
  }, [api.data]);

  if (isEdit && api.status === "loading") return <Spinner size="lg" />;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const payload = { name, description, category, target_participants: target ? Number(target) : undefined };
      if (isEdit) await apiPatch(`/programmes/${id}/`, payload);
      else await apiPost("/programmes/", payload);
      toast(`Programme ${isEdit ? "updated" : "created"}.`, "success");
      navigate("/workspace/programmes");
    } catch (e) {
      toast(apiError(e), "error");
    } finally { setSubmitting(false); }
  };

  return (
    <div>
      <BackButton />
      <PageHeader title={isEdit ? "Edit programme" : "Create programme"} subtitle="Programme details" />
      <div className="rounded-lg border border-slate-200 bg-white p-6 shadow">
        <form onSubmit={handleSubmit} className="grid gap-4 md:grid-cols-2">
          <Field label="Name"><Input value={name} onChange={(e) => setName(e.target.value)} required /></Field>
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
          <div className="md:col-span-2">
            <Field label="Description"><Input as="textarea" value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Programme description…" /></Field>
          </div>
          <div className="md:col-span-2 flex justify-end gap-2 pt-2">
            <Button variant="secondary" size="sm" onClick={() => navigate("/workspace/programmes")} disabled={submitting}>Cancel</Button>
            <Button variant="primary" size="sm" type="submit" disabled={submitting}>{submitting ? "Saving…" : "Save"}</Button>
          </div>
        </form>
      </div>
    </div>
  );
}
