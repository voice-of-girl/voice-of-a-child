import { useState } from "react";
import { useApi, useList } from "../hooks/useApi";
import { Button } from "../components/ui/Button";
import { Badge, Spinner } from "../components/ui/Indicators";
import { Card, CardBody, CardHeader } from "../components/ui/Card";
import { PageHeader } from "../components/PageHeader";
import { KpiProgressChart, TrendLine } from "../components/charts";
import { toast } from "../components/ui/Toast";
import { apiPost, apiError } from "../services/api";
import type { KPI, BaselineEndline } from "../types";

interface StatisticsResponse {
  programmes: { programme_id: string; programme: string; enrolment: number; active: number; completed: number; completion_rate: number; survey_responses: number; target_participants: number }[];
  surveys: { survey_id: string; survey: string; responses: number; response_rate: number }[];
}

interface BaselineEndlineResponse {
  baseline_endline: BaselineEndline[];
  kpis: { id: string; kpi: string; baseline?: number; endline?: number; change?: number | null; unit?: string }[];
}

export function ImpactPage() {
  const dash = useApi<{ overview: { participants_reached: number; enrolment: number; survey_responses: number; survey_response_rate: number; completion_rate: number; active_programmes: number; active_surveys: number; target_participants: number }; impact: { kpis: { id: string; kpi: string; baseline?: number; current?: number; target?: number; endline?: number; progress_percentage?: number; status: string }[]; baseline_endline: BaselineEndline[] } }>("/impact/dashboard/");
  const trends = useApi<{ responses_per_day: Record<string, unknown>[]; enrolment_over_time: Record<string, unknown>[] }>("/impact/trends/?days=180");
  const chall = useApi<{ over_time: Record<string, unknown>[]; by_category: { category: string; count: number }[] }>("/impact/challenge-trends/?days=120");
  const respRates = useApi<{ surveys: { survey_id: string; survey: string; responses: number; response_rate: number; eligible: number }[]; enrolment: number }>("/impact/survey-response-rates/");
  const be = useApi<BaselineEndlineResponse>("/impact/baseline-endline/");

  if (dash.status === "error") toast(dash.error || "Failed to load impact", "error");
  if (dash.status === "loading") return <Spinner size="lg" />;

  const d = dash.data;
  if (!d) return null;

  return (
    <div>
      <PageHeader title="Impact measurement" subtitle="KPIs, baseline vs endline, and outcome trends" />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Stat label="Participants reached" value={d.overview.participants_reached} />
        <Stat label="Enrolment" value={d.overview.enrolment} />
        <Stat label="Survey responses" value={d.overview.survey_responses} />
        <Stat label="Completion rate" value={`${d.overview.completion_rate}%`} />
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader><h3 className="text-lg font-semibold">KPI progress</h3></CardHeader>
          <CardBody><KpiProgressChart data={d.impact.kpis.map((k) => ({ name: k.kpi, baseline: k.baseline, current: k.current, target: k.target, endline: k.endline }))} /></CardBody>
        </Card>
        <Card>
          <CardHeader><h3 className="text-lg font-semibold">Responses over time</h3></CardHeader>
          <CardBody><TrendLine data={trends.data?.responses_per_day ?? []} /></CardBody>
        </Card>
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader><h3 className="text-lg font-semibold">Baseline vs endline</h3></CardHeader>
          <CardBody>
            <div className="space-y-3">
              {d.impact.baseline_endline.map((b) => (
                <div key={b.kpi} className="rounded border border-slate-200 bg-slate-50 p-3">
                  <div className="font-semibold text-slate-900">{b.kpi}</div>
                  <div className="mt-1 flex items-center gap-3 text-sm">
                    <span>Baseline: {b.baseline ?? "—"} {b.unit}</span>
                    <span>→</span>
                    <span>Endline: {b.endline ?? "—"} {b.unit}</span>
                    {b.change != null && <Badge color={b.change >= 0 ? "emerald" : "red"}>{b.change > 0 ? "+" : ""}{b.change}</Badge>}
                  </div>
                </div>
              ))}
              {d.impact.baseline_endline.length === 0 && <p className="text-sm text-slate-500">No baseline/endline pairs yet.</p>}
            </div>
          </CardBody>
        </Card>
        <Card>
          <CardHeader><h3 className="text-lg font-semibold">Survey response rates</h3></CardHeader>
          <CardBody>
            <div className="space-y-2">
              {(respRates.data?.surveys ?? []).map((s) => (
                <div key={s.survey_id} className="flex items-center justify-between rounded border border-slate-200 bg-slate-50 p-2">
                  <span className="text-sm font-medium">{s.survey}</span>
                  <span className="text-sm">{s.response_rate}% ({s.responses}/{s.eligible})</span>
                </div>
              ))}
              {!respRates.data?.surveys?.length && <p className="text-sm text-slate-500">No survey data yet.</p>}
            </div>
          </CardBody>
        </Card>
      </div>

      <div className="mt-6">
        <Card>
          <CardHeader><h3 className="text-lg font-semibold">Challenges by category</h3></CardHeader>
          <CardBody><TrendLine data={chall.data?.by_category ?? []} dataKey="count" xAxis="category" /></CardBody>
        </Card>
      </div>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
      <div className="text-xs font-medium uppercase text-slate-500">{label}</div>
      <div className="mt-1 text-2xl font-bold text-slate-900">{value}</div>
    </div>
  );
}
