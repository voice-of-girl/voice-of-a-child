import { useState } from "react";
import { Modal } from "../ui/Table";
import { Button } from "../ui/Button";
import { Input, Select, Textarea, Field } from "../ui/Indicator";
import { apiPost, apiError } from "../../services/api";
import { toast } from "../ui/Toast";

type Kind = "CHALLENGE" | "FEEDBACK" | "SUPPORT";

export function LogForm({ open, onClose }: { open: boolean; onClose: () => void }) {
  const [kind, setKind] = useState<Kind>("CHALLENGE");
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [category, setCategory] = useState("");
  const [priority, setPriority] = useState("MEDIUM");
  const [submitting, setSubmitting] = useState(false);

  const reset = () => {
    setTitle("");
    setDescription("");
    setCategory("");
    setPriority("MEDIUM");
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      if (kind === "CHALLENGE") {
        await apiPost("/monitoring/challenges/", {
          title, description, category: category || "OTHER", priority,
        });
        toast("Challenge logged.", "success");
      } else if (kind === "FEEDBACK") {
        await apiPost("/monitoring/feedback/", {
          message: description, category: category || "GENERAL",
        });
        toast("Feedback submitted.", "success");
      } else {
        await apiPost("/monitoring/support-requests/", {
          description, category: category || "OTHER",
        });
        toast("Support request created.", "success");
      }
      reset();
      onClose();
    } catch (e) {
      toast(apiError(e), "error");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Modal open={open} title="Log monitoring item" onClose={onClose}>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <Field label="Type">
          <Select value={kind} onChange={(e) => setKind(e.target.value as Kind)}>
            <option value="CHALLENGE">Challenge</option>
            <option value="FEEDBACK">Feedback</option>
            <option value="SUPPORT">Support request</option>
          </Select>
        </Field>
        {kind === "CHALLENGE" && (
          <Field label="Title">
            <Input value={title} onChange={(e) => setTitle(e.target.value)} required />
          </Field>
        )}
        <Field label={kind === "FEEDBACK" ? "Message" : "Description"}>
          <Textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            required
            placeholder={kind === "FEEDBACK" ? "Share feedback…" : "Describe in detail…"}
          />
        </Field>
        <Field label="Category">
          <Select value={category} onChange={(e) => setCategory(e.target.value)}>
            <option value="">Select…</option>
            {kind === "CHALLENGE" ? (
              <>
                <option value="TRANSPORT">Transport</option>
                <option value="ATTENDANCE">Attendance</option>
                <option value="EQUIPMENT">Equipment</option>
                <option value="SCHEDULING">Scheduling</option>
                <option value="SAFETY">Safety</option>
                <option value="FINANCIAL">Financial</option>
                <option value="FAMILY_CARE">Family care</option>
                <option value="HEALTH">Health</option>
                <option value="OTHER">Other</option>
              </>
            ) : kind === "FEEDBACK" ? (
              <>
                <option value="PROGRAMME">Programme</option>
                <option value="MATERIALS">Materials</option>
                <option value="FACILITATOR">Facilitator</option>
                <option value="VENUE">Venue</option>
                <option value="GENERAL">General</option>
              </>
            ) : (
              <>
                <option value="TRAINING">Training</option>
                <option value="TECHNICAL">Technical</option>
                <option value="MATERIALS">Materials</option>
                <option value="DATA">Data</option>
                <option value="OTHER">Other</option>
              </>
            )}
          </Select>
        </Field>
        {kind === "CHALLENGE" && (
          <Field label="Priority">
            <Select value={priority} onChange={(e) => setPriority(e.target.value)}>
              <option value="LOW">Low</option>
              <option value="MEDIUM">Medium</option>
              <option value="HIGH">High</option>
              <option value="CRITICAL">Critical</option>
            </Select>
          </Field>
        )}
        <div className="flex justify-end gap-2 pt-2">
          <Button variant="secondary" size="sm" onClick={onClose} disabled={submitting}>Cancel</Button>
          <Button variant="primary" size="sm" disabled={submitting} type="submit">
            {submitting ? "Saving…" : "Save"}
          </Button>
        </div>
      </form>
    </Modal>
  );
}
