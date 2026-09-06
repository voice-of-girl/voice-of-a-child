import type { Dispatch, SetStateAction } from "react";
import type { PublicQuestion } from "../../types";

const yesNoOptions = [
  { label: "Yes", value: true },
  { label: "No", value: false },
];

export function QuestionField({
  q,
  answers,
  setAnswers,
}: {
  q: PublicQuestion;
  answers: Record<string, unknown>;
  setAnswers: Dispatch<SetStateAction<Record<string, unknown>>>;
}) {
  const set = (value: unknown) =>
    setAnswers((prev) => ({ ...prev, [q.id]: value }));

  const baseInput =
    "mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500";
  const wrap = "flex flex-col gap-1";

  const renderInput = () => {
    const t = q.question_type;
    if (t === "NUMBER") {
      return <input type="number" className={baseInput} value={(answers[q.id] as number) ?? ""}
        onChange={(e) => set(e.target.value === "" ? null : Number(e.target.value))} />;
    }
    if (t === "EMAIL") {
      return <input type="email" className={baseInput} placeholder="name@example.com"
        value={(answers[q.id] as string) ?? ""} onChange={(e) => set(e.target.value)} />;
    }
    if (t === "DATE") {
      return <input type="date" className={baseInput} value={(answers[q.id] as string) ?? ""}
        onChange={(e) => set(e.target.value)} />;
    }
    if (t === "YES_NO") {
      const opts = yesNoOptions;
      return (
        <div className="flex gap-4 mt-1">
          {opts.map((o) => (
            <label key={String(o.value)} className="flex items-center gap-2 text-sm">
              <input type="radio" name={q.id} checked={answers[q.id] === o.value}
                onChange={() => set(o.value)} /> {o.label}
            </label>
          ))}
        </div>
      );
    }
    if (t === "MULTIPLE_CHOICE" || t === "DROPDOWN") {
      const opts = q.options ?? [];
      if (t === "DROPDOWN") {
        return (
          <select className={baseInput} value={(answers[q.id] as string) ?? ""}
            onChange={(e) => set(e.target.value)}>
            <option value="">Select…</option>
            {opts.map((o) => <option key={o} value={o}>{o}</option>)}
          </select>
        );
      }
      return (
        <div className="flex flex-col gap-2 mt-1">
          {opts.map((o) => (
            <label key={o} className="flex items-center gap-2 text-sm">
              <input type="radio" name={q.id} value={o}
                checked={answers[q.id] === o} onChange={() => set(o)} /> {o}
            </label>
          ))}
        </div>
      );
    }
    if (t === "CHECKBOX") {
      const opts = q.options ?? [];
      const current = (answers[q.id] as string[]) ?? [];
      return (
        <div className="flex flex-col gap-2 mt-1">
          {opts.map((o) => (
            <label key={o} className="flex items-center gap-2 text-sm">
              <input type="checkbox" value={o}
                checked={current.includes(o)}
                onChange={(e) => {
                  const next = e.target.checked
                    ? [...current, o]
                    : current.filter((v) => v !== o);
                  set(next);
                }} /> {o}
            </label>
          ))}
        </div>
      );
    }
    if (t === "RATING_SCALE") {
      return (
        <div className="flex items-center gap-2 mt-1">
          {[1, 2, 3, 4, 5].map((n) => (
            <button key={n} type="button"
              className={`h-9 w-9 rounded-md border text-sm font-medium ${
                (answers[q.id] as number) === n
                  ? "border-blue-600 bg-blue-600 text-white"
                  : "border-slate-300 hover:bg-slate-100"
              }`}
              onClick={() => set(n)}>
              {n}
            </button>
          ))}
        </div>
      );
    }
    // SHORT_TEXT / LONG_TEXT / default
    if (t === "LONG_TEXT") {
      return <textarea className={`${baseInput} min-h-[100px]`} value={(answers[q.id] as string) ?? ""}
        onChange={(e) => set(e.target.value)} />;
    }
    return <input className={baseInput} value={(answers[q.id] as string) ?? ""}
      onChange={(e) => set(e.target.value)} />;
  };

  return (
    <div className={wrap}>
      <label className="text-sm font-medium text-slate-800">
        {q.question}
        {q.required && <span className="text-red-500"> *</span>}
      </label>
      {q.help_text && <span className="text-xs text-slate-500">{q.help_text}</span>}
      {renderInput()}
    </div>
  );
}
