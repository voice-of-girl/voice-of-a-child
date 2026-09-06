import { Link, useParams } from "react-router-dom";
import { useList } from "../hooks/useApi";
import type { SurveyResponse, AnswerRead } from "../types";
import { Badge, Spinner } from "../components/ui/Indicators";
import { Button } from "../components/ui/Button";
import { PageHeader } from "../components/PageHeader";

function AnswerList({ answers }: { answers: AnswerRead[] }) {
  return (
    <dl className="mt-3 space-y-2">
      {answers.map((a) => (
        <div key={a.id} className="rounded border border-slate-200 bg-slate-50 p-2">
          <dt className="text-xs font-semibold text-slate-700">{a.question}</dt>
          <dd className="mt-0.5 text-sm text-slate-900 break-words">{Array.isArray(a.value) ? a.value.join(", ") : String(a.value ?? "—")}</dd>
        </div>
      ))}
    </dl>
  );
}

export function ResponsesPage() {
  const params = useParams<{ id: string }>();
  const surveyId = params.id;
  const { data: list, status, count } = useList<SurveyResponse>(surveyId ? `/survey-responses/?survey=${surveyId}` : "/survey-responses/");
  return (
    <div>
      <PageHeader title="Survey responses" subtitle={`${count} response${count === 1 ? "" : "s"}`}>
        <Link to={`/workspace/surveys/${surveyId}`}><Button variant="ghost" size="sm">← Back to survey</Button></Link>
      </PageHeader>
      {status === "loading" ? <Spinner size="lg" /> : null}
      <div className="mt-4 space-y-3">
        {list.map((r) => (
          <div key={r.id} className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium text-slate-900">{r.respondent_name || r.participant_name || "Anonymous"}</div>
                <div className="text-xs text-slate-500">{r.survey_title} · {r.submitted_at ? new Date(r.submitted_at).toLocaleString() : "—"}</div>
              </div>
              <Badge color={r.status === "SUBMITTED" ? "emerald" : "slate"}>{r.status}</Badge>
            </div>
            {r.answers && r.answers.length > 0 && <AnswerList answers={r.answers} />}
          </div>
        ))}
        {list.length === 0 && <p className="py-6 text-center text-slate-500">No responses yet for this survey.</p>}
      </div>
    </div>
  );
}
