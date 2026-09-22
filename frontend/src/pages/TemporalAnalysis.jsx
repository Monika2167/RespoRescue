import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { Clock, RefreshCw, TrendingUp, Users, GitPullRequest } from "lucide-react";
import { graphService } from "../services/graph";
import { useRepo } from "../context/RepoContext";
import { RepoWorkspaceHeader } from "../components/repository/RepoWorkspaceHeader";
import { RepoWorkspaceNav } from "../components/repository/RepoWorkspaceNav";
import { Card } from "../components/common/Card";
import { Button } from "../components/common/Button";
import { Skeleton } from "../components/common/Skeleton";
import { LineChart } from "../components/charts/LineChart";
import { BarChart } from "../components/charts/BarChart";

export const TemporalAnalysis = () => {
  const { repositoryId } = useParams();
  const { selectedRepo } = useRepo();

  const [temporalData, setTemporalData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadTemporal = async () => {
    try {
      setLoading(true);
      setError("");
      const res = await graphService.getTemporalFeatures();
      setTemporalData(res.data || []);
    } catch (err) {
      setError(err.message || "Failed to load temporal features.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTemporal();
  }, []);

  const commitChart = temporalData.map((d) => ({
    week: `W${d.week}`,
    commits: d.commits_per_week,
  }));

  const prBarData = temporalData.slice(-12).map((d) => ({
    label: `W${d.week}`,
    value: d.prs_per_week,
  }));

  return (
    <div className="space-y-6 animate-fade-in">
      <RepoWorkspaceHeader repository={selectedRepo} />
      <RepoWorkspaceNav />

      <div className="flex items-center justify-between border-b border-slate-800/80 pb-4">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
            <Clock className="w-5 h-5 text-indigo-400" />
            Temporal Repository Analysis
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Real historical commit velocity, active contributor trends, and PR throughput over time.
          </p>
        </div>

        <Button
          variant="outline"
          size="sm"
          icon={RefreshCw}
          loading={loading}
          onClick={loadTemporal}
        >
          Refresh Data
        </Button>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          <Skeleton count={2} className="h-64" />
        </div>
      ) : error ? (
        <div className="p-8 text-center border border-dashed border-slate-800 rounded-xl text-xs text-slate-400">
          {error}
        </div>
      ) : temporalData.length === 0 ? (
        <div className="p-8 text-center text-xs text-slate-500 border border-slate-800 rounded-xl">
          No temporal activity data available yet.
        </div>
      ) : (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
            <Card
              title="Weekly Commit Velocity"
              subtitle="Total commits recorded per calendar week"
            >
              <LineChart
                data={commitChart}
                xKey="week"
                yKey="commits"
                label="Commits"
                height={200}
                strokeColor="#6366f1"
              />
            </Card>

            <Card
              title="Recent PR Throughput"
              subtitle="Pull requests created per week (Last 12 weeks)"
            >
              <BarChart
                data={prBarData}
                labelKey="label"
                valueKey="value"
                height={200}
                barColor="#8b5cf6"
              />
            </Card>
          </div>

          <Card title="Weekly Activity Log" subtitle="Comprehensive weekly aggregation records">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400">
                    <th className="pb-3 font-semibold">Week</th>
                    <th className="pb-3 font-semibold">Commits</th>
                    <th className="pb-3 font-semibold">Active Developers</th>
                    <th className="pb-3 font-semibold">PRs</th>
                    <th className="pb-3 font-semibold">PR Authors</th>
                    <th className="pb-3 font-semibold">Files Changed</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 font-mono">
                  {temporalData.map((row, idx) => (
                    <tr key={idx} className="hover:bg-slate-800/30">
                      <td className="py-2.5 font-semibold text-indigo-400">Week {row.week}</td>
                      <td className="py-2.5 text-slate-200">{row.commits_per_week}</td>
                      <td className="py-2.5 text-slate-300">{row.active_developers}</td>
                      <td className="py-2.5 text-slate-300">{row.prs_per_week}</td>
                      <td className="py-2.5 text-slate-400">{row.pr_authors}</td>
                      <td className="py-2.5 text-slate-400">{row.files_changed_per_week}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
};
