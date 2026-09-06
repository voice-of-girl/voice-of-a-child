import { useList } from "../hooks/useApi";
import type { Organisation, User } from "../types";
import { Button } from "../components/ui/Button";
import { Badge, Spinner } from "../components/ui/Indicators";
import { PageHeader } from "../components/PageHeader";
import { toast } from "../components/ui/Toast";
import { apiPatch, apiError } from "../services/api";

export function AdminPage() {
  const orgs = useList<Organisation>("/organisations/");
  const users = useList<User>("/auth/users/");

  const verifyOrg = async (id: string, status: string) => {
    try {
      await apiPatch(`/organisations/${id}/verify/`, { verification_status: status });
      toast("Organisation updated.", "success");
      orgs.refetch();
    } catch (e) {
      toast(apiError(e), "error");
    }
  };

  return (
    <div>
      <PageHeader title="Platform administration" subtitle="Manage organisations and users across the platform." />

      <div className="grid gap-6 lg:grid-cols-2">
        <div>
          <h2 className="mb-3 text-lg font-semibold text-slate-900">Organisations</h2>
          {orgs.status === "loading" && <Spinner size="md" />}
          <div className="space-y-3">
            {orgs.data.map((o) => (
              <div key={o.id} className="flex items-center justify-between rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
                <div>
                  <div className="font-medium text-slate-900">{o.name}</div>
                  <div className="text-xs text-slate-500">{o.contact_email} · {o.district || "—"}</div>
                </div>
                <div className="flex items-center gap-2">
                  <Badge color={o.verification_status === "VERIFIED" ? "emerald" : o.verification_status === "PENDING" ? "amber" : "red"}>{o.verification_status}</Badge>
                  {o.verification_status !== "VERIFIED" && (
                    <Button variant="primary" size="sm" onClick={() => verifyOrg(o.id, "VERIFIED")}>Verify</Button>
                  )}
                </div>
              </div>
            ))}
            {orgs.data.length === 0 && <p className="py-4 text-center text-slate-500">No organisations.</p>}
          </div>
        </div>

        <div>
          <h2 className="mb-3 text-lg font-semibold text-slate-900">Users</h2>
          {users.status === "loading" && <Spinner size="md" />}
          <div className="space-y-3">
            {users.data.map((u) => (
              <div key={u.id} className="flex items-center justify-between rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
                <div>
                  <div className="font-medium text-slate-900">{u.full_name || u.email}</div>
                  <div className="text-xs text-slate-500">{u.role} · {u.organisation_name || "No org"}</div>
                </div>
                <Badge color={u.is_active ? "emerald" : "slate"}>{u.is_active ? "Active" : "Inactive"}</Badge>
              </div>
            ))}
            {users.data.length === 0 && <p className="py-4 text-center text-slate-500">No users.</p>}
          </div>
        </div>
      </div>
    </div>
  );
}
