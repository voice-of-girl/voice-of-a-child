import { Link } from "react-router-dom";
import { Globe, Users, BarChart3, FileText, Shield } from "lucide-react";

export function PublicHomePage() {
  return (
    <div className="min-h-screen bg-white text-slate-800">
      <header className="border-b border-slate-200 bg-white">
        <div className="max-w-7xl mx-auto flex items-center justify-between px-4 py-3 sm:px-6 lg:px-8">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-600 text-white text-sm font-bold">VG</div>
            <span className="text-xl font-bold">Voice of a Girl</span>
          </div>
          <Link
            to="/login"
            className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            Team sign in
          </Link>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-12 sm:px-6 lg:px-8">
        <section className="text-center">
          <h1 className="text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl">
            Impact measurement that works for social-impact teams.
          </h1>
          <p className="mx-auto mt-5 max-w-2xl text-lg text-slate-600">
            Manage programmes, collect survey responses through shareable public
            links, track KPIs, challenges and outcomes — all within strict
            multi-tenant data isolation.
          </p>
          <div className="mt-8 flex justify-center gap-4">
            <Link
              to="/login"
              className="rounded-md bg-blue-600 px-5 py-2.5 text-sm font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              Sign in to get started
            </Link>
          </div>
        </section>

        <section className="mt-16 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          <Feature icon={<Users />} title="Programmes & participants" desc="Enrol participants and track them through every phase of a programme." />
          <Feature icon={<BarChart3 />} title="Surveys & real responses" desc="Build surveys and share a single secure link — no login needed to respond." />
          <Feature icon={<Globe />} title="Secure public surveys" desc="Collect responses from anyone, anywhere, while keeping every organisation's data fully isolated." />
          <Feature icon={<Shield />} title="Multi-tenant isolation" desc="Organisation A can never read, update or delete Organisation B's data." />
          <Feature icon={<FileText />} title="Reports & analytics" desc="Export professionally formatted PDF, Excel and CSV reports." />
        </section>
      </main>

      <footer className="border-t border-slate-200 py-6 text-center text-sm text-slate-500">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <p className="font-semibold text-slate-700">Voice of a Girl — platform version 1.0</p>
          <p>Seed demo login: admin@voiceofagirl.org / Voice@2026!</p>
        </div>
      </footer>
    </div>
  );
}

function Feature({ icon, title, desc }: { icon: React.ReactNode; title: string; desc: string }) {
  return (
    <div className="rounded-lg border border-slate-200 p-5 shadow-sm">
      <div className="mb-3 text-blue-600">{icon}</div>
      <h3 className="text-lg font-semibold text-slate-900">{title}</h3>
      <p className="mt-1 text-sm text-slate-600">{desc}</p>
    </div>
  );
}
