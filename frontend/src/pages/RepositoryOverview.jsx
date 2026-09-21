import React, { useState, useEffect } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { Play } from "lucide-react";
import { repositoryService } from "../services/repository";
import { useRepo } from "../context/RepoContext";
import { RepoWorkspaceHeader } from "../components/repository/RepoWorkspaceHeader";
import { RepoWorkspaceNav } from "../components/repository/RepoWorkspaceNav";
import { Card } from "../components/common/Card";
import { Button } from "../components/common/Button";
import { Badge } from "../components/common/Badge";
import { Skeleton } from "../components/common/Skeleton";
import { Modal } from "../components/common/Modal";

export const RepositoryOverview = () => {
  const { repositoryId } = useParams();
  const { selectedRepo, selectRepo } = useRepo();
  const navigate = useNavigate();

  const [repoDetails, setRepoDetails] = useState(null);
  const [analyses, setAnalyses] = useState([]);
  const [healthForecast, setHealthForecast] = useState(null);
  const [loading, setLoading] = useState(true);

  const [analyzeModalOpen, setAnalyzeModalOpen] = useState(false);
  const [prNumber, setPrNumber] = useState("");
  const [analyzing, setAnalyzing] = useState(false);
  const [analyzeError, setAnalyzeError] = useState("");

  useEffect(() => {
    const loadOverviewData = async () => {
      try {
        setLoading(true);
        const [detailRes, analysesRes, healthRes] = await Promise.allSettled([
          repositoryService.getRepositoryDetail(repositoryId),
          repositoryService.getAnalysisHistory(repositoryId),
          repositoryService.getHealthForecast(),
        ]);

        if (detailRes.status === "fulfilled" && detailRes.value.repository) {
          setRepoDetails(detailRes.value.repository);
          selectRepo(detailRes.value.repository);
        }

        if (analysesRes.status === "fulfilled") {
          setAnalyses(analysesRes.value.analyses || []);
        }

        if (healthRes.status === "fulfilled" && healthRes.value.success) {
          setHealthForecast(healthRes.value);
        }
      } catch (err) {
        console.error("Overview error:", err);
      } finally {
        setLoading(false);
      }
    };

    if (repositoryId) {
      loadOverviewData();
    }
  }, [repositoryId]);

  const handleQuickAnalyze = async (e) => {
    e.preventDefault();
    if (!prNumber) return;
    setAnalyzeError("");
    setAnalyzing(true);

    try {
      await repositoryService.analyzePR(repositoryId, prNumber);
      setAnalyzeModalOpen(false);
      navigate(`/repositories/${repositoryId}/risk/bottleneck`);
    } catch (err) {
      setAnalyzeError(err.message || "Failed to analyze PR.");
    } finally {
      setAnalyzing(false);
    }
  };

  const samplePrs = [333333, 333999, 335913, 335882];
  const repo = repoDetails || selectedRepo;

  return (
    <div className="space-y-6 animate-fade-in">
      <RepoWorkspaceHeader
        repository={repo}
        onAnalyzeClick={() => setAnalyzeModalOpen(true)}
      />

      <RepoWorkspaceNav />

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          <Skeleton count={3} className="h-32" />
        </div>
      ) : (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            <Card
              title="Repository Health Forecast"
              subtitle="Ridge regression temporal backlog model"
              headerAction={
                <Link
                  to={`/repositories/${repositoryId}/health`}
                  className="text-xs text-indigo-400 hover:text-indigo-300"
                >
                  View Details →
                </Link>
              }
            >
              {healthForecast ? (
                <div className="space-y-2">
                  <div className="flex items-baseline gap-2">
                    <span className="text-3xl font-bold text-white tracking-tight">
                      {healthForecast.forecast}
                    </span>
                    <span className="text-xs text-slate-400">PRs</span>
                  </div>
                  <p className="text-xs text-slate-400">
                    Projected 7-day average open PR backlog. Current open PRs:{" "}
                    <span className="text-slate-200 font-semibold">
                      {healthForecast.current_open_pr_backlog}
                    </span>
                    .
                  </p>
                </div>
              ) : (
                <div className="text-xs text-slate-500 py-3">
                  Data not available yet. Run health analysis to generate this insight.
                </div>
              )}
            </Card>

            <Card
              title="Bottleneck Risk Status"
              subtitle="Combined 400-feature ML model (Threshold: 0.57)"
              headerAction={
                <Link
                  to={`/repositories/${repositoryId}/risk/bottleneck`}
                  className="text-xs text-indigo-400 hover:text-indigo-300"
                >
                  Explore →
                </Link>
              }
            >
              {analyses.length > 0 ? (
                <div className="space-y-2">
                  <div className="flex items-baseline gap-2">
                    <span className="text-3xl font-bold text-white tracking-tight">
                      {
                        analyses.filter(
                          (a) => a.prediction === "Potential Bottleneck"
                        ).length
                      }
                    </span>
                    <span className="text-xs text-slate-400">
                      / {analyses.length} PRs flagged
                    </span>
                  </div>
                  <p className="text-xs text-slate-400">
                    Latest prediction:{" "}
                    <span className="font-semibold text-slate-200">
                      {analyses[0].prediction}
                    </span>{" "}
                    (PR #{analyses[0].pr_number})
                  </p>
                </div>
              ) : (
                <div className="text-xs text-slate-500 py-3">
                  No pull requests analyzed yet. Run analysis to detect bottlenecks.
                </div>
              )}
            </Card>

            <Card
              title="Change Risk Model"
              subtitle="24h code modification characteristics"
              headerAction={
                <Link
                  to={`/repositories/${repositoryId}/risk/change`}
                  className="text-xs text-indigo-400 hover:text-indigo-300"
                >
                  Inspect →
                </Link>
              }
            >
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <Badge variant="info" size="sm">
                    Threshold: 0.50
                  </Badge>
                  <span className="text-xs text-slate-400">Scaled Ridge Classifier</span>
                </div>
                <p className="text-xs text-slate-400">
                  Evaluates lines added, deletion ratios, and author churn across the first 24 hours.
                </p>
              </div>
            </Card>
          </div>

          <Card
            title="Recent Analyses for this Repository"
            subtitle="Historical predictions generated for pull requests"
            headerAction={
              <Link
                to={`/repositories/${repositoryId}/risk/bottleneck`}
                className="text-xs text-indigo-400 hover:text-indigo-300 font-medium"
              >
                + Analyze New PR
              </Link>
            }
          >
            {analyses.length === 0 ? (
              <div className="text-center py-8 text-xs text-slate-500">
                No analyses on record for this repository. Click "Analyze Pull Request" above to run predictions.
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr className="border-b border-slate-800 text-slate-400">
                      <th className="pb-3 font-semibold">PR Number</th>
                      <th className="pb-3 font-semibold">Prediction</th>
                      <th className="pb-3 font-semibold">Probability</th>
                      <th className="pb-3 font-semibold">Threshold</th>
                      <th className="pb-3 font-semibold">Semantic Signal</th>
                      <th className="pb-3 font-semibold">Analyzed Date</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60">
                    {analyses.slice(0, 5).map((a) => (
                      <tr key={a.analysis_id || a.id} className="hover:bg-slate-800/30">
                        <td className="py-3 font-mono font-medium text-slate-200">
                          #{a.pr_number}
                        </td>
                        <td className="py-3">
                          <Badge
                            variant={
                              a.prediction === "Potential Bottleneck"
                                ? "danger"
                                : "success"
                            }
                            size="xs"
                          >
                            {a.prediction}
                          </Badge>
                        </td>
                        <td className="py-3 font-mono text-slate-300">
                          {a.probability !== null && a.probability !== undefined
                            ? `${(a.probability * 100).toFixed(1)}%`
                            : "N/A"}
                        </td>
                        <td className="py-3 font-mono text-slate-500">
                          {a.threshold || "0.57"}
                        </td>
                        <td className="py-3 text-slate-400">
                          {a.semantic_signal || "N/A"}
                        </td>
                        <td className="py-3 text-slate-500">
                          {a.created_at
                            ? new Date(a.created_at).toLocaleString()
                            : "Recent"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </Card>
        </div>
      )}

      <Modal
        isOpen={analyzeModalOpen}
        onClose={() => setAnalyzeModalOpen(false)}
        title="Analyze Pull Request"
        subtitle="Input a pull request number to run the combined 400-feature ML prediction"
      >
        <form onSubmit={handleQuickAnalyze} className="space-y-4">
          {analyzeError && (
            <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs">
              {analyzeError}
            </div>
          )}

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1.5">
              Pull Request Number
            </label>
            <input
              type="number"
              required
              value={prNumber}
              onChange={(e) => setPrNumber(e.target.value)}
              placeholder="e.g. 333333"
              className="w-full px-3 py-2 text-sm bg-slate-900 border border-slate-800 rounded-lg text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div>
            <div className="text-[11px] text-slate-400 mb-1.5 font-medium">
              Available PRs in repository dataset:
            </div>
            <div className="flex items-center gap-2 flex-wrap">
              {samplePrs.map((num) => (
                <button
                  type="button"
                  key={num}
                  onClick={() => setPrNumber(String(num))}
                  className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-xs font-mono text-indigo-300 transition"
                >
                  #{num}
                </button>
              ))}
            </div>
          </div>

          <div className="flex items-center justify-end gap-3 pt-3">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setAnalyzeModalOpen(false)}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              variant="primary"
              size="sm"
              loading={analyzing}
              icon={Play}
            >
              Run Prediction
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
