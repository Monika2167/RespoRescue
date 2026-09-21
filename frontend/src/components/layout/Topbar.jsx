import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  Search,
  Bell,
  ChevronDown,
  Menu,
  CheckCircle2,
  AlertCircle
} from "lucide-react";
import { Github } from "../common/GithubIcon";
import { useRepo } from "../../context/RepoContext";
import { useAuth } from "../../context/AuthContext";
import { Badge } from "../common/Badge";

export const Topbar = ({ onMenuClick }) => {
  const { user } = useAuth();
  const { repositories, selectedRepo, selectRepo, githubStatus } = useRepo();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const navigate = useNavigate();

  const handleSelectRepo = (r) => {
    selectRepo(r);
    setDropdownOpen(false);
    navigate(`/repositories/${r.repository_id || r.id}`);
  };

  return (
    <header className="h-16 bg-[#0a0f1d]/90 backdrop-blur border-b border-slate-800/80 px-4 md:px-8 flex items-center justify-between z-20 sticky top-0">
      <div className="flex items-center gap-3">
        <button
          onClick={onMenuClick}
          className="md:hidden p-2 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800"
        >
          <Menu className="w-5 h-5" />
        </button>

        {/* Repository selector */}
        {selectedRepo ? (
          <div className="relative">
            <button
              onClick={() => setDropdownOpen(!dropdownOpen)}
              className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 hover:border-slate-700 text-xs font-medium text-slate-200 transition"
            >
              <Github className="w-3.5 h-3.5 text-indigo-400" />
              <span className="font-semibold text-slate-100">{selectedRepo.name}</span>
              <ChevronDown className="w-3.5 h-3.5 text-slate-500" />
            </button>

            {dropdownOpen && (
              <div className="absolute left-0 mt-2 w-64 bg-[#111726] border border-slate-800 rounded-xl shadow-2xl py-1.5 z-30 animate-fade-in">
                <div className="px-3 py-1.5 text-[10px] font-semibold text-slate-500 uppercase tracking-wider">
                  Switch Repository
                </div>
                {repositories.map((r) => (
                  <button
                    key={r.repository_id || r.id}
                    onClick={() => handleSelectRepo(r)}
                    className={`w-full text-left px-3 py-2 text-xs flex items-center justify-between hover:bg-slate-800 transition ${
                      (selectedRepo.repository_id || selectedRepo.id) ===
                      (r.repository_id || r.id)
                        ? "text-indigo-400 font-semibold bg-indigo-500/10"
                        : "text-slate-300"
                    }`}
                  >
                    <span className="truncate">{r.name}</span>
                  </button>
                ))}
                <div className="border-t border-slate-800 mt-1 pt-1">
                  <Link
                    to="/repositories"
                    onClick={() => setDropdownOpen(false)}
                    className="block px-3 py-1.5 text-xs text-indigo-400 hover:bg-slate-800 font-medium"
                  >
                    + Manage All Repositories
                  </Link>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="text-xs text-slate-400 flex items-center gap-2">
            <span>RepoRescue Intelligence Platform</span>
          </div>
        )}
      </div>

      {/* Right Controls */}
      <div className="flex items-center gap-3">
        {/* GitHub Connection Status */}
        {githubStatus.github_connected ? (
          <Badge variant="success" size="sm" icon={CheckCircle2}>
            GitHub: {githubStatus.username}
          </Badge>
        ) : (
          <Link to="/settings">
            <Badge variant="neutral" size="sm" icon={AlertCircle}>
              GitHub: Not Connected
            </Badge>
          </Link>
        )}

        <Link
          to="/alerts"
          className="p-2 text-slate-400 hover:text-slate-200 hover:bg-slate-800/60 rounded-lg transition relative"
        >
          <Bell className="w-4 h-4" />
        </Link>
      </div>
    </header>
  );
};
