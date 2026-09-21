import React, { useState } from "react";
import { useParams } from "react-router-dom";
import { GitPullRequest, Play, AlertCircle, TrendingUp, CheckCircle2 } from "lucide-react";
import { repositoryService } from "../services/repository";
import { useRepo } from "../context/RepoContext";
import { RepoWorkspaceHeader } from "../components/repository/RepoWorkspaceHeader";
import { RepoWorkspaceNav } from "../components/repository/RepoWorkspaceNav";
import { Card } from "../components/common/Card";
import { Button } from "../components/common/Button";
import { Badge } from "../components/common/Badge";

export const ChangeRisk = () => {
  const { repositoryId } = useParams();
  const { selectedRepo } = useRepo();

  const [prNumber, setPrNumber] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  const samplePrs = [333333, 333999, 326789];

  const handlePredict = async (target) => {
    const num = target || prNumber;
    if (!num) return;
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const res = await repositoryService.predictChangeRisk(num);
      if (!res.success) {
        throw new Error(res.error || "No change-risk data available for PR #" + num);
      }
      setResult(res);
      setPrNumber(String(num));
    } catch (err) {
      setError(err.message || "Failed to calculate change risk.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <RepoWorkspaceHeader repository={selectedRepo} />
      <RepoWorkspaceNav />

      <div className="border-b border-slate-800/80 pb-4">
        <h2 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
          <GitPullRequest className="w-5 h-5 text-indigo-400" />
          Change Risk Prediction
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Predicts whether code changes in a pull request exhibit high structural turnover risk based on 24h activity.
        </p>
      </div>

      <Card title="Evaluate Change Risk" subtitle="Input a pull request number to calculate change risk">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handlePredict();
          }}
          className="flex flex-col sm:flex-row items-center gap-3"
        >
          <div className="relative flex-1 w-full">
            <span className="absolute left-3 top-1/2 -translate-y-1/2 text-xs text-slate-500 font-mono">
              PR #
            </span>
            <input
              type="number"
              required
              value={prNumber}
              onChange={(e) => setPrNumber(e.target.value)}
              placeholder="e.g. 333333"
              className="w-full pl-12 pr-3 py-2 text-sm bg-slate-900 border border-slate-800 rounded-lg text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 font-mono"
            />
          </div>

          <Button
            type="submit"
            variant="primary"
            size="md"
            icon={Play}
            loading={loading}
            className="w-full sm:w-auto"
          >
            Calculate Change Risk
          </Button>
        </form>

        <div className="mt-4 pt-4 border-t border-slate-800/60 flex items-center gap-2 flex-wrap text-xs text-slate-400">
          <span className="font-medium">Available PR Samples:</span>
          {samplePrs.map((num) => (
            <button
              key={num}
              type="button"
              onClick={() => handlePredict(num)}
              className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-indigo-300 font-mono text-xs transition"
            >
              #{num}
            </button>
          ))}
        </div>
      </Card>

      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs flex items-center gap-2.5">
          <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {result && (
        <div className="space-y-6 animate-scale-up">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            <Card title="Change Risk Result" className="md:col-span-2">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-4 rounded-xl bg-slate-900/60 border border-slate-800/80">
                <div>
                  <div className="text-xs text-slate-400 mb-1">PR #{result.pr_number}</div>
                  <div className="text-2xl font-bold text-white flex items-center gap-3">
                    {result.prediction}
                    <Badge
                      variant={result.prediction === "High Change Risk" ? "danger" : "success"}
                      size="sm"
                    >
                      {result.prediction}
                    </Badge>
                  </div>
                </div>

                <div className="text-right sm:border-l sm:border-slate-800 sm:pl-6">
                  <div className="text-xs text-slate-400 mb-1">Risk Probability</div>
                  <div className="text-3xl font-mono font-bold text-indigo-400">
                    {result.probability_percent}%
                  </div>
                  <div className="text-[10px] text-slate-500 mt-0.5">
                    Threshold: {result.threshold}
                  </div>
                </div>
              </div>
            </Card>

            <Card title="Model Specs" subtitle="Scaled Ridge Change Classifier">
              <div className="space-y-2.5 text-xs text-slate-300">
                <div className="flex justify-between py-1 border-b border-slate-800">
                  <span className="text-slate-400">Feature Count</span>
                  <span className="font-mono text-slate-100">{result.feature_count} features</span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-800">
                  <span className="text-slate-400">Observation Window</span>
                  <span className="font-mono text-slate-100">First 24 Hours</span>
                </div>
                <div className="flex justify-between py-1">
                  <span className="text-slate-400">Decision Threshold</span>
                  <span className="font-mono font-semibold text-indigo-400">0.50</span>
                </div>
              </div>
            </Card>
          </div>

          <Card title="Observed Model Evidence" subtitle="Signals contributing to this change risk calculation">
            {result.top_evidence && result.top_evidence.length > 0 ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
                {result.top_evidence.map((ev, i) => (
                  <div
                    key={i}
                    className="p-3 rounded-lg bg-slate-900/80 border border-slate-800 text-xs text-slate-200 flex items-center gap-2.5"
                  >
                    <CheckCircle2 className="w-4 h-4 text-indigo-400 shrink-0" />
                    <span>{ev}</span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-xs text-slate-500 py-2">
                No acute change risk signals detected for this PR.
              </div>
            )}
          </Card>
        </div>
      )}
    </div>
  );
};
