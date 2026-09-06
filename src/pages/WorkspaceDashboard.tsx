import { Link } from "react-router-dom";
import { useApi } from "../hooks/useApi";
import type { DashboardResponse } from "../types";
import { StatCard } from "../components/ui/Indicators";
import { Badge } from "../components/ui/Indicator";
import { Card, CardBody, CardHeader } from "../components/ui/Card";
import { KpiProgressChart, TrendLine } from "../components/charts";
import { ApiState, PageHeader } from "../components/PageHeader";
import { toast } from "../components/ui/Toast";

export function WorkspaceDashboard() {
  const dash = useApi<DashboardResponse>("/impact/dashboard/");
  const trends = useApi<{ responses_per_day: unknown[]; enrolment_over_time: unknown[] }>("/impact/trends/?days=180");
  const chall = useApi<{ over_time: unknown[]; by_category: { category: string; count: number }[] }>("/impact/challenge-trends/?days=120");

  if (dash.status === "error") toast(dash.error || "Failed to load dashboard", "error");

  if (dash.status === "loading")
    return <ApiState status="loading" children={null} />;

  const d = dash.data;
  if (!d) return <ApiState status={dash.status} error={dash.error} children={<></>} onRetry={dash.refetch} empty={!dash.data} />;

  const o = d.overview;
  return (
    <div>
      <PageHeader title="Workspace dashboard" subtitle="Voice of a Girl" />

            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <StatCard label="Participants reached" value={o.participants_reached} />
        <StatCard label="Enrolment" value={o.enrolment} sub={`${o.completion_rate}% completed`} />
        <StatCard label="Survey responses" value={o.survey_responses} sub={`${o.survey_response_rate}% response rate`} />
        <StatCard label="Active programmes" value={o.active_programmes} />
        <StatCard label="Active surveys" value={o.active_surveys} />
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader><h3 className="text-lg font-semibold">KPI progress</h3></CardHeader>
          <CardBody>
            <KpiProgressChart data={d.impact.kpis} />
          </CardBody>
        </Card>
        <Card>
          <CardHeader><h3 className="text-lg font-semibold">Responses over time</h3></CardHeader>
          <CardBody>
            <TrendLine data={trends.data?.responses_per_day ?? []} />
          </CardBody>
        </Card>
        <Card>
          <CardHeader><h3 className="text-lg font-semibold">Challenges by category</h3></CardHeader>
          <CardBody>
            <TrendLine data={chall.data?.by_category ?? []} dataKey="count" xAxis="category" />
          </CardBody>
        </Card>
        <Card>
          <CardHeader><h3 className="text-lg font-semibold">Monitoring at a glance</h3></CardHeader>
          <CardBody>
            <div className="grid grid-cols-2 gap-4 text-center">
              <StatCard label="Open" value={d.monitoring.open} />
              <StatCard label="In progress" value={d.monitoring.in_progress} />
              <StatCard label="Resolved" value={d.monitoring.resolved} />
              <StatCard label="Resolution rate" value={`${d.monitoring.resolution_rate}%`} />
            </div>
            <div className="mt-2 text-xs text-slate-500">
              Resolution rate: {d.monitoring.resolution_rate}% over {d.monitoring.total_challenges} total challenges.
            </div>
          </CardBody>
        </Card>
      </div>

      <div className="mt-6 grid gap-6 md:grid-cols-2">
        {d.impact.baseline_endline.map((b) => (
          <Card key={b.kpi}>
            <CardHeader><h3 className="text-lg font-semibold">{b.kpi}</h3></CardHeader>
            <CardBody>
              <div className="text-2xl font-bold">{b.endline ?? b.baseline} {b.unit}</div>
              <div className="text-sm text-slate-500">
                Baseline {b.baseline} → Endline {b.endline}
                {b.change != null && <span className="ml-2">({b.change > 0 ? "+" : ""}{b.change} {b.unit})</span>}
              </div>
            </CardBody>
          </Card>
        ))}
      </div>

      <div className="mt-6">
        <Link to="/workspace/programmes" className="text-blue-600 underline text-sm font-medium">View all programmes →</Link>
      </div>
    </div>
  );
}

