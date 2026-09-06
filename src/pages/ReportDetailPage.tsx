import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useList } from "../hooks/useApi";
import type { Programme } from "../types";
import { Button } from "../components/ui/Button";
import { Select, Field } from "../components/ui/Indicator";
import { PageHeader } from "../components/PageHeader";
import { toast } from "../components/ui/Toast";
import { apiPost, apiError } from "../services/api";

export function ReportDetailPage({ createOnly }: { createOnly?: boolean }) {
  const navigate = useNavigate();
  const { data: programmes } = useList<Programme>("/programmes/");
  const [title, setTitle] = useState("");
  const [reportType, setReportType] = useState("GENERAL");
  const [fileFormat, setFileFormat] = useState("PDF");
  const [programmeId, setProgrammeId] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const res = await apiPost("/reports/generate/", {
        title: title || "Impact report",
        report_type: reportType,
        file_format: fileFormat,
        programme: programmeId || undefined,
      });
      toast("Report generated.", "success");
      navigate(`/workspace/reports/${res.id}`);
    } catch (e) {
      toast(apiError(e), "error");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div>
      <PageHeader title="Generate report" subtitle="Create a PDF, Excel or CSV report" />
      <form onSubmit={handleSubmit} className="max-w-2xl space-y-4 rounded-lg border border-slate-200 bg-white p-6">
        <Field label="Report title"><input className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm" value={title} onChange={(e) => setTitle(e.target.value)} placeholder="e.g. Q2 Programme Impact Report" /></Field>
        <Field label="Report type">
          <Select value={reportType} onChange={(e) => setReportType(e.target.value)}>
            <option value="GENERAL">General Impact</option>
            <option value="PROGRAMME">Programme</option>
            <option value="SURVEY">Survey</option>
            <option value="IMPACT">Impact</option>
            <option value="KPI">KPI</option>
            <option value="PROJECT">Impact Project</option>
          </Select>
        </Field>
        <Field label="Format">
          <Select value={fileFormat} onChange={(e) => setFileFormat(e.target.value)}>
            <option value="PDF">PDF</option>
            <option value="EXCEL">Excel</option>
            <option value="CSV">CSV</option>
          </Select>
        </Field>
        <Field label="Programme (optional)">
          <Select value={programmeId} onChange={(e) => setProgrammeId(e.target.value)}>
            <option value="">All programmes</option>
            {programmes.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
          </Select>
        </Field>
        <div className="flex justify-end gap-2 pt-2">
          <Button variant="secondary" onClick={() => navigate(-1)} disabled={submitting}>Cancel</Button>
          <Button variant="primary" disabled={submitting} type="submit">{submitting ? "Generating…" : "Generate"}</Button>
        </div>
      </form>
    </div>
  );
}
