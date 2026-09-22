import React, { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import {
  AlertTriangle,
  Play,
  ShieldCheck,
  Zap,
  Info,
  Layers,
  Sparkles,
  ArrowRight,
  TrendingUp,
  TrendingDown
} from "lucide-react";
import { repositoryService } from "../services/repository";
import { useRepo } from "../context/RepoContext";
import { RepoWorkspaceHeader } from "../components/repository/RepoWorkspaceHeader";
import { RepoWorkspaceNav } from "../components/repository/RepoWorkspaceNav";
import { Card } from "../components/common/Card";
import { Button } from "../components/common/Button";
import { Badge } from "../components/common/Badge";
import { EmptyState } from "../components/common/EmptyState";
import { Skeleton } from "../components/common/Skeleton";

export const BottleneckRisk = () => {
  const { repositoryId } = useParams();
  const { selectedRepo } = useRepo();

  const [prNumber, setPrNumber] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [prediction, setPrediction] = useState(null);
  const [history, setHistory] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(true);

  const samplePrs = [333333, 333999, 335913, 335882, 335878];

  const loadHistory = async () => {
    try {
      setHistoryLoading(true);
      const res = await repositoryService.getAnalysisHistory(repositoryId);
      const list = res.analyses || [];
      setHistory(list);
      if (list.length > 0 && !prediction) {
        const latest = list[0];
        setPrNumber(String(latest.pr_number));
        setPrediction({
          success: true,
          pr_number: latest.pr_number,
          probability: latest.probability,
          probability_percent:
            latest.probability !== null ? Math.round(latest.probability * 10000) / 100 : null,
          prediction: latest.prediction,
          threshold: latest.threshold || 0.57,
          semantic_signal: latest.semantic_signal,
          semantic_strength: latest.semantic_strength,
          top_evidence: typeof latest.top_evidence === "string" ? [] : (latest.top_evidence || []),
        });
      }
    } catch (err) {
      console.error("History error:", err);
    } finally {
      setHistoryLoading(false);
    }
  };

  useEffect(() => {
    if (repositoryId) {
      loadHistory();
    }
  }, [repositoryId]);

  const handlePredict = async (prToTest) => {
    const targetPr = prToTest || prNumber;
    if (!targetPr) return;
    setLoading(true);
    setError("");

    try {
      const res = await repositoryService.analyzePR(repositoryId, targetPr);
      setPrediction(res);
      setPrNumber(String(targetPr));
      loadHistory();
    } catch (err) {
      setError(err.message || "Prediction failed for PR #" + targetPr);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <RepoWorkspaceHeader repository={selectedRepo} />
      <RepoWorkspaceNav />

      {/* Header Info */}
      <div className="border-b border-slate-800/80 pb-4">
        <h2 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
          <AlertTriangle className="w-5 h-5 text-amber-400" />
          PR Bottleneck Prediction
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Predicts whether a pull request is likely to remain unresolved beyond the 7-day threshold using a 400-feature ML model.
        </p>
      </div>

      {/* Input Section */}
      <Card title="Run Bottleneck Prediction" subtitle="Select or enter a pull request number">
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
            Predict Bottleneck Risk
          </Button>
        </form>

        {/* Dataset Suggestions */}
        <div className="mt-4 pt-4 border-t border-slate-800/60 flex items-center gap-2 flex-wrap text-xs text-slate-400">
          <span className="font-medium">Quick Pick From Dataset:</span>
          {samplePrs.map((num) => (
            <button
              key={num}
              type="button"
              onClick={() => {
                setPrNumber(String(num));
                handlePredict(num);
              }}
              className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-indigo-300 font-mono text-xs transition"
            >
              #{num}
            </button>
          ))}
        </div>
      </Card>

      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs">
          {error}
        </div>
      )}

      {/* Prediction Result Display */}
      {prediction && (
        <div className="space-y-6 animate-scale-up">
          {/* Main Risk Status Card */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            <Card title="Prediction Status" className="md:col-span-2">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-4 rounded-xl bg-slate-900/60 border border-slate-800/80">
                <div>
                  <div className="text-xs text-slate-400 mb-1">
                    Pull Request #{prediction.pr_number} Outcome
                  </div>
                  <div className="text-2xl font-bold text-white flex items-center gap-3">
                    {prediction.prediction}
                    <Badge
                      variant={
                        prediction.prediction === "Potential Bottleneck"
                          ? "danger"
                          : "success"
                      }
                      size="sm"
                    >
                      {prediction.prediction === "Potential Bottleneck"
                        ? "High Bottleneck Risk"
                        : "Lower Bottleneck Risk"}
                    </Badge>
                  </div>
                </div>

                <div className="text-right sm:border-l sm:border-slate-800 sm:pl-6">
                  <div className="text-xs text-slate-400 mb-1">Model Probability</div>
                  <div className="text-3xl font-mono font-bold text-indigo-400">
                    {prediction.probability_percent !== null &&
                    prediction.probability_percent !== undefined
                      ? `${prediction.probability_percent}%`
                      : prediction.probability !== null
                      ? `${(prediction.probability * 100).toFixed(2)}%`
                      : "N/A"}
                  </div>
                  <div className="text-[10px] text-slate-500 mt-0.5">
                    Threshold: {prediction.threshold || 0.57}
                  </div>
                </div>
              </div>

              {/* Semantic Signal */}
              {(prediction.semantic_signal || prediction.semantic_strength) && (
                <div className="mt-4 p-3.5 rounded-lg bg-indigo-950/20 border border-indigo-500/20 flex items-center justify-between text-xs">
                  <div className="flex items-center gap-2">
                    <Sparkles className="w-4 h-4 text-indigo-400" />
                    <span className="text-slate-300 font-medium">Semantic NLP Signal:</span>
                    <span className="text-indigo-300 font-semibold">
                      {prediction.semantic_signal || "Neutral"}
                    </span>
                  </div>
                  {prediction.semantic_strength && (
                    <span className="text-slate-400 font-mono text-[11px]">
                      Strength: {prediction.semantic_strength}
                    </span>
                  )}
                </div>
              )}
            </Card>

            {/* Model Calibration Info */}
            <Card title="Decision Threshold" subtitle="Scaled Combined Logistic Regression">
              <div className="space-y-3 text-xs text-slate-300">
                <div className="flex justify-between py-1.5 border-b border-slate-800">
                  <span className="text-slate-400">Decision Cutoff</span>
                  <span className="font-mono font-semibold text-slate-100">
                    {prediction.threshold || 0.57}
                  </span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-slate-800">
                  <span className="text-slate-400">Structured Features</span>
                  <span className="font-mono text-slate-100">16 features</span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-slate-800">
                  <span className="text-slate-400">Semantic Embeddings</span>
                  <span className="font-mono text-slate-100">384 dimensions</span>
                </div>
                <div className="flex justify-between py-1.5">
                  <span className="text-slate-400">Total Feature Space</span>
                  <span className="font-mono font-semibold text-indigo-400">
                    400 features
                  </span>
                </div>
              </div>
            </Card>
          </div>

          {/* Model Evidence Section */}
          <Card
            title="Model Evidence"
            subtitle="Signals contributing to this prediction (Note: statistical feature signals, not causal assertions)"
          >
            {prediction.top_evidence && prediction.top_evidence.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {prediction.top_evidence.map((item, idx) => (
                  <div
                    key={idx}
                    className="p-4 rounded-xl bg-slate-900/70 border border-slate-800 hover:border-slate-700 transition"
                  >
                    <div className="flex items-center justify-between mb-1.5">
                      <span className="text-xs font-semibold text-slate-200">
                        {item.description || item.feature}
                      </span>
                      <Badge
                        variant={item.direction === "increases_risk" ? "danger" : "success"}
                        size="xs"
                        icon={item.direction === "increases_risk" ? TrendingUp : TrendingDown}
                      >
                        {item.direction === "increases_risk"
                          ? "Increases Risk"
                          : "Reduces Risk"}
                      </Badge>
                    </div>
                    <p className="text-xs text-slate-400 leading-relaxed mb-2">
                      {item.explanation || "Feature weight observed in initial 24 hours."}
                    </p>
                    {item.contribution !== undefined && (
                      <div className="text-[11px] font-mono text-slate-500">
                        Signal contribution: {Math.round(item.contribution * 1000) / 10}%
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-xs text-slate-400 py-3 leading-relaxed">
                Model evidence signals evaluated: 24h file modifications, commit frequency, author churn, draft flags, and NLP title/description semantics.
              </div>
            )}
          </Card>
        </div>
      )}

      {/* Historical Repository Analyses */}
      <Card title="Analysis History for this Repository" subtitle="Previously evaluated pull requests">
        {historyLoading ? (
          <Skeleton count={3} className="h-10" />
        ) : history.length === 0 ? (
          <div className="text-center py-6 text-xs text-slate-500">
            No analyses on record. Enter a PR number above to run predictions.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400">
                  <th className="pb-2.5 font-semibold">PR #</th>
                  <th className="pb-2.5 font-semibold">Prediction</th>
                  <th className="pb-2.5 font-semibold">Probability</th>
                  <th className="pb-2.5 font-semibold">Semantic Signal</th>
                  <th className="pb-2.5 font-semibold">Date</th>
                  <th className="pb-2.5 font-semibold text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {history.map((h) => (
                  <tr key={h.analysis_id || h.id} className="hover:bg-slate-800/30">
                    <td className="py-2.5 font-mono text-slate-200">#{h.pr_number}</td>
                    <td className="py-2.5">
                      <Badge
                        variant={h.prediction === "Potential Bottleneck" ? "danger" : "success"}
                        size="xs"
                      >
                        {h.prediction}
                      </Badge>
                    </td>
                    <td className="py-2.5 font-mono text-slate-300">
                      {h.probability !== null ? `${(h.probability * 100).toFixed(1)}%` : "N/A"}
                    </td>
                    <td className="py-2.5 text-slate-400">{h.semantic_signal || "N/A"}</td>
                    <td className="py-2.5 text-slate-500">
                      {h.created_at ? new Date(h.created_at).toLocaleDateString() : "Recent"}
                    </td>
                    <td className="py-2.5 text-right">
                      <button
                        onClick={() => {
                          setPrNumber(String(h.pr_number));
                          handlePredict(h.pr_number);
                        }}
                        className="text-xs text-indigo-400 hover:text-indigo-300 font-medium"
                      >
                        Re-evaluate
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
};
