import React from "react";
import { useParams, Link } from "react-router-dom";
import {
  Brain,
  AlertTriangle,
  Users,
  Share2,
  Sliders,
  Clock,
  HeartPulse,
  GitPullRequest,
  ArrowRight,
  ShieldAlert
} from "lucide-react";
import { useRepo } from "../context/RepoContext";
import { RepoWorkspaceHeader } from "../components/repository/RepoWorkspaceHeader";
import { RepoWorkspaceNav } from "../components/repository/RepoWorkspaceNav";
import { Card } from "../components/common/Card";

export const IntelligenceHub = () => {
  const { repositoryId } = useParams();
  const { selectedRepo } = useRepo();
  const base = `/repositories/${repositoryId}`;

  const intelligenceModules = [
    {
      title: "Early Warning System & Bottleneck Risk",
      description:
        "400-feature logistic regression model predicting PRs likely to remain unresolved beyond 7 days.",
      path: `${base}/risk/bottleneck`,
      icon: AlertTriangle,
      badge: "ML Model",
    },
    {
      title: "Change-Risk Prediction",
      description:
        "24-hour code churn and author churn classification evaluating structural change volatility.",
      path: `${base}/risk/change`,
      icon: GitPullRequest,
      badge: "ML Model",
    },
    {
      title: "Repository Health Forecast",
      description:
        "Ridge regression time-series forecast modeling 7-day average PR and issue backlog trajectory.",
      path: `${base}/health`,
      icon: HeartPulse,
      badge: "Forecasting",
    },
    {
      title: "Knowledge Concentration Risk",
      description:
        "Single-contributor exposure flags and dominant developer share across critical source files.",
      path: `${base}/knowledge`,
      icon: Users,
      badge: "Risk Analysis",
    },
    {
      title: "Interactive Graph Intelligence",
      description:
        "Bipartite graph topology mapping relationships between Developers, Files, PRs, Commits, and Issues.",
      path: `${base}/graph`,
      icon: Share2,
      badge: "Graph Mining",
    },
    {
      title: "Impact Propagation Graph",
      description:
        "Calculated co-change frequency matrix determining cascading risks when files are modified.",
      path: `${base}/impact`,
      icon: Share2,
      badge: "Propagation",
    },
    {
      title: "What-If Simulation",
      description:
        "Hypothetical simulation modeling developer departure, reviewer capacity shifts, and backlog stress.",
      path: `${base}/simulation`,
      icon: Sliders,
      badge: "Simulation",
    },
    {
      title: "Temporal Repository Analysis",
      description:
        "Weekly aggregation of active contributors, PR throughput, and commit velocity patterns.",
      path: `${base}/temporal`,
      icon: Clock,
      badge: "Temporal",
    },
    {
      title: "Developer–File Analysis",
      description:
        "Author contribution matrix detailing commit shares and file specialization profiles.",
      path: `${base}/developers`,
      icon: Users,
      badge: "Ownership",
    },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      <RepoWorkspaceHeader repository={selectedRepo} />
      <RepoWorkspaceNav />

      <div className="border-b border-slate-800/80 pb-4">
        <h2 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
          <Brain className="w-5 h-5 text-indigo-400" />
          Repository Intelligence Center
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Explore advanced machine learning predictions, graph mining, and simulations.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {intelligenceModules.map((m) => {
          const Icon = m.icon;
          return (
            <Link
              key={m.path}
              to={m.path}
              className="bg-[#111726] border border-slate-800/90 hover:border-indigo-500/50 rounded-xl p-5 shadow-lg flex flex-col justify-between transition group"
            >
              <div>
                <div className="flex items-center justify-between mb-3">
                  <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800 text-indigo-400 group-hover:bg-indigo-600/10 group-hover:border-indigo-500/30 transition">
                    <Icon className="w-5 h-5" />
                  </div>
                  <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 font-medium">
                    {m.badge}
                  </span>
                </div>
                <h3 className="text-sm font-semibold text-slate-100 group-hover:text-indigo-300 transition mb-1.5">
                  {m.title}
                </h3>
                <p className="text-xs text-slate-400 leading-relaxed line-clamp-2">
                  {m.description}
                </p>
              </div>

              <div className="pt-4 mt-3 border-t border-slate-800/60 flex items-center justify-between text-xs text-indigo-400 font-medium group-hover:text-indigo-300">
                <span>Explore Intelligence</span>
                <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition" />
              </div>
            </Link>
          );
        })}
      </div>
    </div>
  );
};
