import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useApi } from "../hooks/useApi";
import { Button } from "../components/ui/Button";
import { Spinner } from "../components/ui/Indicators";
import { Input, Select, Field } from "../components/ui/Indicator";
import { PageHeader, BackButton } from "../components/PageHeader";
import { toast } from "../components/ui/Toast";
import { apiPost, apiPatch, apiError } from "../services/api";

const QUESTION_TYPES = [
  { value: "SHORT_TEXT", label: "Short text" },
  { value: "LONG_TEXT", label: "Long text" },
  { value: "NUMBER", label: "Number" },
  { value: "EMAIL", label: "Email" },
  { value: "YES_NO", label: "Yes / No" },
  { value: "MULTIPLE_CHOICE", label: "Multiple choice" },
  { value: "CHECKBOX", label: "Checkbox (multi)" },
  { value: "DROPDOWN", label: "Dropdown" },
  { value: "DATE", label: "Date" },
  { value: "RATING_SCALE", label: "Rating (1-5)" },
];

interface Q { question: string; question_type: string; options: string[]; required: boolean; order: number }

export function SurveyBuilderPage() {
  const { id: surveyId } = useParams<{ id: string }>();
  const isEdit = Boolean(surveyId);
  const navigate = useNavigate();
  const surveyApi = useApi<any>(isEdit ? `/surveys/${surveyId}/` : null);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [programme, setProgramme] = useState("");
  const [questions, setQuestions] = useState<Q[]>([
    { question: "", question_type: "SHORT_TEXT", options: [], required: true, order: 1 },
  ]);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (surveyApi.data) {
      const s = surveyApi.data;
      setTitle(s.title);
      setDescription(s.description ?? "");
      setProgramme(s.programme ?? "");
      setQuestions((s.questions || []).map((q: any) => ({
        question: q.question, question_type: q.question_type,
        options: q.options ?? [], required: q.required, order: q.order,
      })));
    }
  }, [surveyApi.data]);

  const addQuestion = () =>
    setQuestions([...questions, { question: "", question_type: "SHORT_TEXT", options: [], required: true, order: questions.length + 1 }]);
  const removeQuestion = (idx: number) => setQuestions(questions.filter((_, i) => i !== idx));
  const updateQuestion = (idx: number, patch: Partial<Q>) =>
    setQuestions(questions.map((q, i) => (i === idx ? { ...q, ...patch } : q)));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    const payload = {
      title, description,
      programme: programme || undefined,
      questions: questions.map((q, i) => ({ ...q, order: i + 1 })),
    };
    try {
      if (isEdit) await apiPatch(`/surveys/${surveyId}/`, payload);
      else await apiPost("/surveys/", payload);
      toast(`Survey ${isEdit ? "updated" : "created"}.`, "success");
      navigate("/workspace/surveys");
    } catch (e) {
      toast(apiError(e), "error");
    } finally { setSubmitting(false); }
  };

  if (isEdit && surveyApi.status === "loading") return <Spinner size="lg" />;

  return (
    <div>
      <BackButton />
      <PageHeader title={isEdit ? "Edit survey" : "Create survey"} subtitle="Build your survey questions" />
      <div className="rounded-lg border border-slate-200 bg-white p-6 shadow">
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <Field label="Title"><Input value={title} onChange={(e) => setTitle(e.target.value)} required /></Field>
          <Field label="Description"><Input value={description} onChange={(e) => setDescription(e.target.value)} /> </Field>
          <Field label="Programme (optional)">
            <Select value={programme} onChange={(e) => setProgramme(e.target.value)}>
              <option value="">None (standalone)</option>
            </Select>
          </Field>
          <div className="mt-2 space-y-4">
            {questions.map((q, i) => (
              <QuestionRow
                key={i} q={q} i={i}
                updateQuestion={updateQuestion} removeQuestion={removeQuestion}
              />
            ))}
          </div>
          <div className="flex justify-between pt-2">
            <Button variant="secondary" size="sm" type="button" onClick={addQuestion}>+ Add question</Button>
            <Button variant="primary" type="submit" disabled={submitting}>{submitting ? "Saving…" : "Save survey"}</Button>
          </div>
        </form>
      </div>
    </div>
  );
}

function QuestionRow({ q, i, updateQuestion, removeQuestion }: {
  q: Q; i: number;
  updateQuestion: (idx: number, patch: Partial<Q>) => void;
  removeQuestion: (idx: number) => void;
}) {
  return (
    <div className="rounded-md border border-slate-200 p-4">
      <div className="grid gap-3 sm:grid-cols-2">
        <Field label="Question text"><Input value={q.question} onChange={(e) => updateQuestion(i, { question: e.target.value })} required /></Field>
        <Field label="Type">
          <Select value={q.question_type} onChange={(e) => updateQuestion(i, { question_type: e.target.value })}>
            {QUESTION_TYPES.map((t) => <option key={t.value} value={t.value}>{t.label}</option>)}
          </Select>
        </Field>
      </div>
      {["MULTIPLE_CHOICE", "CHECKBOX", "DROPDOWN"].includes(q.question_type) && (
        <Field label="Options (one per line)" className="mt-2">
          <textarea
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
            rows={3}
            value={q.options.join("\n")}
            onChange={(e) => updateQuestion(i, { options: e.target.value.split("\n").map((s) => s.trim()).filter(Boolean) })}
          />
        </Field>
      )}
      <div className="mt-2 flex items-center gap-4">
        <label className="flex items-center gap-2 text-sm">
          <input type="checkbox" checked={q.required} onChange={(e) => updateQuestion(i, { required: e.target.checked })} /> Required
        </label>
        <Button variant="secondary" size="sm" onClick={() => removeQuestion(i)} type="button">Remove</Button>
      </div>
    </div>
  );
}

