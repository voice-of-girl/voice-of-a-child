import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { http, apiError } from "../services/api";
import { Button } from "../components/ui/Button";
import { Spinner } from "../components/ui/Indicators";
import { toast } from "../components/ui/Toast";
import { QuestionField } from "../components/survey/QuestionField";
import type { PublicQuestion } from "../types";

interface ApiSurvey {
  id: string;
  title: string;
  description?: string;
  stage: string;
  questions: PublicQuestion[];
  thank_you_message?: string;
  accepting_responses: boolean;
  message?: string;
}

export function PublicSurveyPage() {
  const { token } = useParams<{ token: string }>();
  const [survey, setSurvey] = useState<ApiSurvey | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [answers, setAnswers] = useState<Record<string, unknown>>({});

  useEffect(() => {
    if (!token) return;
    setLoading(true);
    http
      .get<ApiSurvey>(`/public/surveys/${token}/`)
      .then((r) => { setSurvey(r.data); setError(null); })
      .catch((e) => setError(apiError(e)))
      .finally(() => setLoading(false));
  }, [token]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!survey || !survey.accepting_responses) return;
    setSubmitting(true);
    const form = e.currentTarget as HTMLFormElement;
    const respondent_name = (form.elements.namedItem("respondent_name") as HTMLInputElement)?.value ?? "";
    const respondent_email = (form.elements.namedItem("respondent_email") as HTMLInputElement)?.value ?? "";
    try {
      await http.post(`/public/surveys/${token}/responses/`, { respondent_name, respondent_email, answers });
      setSubmitted(true);
      toast("Thank you — your response has been recorded.", "success");
    } catch (e) {
      toast(apiError(e), "error");
    } finally {
      setSubmitting(false);
    }
  };

  if (loading)
    return <div className="flex min-h-screen items-center justify-center bg-slate-50"><Spinner size="lg" /></div>;

  if (error)
    return <div className="flex min-h-screen items-center justify-center bg-slate-50 p-6">
      <div className="max-w-md rounded-lg border border-red-200 bg-red-50 p-6 text-red-800">{error}</div>
    </div>;

  if (!survey) return null;

  if (!survey.accepting_responses)
    return <div className="flex min-h-screen items-center justify-center bg-slate-50 p-6">
      <div className="max-w-lg rounded-lg border border-slate-200 bg-white p-8 text-center shadow">
        <h1 className="text-2xl font-bold text-slate-800">{survey.title}</h1>
        <p className="mt-3 text-slate-600">{survey.message || "This survey is currently closed or not yet open."}</p>
      </div>
    </div>;

  if (submitted)
    return <div className="flex min-h-screen items-center justify-center bg-slate-50 p-6">
      <div className="max-w-lg rounded-lg border border-slate-200 bg-white p-8 text-center shadow">
        <div className="mb-4 text-4xl">✓</div>
        <h1 className="text-2xl font-bold text-slate-800">Thank you</h1>
        <p className="mt-3 text-slate-600">{survey.thank_you_message || "Your response has been submitted successfully."}</p>
      </div>
    </div>;

  return (
    <div className="min-h-screen bg-slate-50 py-10">
      <form onSubmit={handleSubmit} className="mx-auto max-w-2xl space-y-6">
        <div className="rounded-lg border border-slate-200 bg-white p-6 shadow">
          <h1 className="text-2xl font-bold text-slate-900">{survey.title}</h1>
          {survey.description && <p className="mt-1 text-slate-600">{survey.description}</p>}
        </div>
        <div className="rounded-lg border border-slate-200 bg-white p-6 shadow">
          <fieldset className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div><label className="block text-sm font-medium text-slate-700">Your name (optional)</label>
              <input name="respondent_name" type="text" placeholder="Leave blank to stay anonymous"
                className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500" /></div>
            <div><label className="block text-sm font-medium text-slate-700">Your email (optional)</label>
              <input name="respondent_email" type="email" placeholder="used to match a participant, if any"
                className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500" /></div>
          </fieldset>
        </div>
        <div className="space-y-4">
          {survey.questions.slice().sort((a, b) => a.order - b.order).map((q) => (
            <QuestionField key={q.id} q={q} answers={answers} setAnswers={setAnswers} />
          ))}
        </div>
        <div className="flex justify-end gap-3">
          <Button type="submit" variant="primary" disabled={submitting}>
            {submitting ? "Sending…" : "Submit response"}
          </Button>
        </div>
      </form>
    </div>
  );
}
