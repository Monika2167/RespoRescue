import React from "react";
import { NavLink, useParams } from "react-router-dom";
import {
  Activity,
  AlertTriangle,
  GitPullRequest,
  HeartPulse,
  Brain,
  Share2,
  History as HistoryIcon,
  HelpCircle,
  Clock,
  Sparkles,
  Users,
  Sliders
} from "lucide-react";

export const RepoWorkspaceNav = () => {
  const { repositoryId } = useParams();
  const base = `/repositories/${repositoryId}`;

  const tabs = [
    { label: "Overview", to: base, end: true, icon: Activity },
    { label: "Bottleneck Risk", to: `${base}/risk/bottleneck`, icon: AlertTriangle },
    { label: "Change Risk", to: `${base}/risk/change`, icon: GitPullRequest },
    { label: "Health Forecast", to: `${base}/health`, icon: HeartPulse },
    { label: "Intelligence Hub", to: `${base}/intelligence`, icon: Brain },
    { label: "Graph Intelligence", to: `${base}/graph`, icon: Share2 },
    { label: "Temporal Trends", to: `${base}/temporal`, icon: Clock },
    { label: "Knowledge Risk", to: `${base}/knowledge`, icon: Users },
    { label: "Impact Propagation", to: `${base}/impact`, icon: Share2 },
    { label: "What-If Simulation", to: `${base}/simulation`, icon: Sliders },
    { label: "Developers & Files", to: `${base}/developers`, icon: Users },
    { label: "Repo AI Assistant", to: `${base}/assistant`, icon: Sparkles },
  ];

  return (
    <div className="border-b border-slate-800/80 mb-6 overflow-x-auto scrollbar-none">
      <nav className="flex items-center gap-1.5 pb-1">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          return (
            <NavLink
              key={tab.to}
              to={tab.to}
              end={tab.end}
              className={({ isActive }) =>
                `flex items-center gap-2 px-3.5 py-2 text-xs font-medium rounded-lg whitespace-nowrap transition-all duration-150 ${
                  isActive
                    ? "bg-indigo-600/15 text-indigo-300 border border-indigo-500/30 font-semibold"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/40"
                }`
              }
            >
              <Icon className="w-3.5 h-3.5" />
              <span>{tab.label}</span>
            </NavLink>
          );
        })}
      </nav>
    </div>
  );
};
