import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { LogOut, Menu } from "lucide-react";
import { useAuth } from "../../context/AuthContext";
import { useState } from "react";
import { classNames } from "../../services/utils";
import { ToastContainer } from "../ui/Toast";

interface Item { to: string; label: string; icon: React.ReactNode };
const orgItems: Item[] = [
  { to: "/workspace", label: "Dashboard", icon: "🔹" },
  { to: "/workspace/programmes", label: "Programmes", icon: "📚" },
  { to: "/workspace/participants", label: "Participants", icon: "👩‍🎓" },
  { to: "/workspace/surveys", label: "Surveys", icon: "📝" },
  { to: "/workspace/monitoring", label: "Monitoring", icon: "⚠️" },
  { to: "/workspace/impact", label: "Impact", icon: "📊" },
  { to: "/workspace/reports", label: "Reports", icon: "📄" },
  { to: "/workspace/projects", label: "Impact Projects", icon: "🎯" },
];

export function AppShell() {
  const { user, logout } = useAuth();
  const [mobileOpen, setMobileOpen] = useState(false);
  const navigate = useNavigate();
  const orgName = user?.organisation?.name ?? "My Organisation";

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="flex min-h-screen bg-slate-50">
      <aside
        className={classNames(
          "fixed inset-y-0 left-0 z-30 w-64 border-r border-slate-200 bg-white flex flex-col overflow-y-auto",
          "lg:translate-x-0 transition-transform duration-200 ease-in-out",
          mobileOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"
        )}
      >
        <div className="p-5 border-b border-slate-200">
          <div className="text-xl font-bold text-slate-900">Voice of a Girl</div>
          <div className="mt-1 text-xs text-slate-500" title={orgName}>{orgName}</div>
        </div>
        <nav className="flex-1 p-2">
          {orgItems.map((it) => (
            <NavLink
              key={it.to}
              to={it.to}
              end
              className={({ isActive }) =>
                classNames(
                  "flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium text-slate-700 hover:bg-blue-50 hover:text-blue-700",
                  isActive && "bg-blue-50 text-blue-700"
                )
              }
              onClick={() => setMobileOpen(false)}
            >
              <span className="text-base">{it.icon}</span> {it.label}
            </NavLink>
          ))}
        </nav>
        <div className="p-4 border-t border-slate-200">
          <button
            onClick={handleLogout}
            className="flex w-full items-center gap-2 rounded-md px-3 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100"
          >
            <LogOut size={16} /> Logout
          </button>
        </div>
      </aside>

      <div className="flex-1 lg:ml-64">
        <header className="sticky top-0 z-20 flex items-center justify-between border-b border-slate-200 bg-white px-4 py-3 lg:hidden">
          <button
            onClick={() => setMobileOpen((v) => !v)}
            className="rounded-md p-2 text-slate-700 hover:bg-slate-100"
          >
            <Menu size={20} />
          </button>
          <span className="text-sm font-semibold text-slate-900">{orgName}</span>
        </header>
        <main className="p-4 lg:p-6">
          <Outlet />
        </main>
      </div>
      <ToastContainer />
    </div>
  );
}
