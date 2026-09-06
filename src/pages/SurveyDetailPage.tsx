import { Link, useNavigate, useParams } from "react-router-dom";
import { useApi } from "../hooks/useApi";
import { type Survey, type SurveyResponse } from "../types";
import { Button } from "../components/ui/Button";
import { Badge, Spinner } from "../components/ui/Indicators";
import { Card, CardBody, CardHeader } from "../components/ui/Card";
import { PageHeader, BackButton } from "../components/PageHeader";
import { TrendLine } from "../components/charts";
import { apiPost, apiPatch, apiError } from "../services/api";
import { toast } from "../components/ui/Toast";

export function SurveyDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const surveyApi = useApi<Survey>(`/surveys/${id}/`);
  const stats = useApi<{ responses_total: number; responses_per_day: unknown[] }>(`/surveys/${id}/statistics/`);

  if (surveyApi.status === "loading" || !surveyApi.data) {
    return surveyApi.status === "loading" ? <Spinner size="lg" /> :
      <div className="p-6 text-slate-500">{surveyApi.error || "Survey not found."}</div>;
  }

  const s = surveyApi.data;
  const toggleStatus = async () => {
    try {
      const next = s.status === "PUBLISHED" ? "CLOSED" : "PUBLISHED";
      if (next === "PUBLISHED" && (!s.questions?.length)) {
        toast("Add at least one question before publishing.", "error");
        return;
      }
      await apiPost(`/surveys/${s.id}/${next === "PUBLISHED" ? "publish" : "close"}/`, {});
      toast(`Survey ${next === "PUBLISHED" ? "published" : "closed"}.`, "success");
      surveyApi.refetch();
    } catch (e) {
      toast(apiError(e), "error");
    }
  };

  return (
    <div>
      <BackButton />
      <PageHeader title={s.title}>
        <div className="flex gap-2">
          <Button variant="secondary" size="sm" onClick={() => navigate(`/workspace/surveys/${s.id}/edit`)}>Edit</Button>
          <Button variant={s.status === "PUBLISHED" ? "secondary" : "primary"} size="sm" onClick={toggleStatus}>
            {s.status === "PUBLISHED" ? "Close survey" : "Publish survey"}
          </Button>
          <Button variant="secondary" size="sm" onClick={() => navigate(`/workspace/surveys/${s.id}/responses`)}>Responses</Button>
        </div>
      </PageHeader>

      <Card>
        <CardHeader><h3 className="text-lg font-semibold">Details</h3></CardHeader>
        <CardBody className="grid gap-3 md:grid-cols-2">
          <div><span className="text-xs text-slate-500">Status</span><div className="mt-1"><Badge color={s.status === "PUBLISHED" ? "emerald" : s.status === "CLOSED" ? "red" : "slate"}>{s.status}</Badge></div></div>
          <div><span className="text-xs text-slate-500">Programme</span><p className="text-sm">{s.programme_name || "Standalone"}</p></div>
          <div className="md:col-span-2"><span className="text-xs text-slate-500">Public link</span><div className="mt-1 break-all text-sm text-slate-700">{s.public_url || "Not published yet"}</div></div>
        </CardBody>
      </Card>

      <Card className="mt-6">
        <CardHeader><h3 className="text-lg font-semibold">Questions ({s.questions?.length ?? 0})</h3></CardHeader>
        <CardBody>
          <ul className="space-y-2">
            {(s.questions ?? []).map((q) => (
              <li key={q.id} className="flex items-start justify-between rounded-md border border-slate-100 px-3 py-2">
                <div>
                  <span className="text-sm font-medium text-slate-800">{q.question}</span>
                  <span className="ml-2 text-xs text-slate-500">[{q.question_type}]</span>
                  {q.required && <span className="ml-2 text-xs text-red-500">required</span>}
                </div>
              </li>
            ))}
            {(!s.questions?.length) && <li className="text-sm text-slate-500">No questions. Edit the survey to add some.</li>}
          </ul>
        </CardBody>
      </Card>

      {stats.data && (
        <Card className="mt-6">
          <CardHeader><h3 className="text-lg font-semibold">Response activity</h3></CardHeader>
          <CardBody>
            <p className="text-2xl font-bold">{stats.data.responses_total}</p>
            <TrendLine data={stats.data.responses_per_day} />
          </CardBody>
        </Card>
      )}
    </div>
  );
}

export function ResponsesPage() {
  const { id: surveyId } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: list, status, count } = useList<SurveyResponse>(`/surveys/${surveyId}/responses/`);
  return (
    <div>
      <BackButton />
      <PageHeader title="Survey responses" subtitle={`${count} response${count === 1 ? "" : "s"}`} />
      {status === "loading" ? <Spinner size="lg" /> : null}
      <div className="mt-4 overflow-x-auto rounded-lg border border-slate-200 bg-white">
        <table className="w-full text-sm text-left">
          <thead className="bg-slate-50 text-xs font-medium uppercase text-slate-500">
            <tr><th className="px-4 py-2">Respondent</th><th className="px-4 py-2">Participant</th><th className="px-4 py-2">Submitted</th></tr>
          </thead>
          <tbody>
            {list.map((r) => (
              <tr key={r.id} className="border-t border-slate-100">
                <td className="px-4 py-2">{r.respondent_name || "—"}</td>
                <td className="px-4 py-2">{r.participant_name || "—"}</td>
                <td className="px-4 py-2">{r.submitted_at?.slice(0, 10)}</td>
              </tr>
            ))}
            {list.length === 0 && <tr><td colSpan={3} className="px-4 py-6 text-center text-slate-500">No responses yet.</td></tr>}
          </tbody>
        </table>
      </div>
    </div>
  );
}
