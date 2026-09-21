import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { HeartPulse, RefreshCw, Layers, TrendingDown, Clock, Activity } from "lucide-react";
import { repositoryService } from "../services/repository";
import { useRepo } from "../context/RepoContext";
import { RepoWorkspaceHeader } from "../components/repository/RepoWorkspaceHeader";
import { RepoWorkspaceNav } from "../components/repository/RepoWorkspaceNav";
import { Card } from "../components/common/Card";
import { Button } from "../components/common/Button";
import { Badge } from "../components/common/Badge";
import { Skeleton } from "../components/common/Skeleton";
import { LineChart } from "../components/charts/LineChart";

export const HealthForecast = () => {
  const { repositoryId } = useParams();
  const { selectedRepo } = useRepo();

  const [forecastData, setForecastData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadForecast = async () => {
    try {
      setLoading(true);
      setError("");
      const res = await repositoryService.getHealthForecast();
      if (!res.success) throw new Error(res.error || "Unable to fetch health forecast.");
      setForecastData(res);
    } catch (err) {
      setError(err.message || "Failed to load health forecast.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadForecast();
  }, []);

  // Generate chart data projection based on actual backend values
  const chartPoints = forecastData
    ? [
        { day: "Current", backlog: forecastData.current_open_pr_backlog },
        { day: "+2d", backlog: Math.round((forecastData.current_open_pr_backlog * 0.95 + forecastData.forecast * 0.05) * 10) / 10 },
        { day: "+4d", backlog: Math.round((forecastData.current_open_pr_backlog * 0.5 + forecastData.forecast * 0.5) * 10) / 10 },
        { day: "+7d (Target)", backlog: forecastData.forecast },
      ]
    : [];

  return (
    <div className="space-y-6 animate-fade-in">
      <RepoWorkspaceHeader repository={selectedRepo} />
      <RepoWorkspaceNav />

      <div className="flex items-center justify-between border-b border-slate-800/80 pb-4">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
            <HeartPulse className="w-5 h-5 text-rose-400" />
            Repository Health Forecast
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Forecast based on historical repository activity and backlog patterns.
          </p>
        </div>

        <Button
          variant="outline"
          size="sm"
          icon={RefreshCw}
          loading={loading}
          onClick={loadForecast}
        >
          Re-run Forecast
        </Button>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          <Skeleton count={3} className="h-32" />
        </div>
      ) : error ? (
        <div className="p-6 rounded-2xl border border-dashed border-slate-800 text-center">
          <p className="text-xs text-slate-400 mb-3">{error}</p>
          <Button variant="primary" size="sm" onClick={loadForecast}>
            Run Analysis
          </Button>
        </div>
      ) : forecastData ? (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            <Card title="7-Day Backlog Forecast" subtitle="Target projected backlog">
              <div className="flex items-baseline gap-2">
                <span className="text-3xl font-bold text-white tracking-tight font-mono">
                  {forecastData.forecast}
                </span>
                <span className="text-xs text-slate-400">PRs</span>
              </div>
              <p className="text-[11px] text-slate-500 mt-2">
                {forecastData.forecast_unit}
              </p>
            </Card>

            <Card title="Current PR Backlog" subtitle="Active unmerged pull requests">
              <div className="flex items-baseline gap-2">
                <span className="text-3xl font-bold text-indigo-400 tracking-tight font-mono">
                  {forecastData.current_open_pr_backlog}
                </span>
                <span className="text-xs text-slate-400">PRs</span>
              </div>
              <p className="text-[11px] text-slate-500 mt-2">
                Recorded snapshot from repository state
              </p>
            </Card>

            <Card title="Current Issue Backlog" subtitle="Active unresolved issues">
              <div className="flex items-baseline gap-2">
                <span className="text-3xl font-bold text-amber-400 tracking-tight font-mono">
                  {forecastData.current_open_issue_backlog}
                </span>
                <span className="text-xs text-slate-400">Issues</span>
              </div>
              <p className="text-[11px] text-slate-500 mt-2">
                Total open backlog requiring maintainer triage
              </p>
            </Card>
          </div>

          <Card
            title="7-Day Backlog Forecast Trajectory"
            subtitle="Trajectory from current PR backlog to projected 7-day average"
          >
            <div className="pt-2">
              <LineChart
                data={chartPoints}
                xKey="day"
                yKey="backlog"
                label="PR Backlog"
                height={220}
                strokeColor="#6366f1"
              />
            </div>
          </Card>

          <Card title="Model Specifications" subtitle="Underlying predictive architecture">
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4 text-xs text-slate-300">
              <div className="p-3 bg-slate-900/60 rounded-xl border border-slate-800">
                <div className="text-slate-500 text-[10px] uppercase font-semibold">Model</div>
                <div className="font-semibold text-slate-100 mt-1">{forecastData.model}</div>
              </div>
              <div className="p-3 bg-slate-900/60 rounded-xl border border-slate-800">
                <div className="text-slate-500 text-[10px] uppercase font-semibold">Alpha Regularization</div>
                <div className="font-mono text-slate-100 mt-1">{forecastData.alpha}</div>
              </div>
              <div className="p-3 bg-slate-900/60 rounded-xl border border-slate-800">
                <div className="text-slate-500 text-[10px] uppercase font-semibold">Feature Count</div>
                <div className="font-mono text-slate-100 mt-1">{forecastData.feature_count} features</div>
              </div>
              <div className="p-3 bg-slate-900/60 rounded-xl border border-slate-800">
                <div className="text-slate-500 text-[10px] uppercase font-semibold">Forecast Horizon</div>
                <div className="text-slate-100 mt-1">7 Days</div>
              </div>
            </div>
          </Card>
        </div>
      ) : null}
    </div>
  );
};
