import React from "react";
import { NavLink, useNavigate } from "react-router-dom";
import {
  LayoutDashboard,
  GitFork,
  Bell,
  History,
  Settings,
  HelpCircle,
  LogOut,
  ShieldAlert,
  FolderGit2,
  ChevronRight,
  ExternalLink
} from "lucide-react";
import { useAuth } from "../../context/AuthContext";
import { useRepo } from "../../context/RepoContext";

export const Sidebar = ({ isMobile = false, onClose }) => {
  const { user, logout } = useAuth();
  const { selectedRepo } = useRepo();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const navItems = [
    { name: "Dashboard", path: "/dashboard", icon: LayoutDashboard },
    { name: "My Repositories", path: "/repositories", icon: FolderGit2 },
    { name: "Alerts", path: "/alerts", icon: Bell },
    { name: "Analysis History", path: "/history", icon: History },
  ];

  const secondaryNav = [
    { name: "Settings", path: "/settings", icon: Settings },
    { name: "Help & Docs", path: "/help", icon: HelpCircle },
  ];

  return (
    <aside className="w-64 bg-[#0a0f1d] border-r border-slate-800/80 flex flex-col justify-between h-screen select-none">
      <div>
        {/* Brand */}
        <div className="h-16 px-6 flex items-center gap-3 border-b border-slate-800/80">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center shadow-lg shadow-indigo-500/20 text-white font-black text-lg">
            R
          </div>
          <div>
            <div className="font-bold text-slate-100 text-base tracking-tight flex items-center gap-1.5">
              RepoRescue
              <span className="text-[10px] px-1.5 py-0.2 font-medium bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 rounded">
                AI
              </span>
            </div>
            <div className="text-[11px] text-slate-400">Software Intelligence</div>
          </div>
        </div>

        {/* Selected Repo Quick Bar if active */}
        {selectedRepo && (
          <div className="p-3 mx-3 mt-4 rounded-xl bg-slate-900/60 border border-slate-800/80">
            <div className="text-[10px] uppercase font-semibold text-slate-500 tracking-wider mb-1">
              Active Workspace
            </div>
            <NavLink
              to={`/repositories/${selectedRepo.repository_id || selectedRepo.id}`}
              className="flex items-center justify-between text-xs font-medium text-slate-200 hover:text-indigo-400 transition truncate"
              onClick={onClose}
            >
              <span className="truncate">{selectedRepo.name}</span>
              <ChevronRight className="w-3.5 h-3.5 shrink-0 text-slate-500" />
            </NavLink>
          </div>
        )}

        {/* Primary Navigation */}
        <nav className="p-3 space-y-1 mt-2">
          <div className="px-3 py-1.5 text-[10px] font-semibold text-slate-500 uppercase tracking-wider">
            Overview
          </div>
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                onClick={onClose}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition ${
                    isActive
                      ? "bg-indigo-600/15 text-indigo-300 border border-indigo-500/30 font-semibold"
                      : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50"
                  }`
                }
              >
                <Icon className="w-4 h-4" />
                <span>{item.name}</span>
              </NavLink>
            );
          })}
        </nav>

        {/* Secondary Navigation */}
        <div className="p-3 space-y-1 mt-2 border-t border-slate-800/60">
          <div className="px-3 py-1.5 text-[10px] font-semibold text-slate-500 uppercase tracking-wider">
            System
          </div>
          {secondaryNav.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                onClick={onClose}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition ${
                    isActive
                      ? "bg-indigo-600/15 text-indigo-300 border border-indigo-500/30"
                      : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50"
                  }`
                }
              >
                <Icon className="w-4 h-4" />
                <span>{item.name}</span>
              </NavLink>
            );
          })}
        </div>
      </div>

      {/* User Footer */}
      <div className="p-3 border-t border-slate-800/80 bg-slate-900/30">
        <div className="flex items-center justify-between p-2 rounded-xl bg-slate-900/60 border border-slate-800">
          <div className="flex items-center gap-2.5 overflow-hidden">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-slate-700 to-slate-600 text-slate-200 flex items-center justify-center font-bold text-xs uppercase shrink-0">
              {user?.username ? user.username.charAt(0) : "U"}
            </div>
            <div className="overflow-hidden">
              <div className="text-xs font-semibold text-slate-200 truncate">
                {user?.username || "Authenticated"}
              </div>
              <div className="text-[10px] text-slate-500 truncate">
                {user?.email || ""}
              </div>
            </div>
          </div>
          <button
            onClick={handleLogout}
            title="Sign Out"
            className="p-1.5 text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 rounded-lg transition"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </aside>
  );
};
