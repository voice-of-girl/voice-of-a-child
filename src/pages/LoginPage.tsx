import { FormEvent, useState } from "react";
import { ArrowRight, LockKeyhole } from "lucide-react";
import { useNavigate, useLocation, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { toast } from "../components/ui/Toast";

export function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const user = await login(email.trim(), password);
      const to = (location.state as { from?: string })?.from || "/";
      if (user.role === "PLATFORM_ADMIN") navigate("/admin", { replace: true });
      else navigate(to, { replace: true });
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        "Invalid email or password.";
      setError(msg);
      toast(msg, "error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="mb-8 text-center">
          <div className="inline-flex items-center gap-2">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-blue-600 text-white">
              VG
            </div>
            <span className="text-xl font-bold text-slate-900">Voice of a Girl</span>
          </div>
          <h1 className="mt-4 text-2xl font-bold text-slate-800">Sign in to your workspace</h1>
          <p className="mt-1 text-sm text-slate-500">
            Use your authorised work email to continue.
          </p>
        </div>
        <div className="rounded-lg border border-slate-200 bg-white p-8 shadow-sm">
          {error && <div className="mb-4 rounded-md bg-red-50 border border-red-200 p-3 text-sm text-red-800">{error}</div>}
          <form onSubmit={submit} className="flex flex-col gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Work email</label>
              <input
                required type="email" value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@organisation.org"
                className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm outline-none focus:border-blue-600 focus:ring-1 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Password</label>
              <input
                required type="password" minLength={6} value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your password"
                className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm outline-none focus:border-blue-600 focus:ring-1 focus:ring-blue-500"
              />
            </div>
            <button
              disabled={loading}
              className="inline-flex items-center justify-center gap-2 rounded-md bg-blue-600 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-60"
            >
              {loading ? "Signing you in…" : "Sign in"}
              <ArrowRight size={16} />
            </button>
          </form>
        </div>
        <p className="mt-6 text-center text-xs text-slate-500">
          <LockKeyhole size={12} className="inline mr-1" />
          Secure workspace access for authorised teams.
        </p>
        <p className="mt-2 text-center text-xs text-slate-500">
          <Link to="/" className="text-slate-600 underline">Back to public site</Link>
        </p>
      </div>
    </div>
  );
}
