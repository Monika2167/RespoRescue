import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { Bell, AlertTriangle, ShieldAlert, CheckCircle2, Info, ArrowRight } from "lucide-react";
import { useRepo } from "../context/RepoContext";
import { repositoryService } from "../services/repository";
import { graphService } from "../services/graph";
import { Card } from "../components/common/Card";
import { Badge } from "../components/common/Badge";
import { Button } from "../components/common/Button";
import { EmptyState } from "../components/common/EmptyState";
import { Skeleton } from "../components/common/Skeleton";

export const Alerts = () => {
  const { repositories } = useRepo();
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterCategory, setFilterCategory] = useState("all");

  useEffect(() => {
    const generateRealAlerts = async () => {
      try {
        setLoading(true);
        const alertList = [];

        // 1. Check analyses across repositories for real bottleneck flags
        for (const repo of repositories.slice(0, 3)) {
          try {
            const hRes = await repositoryService.getAnalysisHistory(repo.repository_id || repo.id);
            const flagged = (hRes.analyses || []).filter(
              (a) => a.prediction === "Potential Bottleneck"
            );
            flagged.forEach((f) => {
              alertList.push({
                id: `pr-${repo.repository_id}-${f.pr_number}`,
                category: "Critical",
                title: `Potential PR Bottleneck: #${f.pr_number}`,
                repository: repo.name,
                repo_id: repo.repository_id || repo.id,
                message: `ML model predicted high resolution delay with probability ${(f.probability * 100).toFixed(1)}% (Threshold: ${f.threshold || 0.57}).`,
                path: `/repositories/${repo.repository_id || repo.id}/risk/bottleneck`,
                timestamp: f.created_at,
              });
            });
          } catch (e) {}
        }

        // 2. Check health forecast for backlog alert
        try {
          const health = await repositoryService.getHealthForecast();
          if (health.forecast && health.forecast > 500) {
            alertList.push({
              id: "health-surge",
              category: "Warning",
              title: "PR Backlog Elevation Detected",
              repository: "Active Codebase",
              message: `Health model predicts 7-day average backlog will reach ${health.forecast} open pull requests.`,
              path: repositories.length > 0 ? `/repositories/${repositories[0].repository_id || repositories[0].id}/health` : "/dashboard",
              timestamp: health.date,
            });
          }
        } catch (e) {}

        // 3. Check knowledge concentration
        try {
          const kRes = await graphService.getKnowledgeConcentration(10, 0);
          const singles = (kRes.data || []).filter((k) => k.single_contributor_flag === 1);
          if (singles.length > 0) {
            alertList.push({
              id: "knowledge-bus-factor",
              category: "Warning",
              title: "Single Contributor Knowledge Risk",
              repository: "Active Codebase",
              message: `${singles.length} critical source files have only one contributing developer recorded.`,
              path: repositories.length > 0 ? `/repositories/${repositories[0].repository_id || repositories[0].id}/knowledge` : "/dashboard",
              timestamp: new Date().toISOString(),
            });
          }
        } catch (e) {}

        setAlerts(alertList);
      } catch (err) {
        setAlerts([]);
      } finally {
        setLoading(false);
      }
    };

    generateRealAlerts();
  }, [repositories]);

  const filtered = alerts.filter((a) => {
    if (filterCategory === "critical") return a.category === "Critical";
    if (filterCategory === "warning") return a.category === "Warning";
    if (filterCategory === "info") return a.category === "Information";
    return true;
  });

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800/80 pb-5">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            <Bell className="w-6 h-6 text-indigo-400" />
            Early Warning Alerts
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Real-time alerts triggered by predictive models and graph concentration indicators.
          </p>
        </div>

        <div className="flex items-center gap-2">
          {["all", "critical", "warning", "info"].map((cat) => (
            <button
              key={cat}
              onClick={() => setFilterCategory(cat)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium capitalize transition ${
                filterCategory === cat
                  ? "bg-indigo-600 text-white"
                  : "bg-slate-900 border border-slate-800 text-slate-400 hover:text-white"
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <Skeleton count={4} className="h-24" />
      ) : filtered.length === 0 ? (
        <EmptyState
          icon={CheckCircle2}
          title="No active alerts."
          description="Your analyzed repositories have no critical bottleneck or backlog warnings currently triggered."
        />
      ) : (
        <div className="space-y-4">
          {filtered.map((alert) => (
            <div
              key={alert.id}
              className={`p-5 rounded-xl border flex flex-col md:flex-row md:items-center justify-between gap-4 transition ${
                alert.category === "Critical"
                  ? "bg-rose-500/10 border-rose-500/30"
                  : alert.category === "Warning"
                  ? "bg-amber-500/10 border-amber-500/30"
                  : "bg-sky-500/10 border-sky-500/30"
              }`}
            >
              <div className="flex items-start gap-3">
                <div
                  className={`p-2 rounded-lg shrink-0 ${
                    alert.category === "Critical"
                      ? "text-rose-400 bg-rose-500/20"
                      : alert.category === "Warning"
                      ? "text-amber-400 bg-amber-500/20"
                      : "text-sky-400 bg-sky-500/20"
                  }`}
                >
                  <AlertTriangle className="w-5 h-5" />
                </div>

                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-semibold text-white text-sm">
                      {alert.title}
                    </span>
                    <Badge
                      variant={
                        alert.category === "Critical"
                          ? "danger"
                          : alert.category === "Warning"
                          ? "warning"
                          : "info"
                      }
                      size="xs"
                    >
                      {alert.category}
                    </Badge>
                    <span className="text-[11px] text-slate-400 font-mono">
                      {alert.repository}
                    </span>
                  </div>
                  <p className="text-xs text-slate-300 leading-relaxed">
                    {alert.message}
                  </p>
                </div>
              </div>

              <Link to={alert.path} className="shrink-0">
                <Button variant="outline" size="sm">
                  <span>Inspect Risk</span>
                  <ArrowRight className="w-3.5 h-3.5 ml-1" />
                </Button>
              </Link>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
