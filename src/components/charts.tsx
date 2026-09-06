import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, LineChart, Line, CartesianGrid, Cell } from "recharts";

export function KpiProgressChart({ data }: { data: { name: string; baseline?: number; current?: number; target?: number; endline?: number }[] }) {
  if (!data.length) return <p className="text-sm text-slate-500">No KPI data yet.</p>;
  const chartData = data.map((k) => ({
    name: k.name,
    Baseline: k.baseline ?? 0,
    Current: k.current,
    Target: k.target,
    Endline: k.endline,
  }));
  const keys = Array.from(
    new Set(
      data.flatMap((k) =>
        ["Baseline", "Current", "Target", "Endline"].filter((kk) =>
          kk === "Baseline" ? k.baseline != null
          : kk === "Current" ? k.current != null
          : kk === "Target" ? k.target != null
          : k.endline != null
        )
      )
    )
  );
  const colors = ["#64748b", "#2563eb", "#22c55e", "#a855f7"];
  return (
    <ResponsiveContainer width="100%" height={260}>
      <BarChart data={chartData}>
        <XAxis dataKey="name" tick={{ fontSize: 11 }} />
        <YAxis tick={{ fontSize: 11 }} />
        <Tooltip />
        {keys.map((k, i) => <Bar key={k} dataKey={k} fill={colors[i % 4]} />)}
      </BarChart>
    </ResponsiveContainer>
  );
}

export function TrendLine({ data, dataKey = "count", xAxis = "day" }: { data: Record<string, unknown>[]; dataKey?: string; xAxis?: string }) {
  if (!data.length) return <p className="text-sm text-slate-500">No data yet.</p>;
  return (
    <ResponsiveContainer width="100%" height={220}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey={xAxis} tick={{ fontSize: 10 }} />
        <YAxis tick={{ fontSize: 10 }} />
        <Tooltip />
        <Line type="monotone" dataKey={dataKey} stroke="#2563eb" strokeWidth={2} dot={false} />
      </LineChart>
    </ResponsiveContainer>
  );
}

export function DonutChart({ data }: { data: { name: string; value: number }[] }) {
  if (!data.length) return <p className="text-sm text-slate-500">No data yet.</p>;
  const colors = ["#2563eb", "#60a5fa", "#f59e0b", "#ef4444", "#a855f7", "#22c55e", "#64748b"];
  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart layout="vertical" data={data} margin={{ left: 60 }}>
        <XAxis type="number" tick={{ fontSize: 10 }} />
        <YAxis dataKey="name" tick={{ fontSize: 11 }} type="category" />
        <Tooltip />
        <Bar dataKey="value">
          {data.map((_, i) => <Cell key={`c${i}`} fill={colors[i % colors.length]} />)}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
