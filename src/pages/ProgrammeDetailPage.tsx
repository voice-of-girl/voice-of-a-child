import { useNavigate, useParams } from "react-router-dom";
import { useList, useApi } from "../hooks/useApi";
import { type Programme, type SurveySummary } from "../types";
import { Button } from "../components/ui/Button";
import { Badge, Spinner } from "../components/ui/Indicators";
import { Card, CardBody, CardHeader } from "../components/ui/Card";
import { PageHeader, BackButton } from "../components/PageHeader";
import { TrendLine } from "../components/charts";
import { apiPatch, apiError } from "../services/api";
import { toast } from "../components/ui/Toast";

export function ProgrammeDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const prog = useApi<Programme>(`/programmes/${id}/`);
  const stats = useApi<{ enrolment: number; active: number; completed: number; completion_rate: number; survey_responses: number }>(`/programmes/${id}/statistics/`);
  const surveys = useList<SurveySummary>("/surveys/", { programme: id! });

  if (prog.status === "loading") return <Spinner size="lg" />;
  if (!prog.data) return <div className="p-6 text-slate-500">{prog.error || "Programme not found."}</div>;

  const p = prog.data;
  const handleStatus = async (status: string) => {
    try {
      await apiPatch(`/programmes/${p.id}/`, { status });
      toast(`Programme ${status.toLowerCase()}.`, "success");
      prog.refetch();
    } catch (e) {
      toast(apiError(e), "error");
    }
  };

  return (
    <div>
      <BackButton />
      <PageHeader title={p.name}>
        <Button variant="secondary" onClick={() => navigate(`/workspace/programmes/${p.id}/edit`)}>Edit</Button>
      </PageHeader>
      <Card>
        <CardHeader><h3 className="text-lg font-semibold">Details</h3></CardHeader>
        <CardBody className="grid gap-3 md:grid-cols-2">
          <div><span className="text-xs text-slate-500">Description</span><p className="text-sm">{p.description || "—"}</p></div>
          <div><span className="text-xs text-slate-500">Category</span><p className="text-sm">{p.category || "—"}</p></div>
          <div><span className="text-xs text-slate-500">Start</span><p className="text-sm">{p.start_date}</p></div>
          <div><span className="text-xs text-slate-500">End</span><p className="text-sm">{p.end_date}</p></div>
          <div><span className="text-xs text-slate-500">Status</span>
            <div className="mt-1"><Badge color={p.status === "ACTIVE" ? "emerald" : "blue"}>{p.status}</Badge></div>
          </div>
          <div><span className="text-xs text-slate-500">Target participants</span><p className="text-sm">{p.target_participants ?? "—"}</p></div>
        </CardBody>
      </Card>

      {stats.data && (
        <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <Stat label="Enrolment" value={stats.data.enrolment} />
          <Stat label="Active" value={stats.data.active} />
          <Stat label="Completed" value={stats.data.completed} />
          <Stat label="Completion" value={`${stats.data.completion_rate}%`} />
          <Stat label="Survey responses" value={stats.data.survey_responses} />
        </div>
      )}

      <Card className="mt-6">
        <CardHeader>
          <h3 className="text-lg font-semibold">Surveys</h3>
          <p className="text-sm text-slate-500">{surveys.count} survey{surveys.count === 1 ? "" : "s"}</p>
        </CardHeader>
        <CardBody>
          {surveys.data.length === 0 ? (
            <p className="text-sm text-slate-500">No surveys for this programme.</p>
          ) : (
            <ul className="space-y-2">
              {surveys.data.map((s) => (
                <li key={s.id} className="flex items-center justify-between rounded-md border border-slate-100 px-3 py-2">
                  <div>
                    <span className="font-medium text-slate-800">{s.title}</span>
                    <Badge color="slate" size="sm" className="ml-2">{s.status}</Badge>
                  </div>
                  <TrendLine data={[{ day: "1", count: s.responses_count ?? 0 }]} />
                  <Button size="sm" variant="secondary" onClick={() => navigate(`/workspace/surveys/${s.id}`)}>Open</Button>
                </li>
              ))}
            </ul>
          )}
        </CardBody>
      </Card>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: unknown }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4 text-center">
      <div className="text-2xl font-bold text-slate-900">{value}</div>
      <div className="text-xs text-slate-500">{label}</div>
    </div>
  );
}
