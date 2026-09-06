import { useState } from "react";
import { Link } from "react-router-dom";
import { useList } from "../hooks/useApi";
import { Button } from "../components/ui/Button";
import { Badge, Spinner } from "../components/ui/Indicators";
import { Modal } from "../components/ui/Table";
import { Input, Select, Field } from "../components/ui/Indicator";
import { PageHeader } from "../components/PageHeader";
import { toast } from "../components/ui/Toast";
import { apiPost, apiError } from "../services/api";
import type { Report, ReportType, ReportFormat } from "../types";

const REPORT_TYPES: { value: ReportType; label: string }[] = [
  { value: "GENERAL", label: "General Impact Report" },
  { value: "PROGRAMME", label: "Programme Report" },
  { value: "SURVEY", label: "Survey Report" },
  { value: "IMPACT", label: "Impact Report" },
  { value: "KPI", label: "KPI Report" },
  { value: "PROJECT", label: "Impact Project Report" },
];

const FORMATS: { value: ReportFormat; label: string }[] = [
  { value: "PDF", label: "PDF" },
  { value: "EXCEL", label: "Excel" },
  { value: "CSV", label: "CSV" },
];

export function ReportsPage() {
  const { data: list, status, refetch, count } = useList<Report>("/reports/");
  const [show, setShow] = useState(false);
  return (
    <div>
      <PageHeader title="Reports" subtitle={`${count} report${count === 1 ? "" : "s"} generated`}>
        <Button variant="primary" onClick={() => setShow(true)}>+ Generate report</Button>
      </PageHeader>
      <ReportGenerator open={show} onClose={() => setShow(false)} onSaved={refetch} />
      {status === "loading" ? <Spinner size="lg" /> : null}
      <div className="mt-4 space-y-3">
        {list.map((r) => (
          <div key={r.id} className="flex items-center justify-between rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
            <div>
              <div className="font-medium text-slate-900">{r.title || r.report_type}</div>
              <div className="text-xs text-slate-500">{r.report_type} · {r.file_format} · {r.created_at ? new Date(r.created_at).toLocaleDateString() : "—"}</div>
            </div>
            <div className="flex items-center gap-3">
              <Badge color={r.status === "READY" ? "emerald" : r.status === "FAILED" ? "red" : "amber"}>{r.status}</Badge>
              {r.status === "READY" && r.download_url && (
                <a href={r.download_url} target="_blank" rel="noreferrer" className="text-blue-600 underline text-sm">Download</a>
              )}
            </div>
          </div>
        ))}
        {list.length === 0 && <p className="py-6 text-center text-slate-500">No reports generated yet.</p>}
      </div>
    </div>
  );
}

function ReportGenerator({ open, onClose, onSaved }: { open: boolean; onClose: () => void; onSaved: () => void }) {
  const [title, setTitle] = useState("");
  const [reportType, setReportType] = useState<ReportType>("GENERAL");
  const [fileFormat, setFileFormat] = useState<ReportFormat>("PDF");
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await apiPost("/reports/generate/", { title, report_type: reportType, file_format: fileFormat });
      toast("Report generation started.", "success");
      onSaved();
      onClose();
    } catch (e) {
      toast(apiError(e), "error");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Modal open={open} title="Generate report" onClose={onClose}>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <Field label="Report title (optional)"><Input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="e.g. Q2 Programme Impact Report" /></Field>
        <Field label="Report type">
          <Select value={reportType} onChange={(e) => setReportType(e.target.value as ReportType)}>
            {REPORT_TYPES.map((t) => <option key={t.value} value={t.value}>{t.label}</option>)}
          </Select>
        </Field>
        <Field label="File format">
          <Select value={fileFormat} onChange={(e) => setFileFormat(e.target.value as ReportFormat)}>
            {FORMATS.map((f) => <option key={f.value} value={f.value}>{f.label}</option>)}
          </Select>
        </Field>
        <div className="flex justify-end gap-2 pt-2">
          <Button variant="secondary" size="sm" onClick={onClose} disabled={submitting}>Cancel</Button>
          <Button variant="primary" size="sm" disabled={submitting} type="submit">{submitting ? "Generating…" : "Generate"}</Button>
        </div>
      </form>
    </Modal>
  );
}
