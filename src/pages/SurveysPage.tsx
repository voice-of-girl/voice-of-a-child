import { Link, useNavigate } from "react-router-dom";
import { useList } from "../hooks/useApi";
import { type Survey } from "../types";
import { Button } from "../components/ui/Button";
import { Badge, Spinner } from "../components/ui/Indicators";
import { Card, CardBody, CardHeader } from "../components/ui/Card";
import { PageHeader } from "../components/PageHeader";
import { toast } from "../components/ui/Toast";
import { apiPost, apiError } from "../services/api";

export function SurveysPage() {
  const { data: list, status, refetch, count } = useList<Survey>("/surveys/");
  const navigate = useNavigate();
  return (
    <div>
      <PageHeader title="Surveys" subtitle={`${count} survey${count === 1 ? "" : "s"}`}>
        <Button variant="primary" onClick={() => navigate("/workspace/surveys/create")}>+ Create survey</Button>
      </PageHeader>
      {status === "loading" ? <Spinner size="lg" /> : null}
      <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {list.map((s) => (
          <Card key={s.id}>
            <CardHeader>
              <div className="flex items-start justify-between">
                <h3 className="text-lg font-semibold text-slate-900">{s.title}</h3>
                <Badge color={s.status === "PUBLISHED" ? "emerald" : s.status === "CLOSED" ? "red" : "slate"} size="sm">{s.status}</Badge>
              </div>
            </CardHeader>
            <CardBody>
              <p className="text-sm text-slate-600 line-clamp-2">{s.description || "No description."}</p>
              <div className="mt-3 flex items-center justify-between text-sm">
                <span className="text-slate-500">{s.responses_count ?? 0} responses</span>
                <span className="text-slate-500">{s.programme_name || s.project_name || "Standalone"}</span>
              </div>
              <div className="mt-4 flex gap-2">
                <Link to={`/workspace/surveys/${s.id}`} className="text-sm text-blue-600 underline">Open</Link>
                <Button size="sm" variant="secondary" onClick={() => {
                  navigator.clipboard.writeText(s.public_url || "");
                  toast("Public link copied.", "success");
                }}>Copy link</Button>
              </div>
            </CardBody>
          </Card>
        ))}
        {list.length === 0 && <p className="text-slate-500">No surveys yet. Create one to begin.</p>}
      </div>
    </div>
  );
}
