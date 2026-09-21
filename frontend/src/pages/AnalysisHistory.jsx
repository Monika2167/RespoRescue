import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { History, Search, Filter, Trash2, ArrowRight } from "lucide-react";
import { repositoryService } from "../services/repository";
import { useRepo } from "../context/RepoContext";
import { Card } from "../components/common/Card";
import { Button } from "../components/common/Button";
import { Badge } from "../components/common/Badge";
import { EmptyState } from "../components/common/EmptyState";
import { Skeleton } from "../components/common/Skeleton";
import { Modal } from "../components/common/Modal";

export const AnalysisHistory = () => {
  const { repositories, selectedRepo } = useRepo();
  const [selectedRepoId, setSelectedRepoId] = useState(
    selectedRepo?.repository_id || (repositories.length > 0 ? repositories[0].repository_id : "")
  );

  const [analyses, setAnalyses] = useState([]);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState("");
  const [filterResult, setFilterResult] = useState("all");
  const [inspectModal, setInspectModal] = useState(null);

  const loadHistory = async (repoId) => {
    if (!repoId) return;
    try {
      setLoading(true);
      const res = await repositoryService.getAnalysisHistory(repoId);
      setAnalyses(res.analyses || []);
    } catch (err) {
      setAnalyses([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (selectedRepoId) {
      loadHistory(selectedRepoId);
    }
  }, [selectedRepoId]);

  const handleClearHistory = async () => {
    if (!selectedRepoId) return;
    if (window.confirm("Are you sure you want to clear analysis history for this repository?")) {
      try {
        await repositoryService.clearRepositoryAnalyses(selectedRepoId);
        loadHistory(selectedRepoId);
      } catch (err) {
        alert(err.message || "Failed to clear history.");
      }
    }
  };

  const filtered = analyses.filter((a) => {
    const matchesSearch = String(a.pr_number).includes(search);
    if (filterResult === "bottleneck") {
      return matchesSearch && a.prediction === "Potential Bottleneck";
    }
    if (filterResult === "lower") {
      return matchesSearch && a.prediction !== "Potential Bottleneck";
    }
    return matchesSearch;
  });

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800/80 pb-5">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            <History className="w-6 h-6 text-indigo-400" />
            Analysis History
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Historical record of all machine learning predictions run on your repositories.
          </p>
        </div>

        {analyses.length > 0 && (
          <Button
            variant="outline"
            size="sm"
            icon={Trash2}
            className="text-rose-400 hover:text-rose-300"
            onClick={handleClearHistory}
          >
            Clear Repository History
          </Button>
        )}
      </div>

      {/* Repo Selector Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 bg-[#0d1322] p-3 rounded-xl border border-slate-800">
        <div className="flex items-center gap-2 w-full sm:w-auto">
          <span className="text-xs text-slate-400 font-medium">Repository:</span>
          <select
            value={selectedRepoId}
            onChange={(e) => setSelectedRepoId(e.target.value)}
            className="bg-slate-900 border border-slate-800 text-slate-200 text-xs rounded-lg px-3 py-1.5 focus:outline-none cursor-pointer"
          >
            {repositories.map((r) => (
              <option key={r.repository_id || r.id} value={r.repository_id || r.id}>
                {r.name}
              </option>
            ))}
          </select>
        </div>

        <div className="flex items-center gap-3 w-full sm:w-auto justify-end">
          <div className="relative w-44">
            <Search className="w-3.5 h-3.5 text-slate-500 absolute left-2.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="PR # filter..."
              className="w-full pl-8 pr-2.5 py-1 text-xs bg-slate-900 border border-slate-800 rounded-lg text-slate-200 focus:outline-none"
            />
          </div>

          <select
            value={filterResult}
            onChange={(e) => setFilterResult(e.target.value)}
            className="bg-slate-900 border border-slate-800 text-slate-300 text-xs rounded-lg px-2.5 py-1 focus:outline-none cursor-pointer"
          >
            <option value="all">All Outcomes</option>
            <option value="bottleneck">Bottlenecks Only</option>
            <option value="lower">Lower Risk Only</option>
          </select>
        </div>
      </div>

      {loading ? (
        <Skeleton count={5} className="h-12" />
      ) : filtered.length === 0 ? (
        <EmptyState
          icon={History}
          title="No analysis history yet."
          description="Predictions run on pull requests will be logged here chronologically."
        />
      ) : (
        <Card noPadding>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 bg-slate-900/40">
                  <th className="p-3.5 font-semibold">PR #</th>
                  <th className="p-3.5 font-semibold">Prediction Status</th>
                  <th className="p-3.5 font-semibold">Probability</th>
                  <th className="p-3.5 font-semibold">Threshold</th>
                  <th className="p-3.5 font-semibold">Semantic Signal</th>
                  <th className="p-3.5 font-semibold">Evaluated At</th>
                  <th className="p-3.5 font-semibold text-right">Details</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {filtered.map((a) => (
                  <tr key={a.analysis_id || a.id} className="hover:bg-slate-800/30">
                    <td className="p-3.5 font-mono font-medium text-slate-200">
                      #{a.pr_number}
                    </td>
                    <td className="p-3.5">
                      <Badge
                        variant={
                          a.prediction === "Potential Bottleneck" ? "danger" : "success"
                        }
                        size="xs"
                      >
                        {a.prediction}
                      </Badge>
                    </td>
                    <td className="p-3.5 font-mono text-slate-300">
                      {a.probability !== null ? `${(a.probability * 100).toFixed(1)}%` : "N/A"}
                    </td>
                    <td className="p-3.5 font-mono text-slate-500">{a.threshold || 0.57}</td>
                    <td className="p-3.5 text-slate-400">{a.semantic_signal || "N/A"}</td>
                    <td className="p-3.5 text-slate-500">
                      {a.created_at ? new Date(a.created_at).toLocaleString() : "Recent"}
                    </td>
                    <td className="p-3.5 text-right">
                      <button
                        onClick={() => setInspectModal(a)}
                        className="text-indigo-400 hover:text-indigo-300 font-medium"
                      >
                        Inspect
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {inspectModal && (
        <Modal
          isOpen={true}
          onClose={() => setInspectModal(null)}
          title={`PR #${inspectModal.pr_number} Analysis Record`}
          subtitle={`Analyzed on ${new Date(inspectModal.created_at).toLocaleString()}`}
        >
          <div className="space-y-4 text-xs">
            <div className="p-3 bg-slate-900 rounded-xl border border-slate-800 flex justify-between items-center">
              <div>
                <div className="text-slate-400">Prediction Outcome</div>
                <div className="text-base font-bold text-white mt-0.5">
                  {inspectModal.prediction}
                </div>
              </div>
              <div className="text-right">
                <div className="text-slate-400">Probability</div>
                <div className="text-base font-bold font-mono text-indigo-400">
                  {inspectModal.probability !== null
                    ? `${(inspectModal.probability * 100).toFixed(2)}%`
                    : "N/A"}
                </div>
              </div>
            </div>

            <div>
              <div className="text-slate-400 font-semibold mb-1">Top Model Evidence:</div>
              <div className="p-3 bg-slate-900 rounded-xl border border-slate-800 font-mono text-[11px] text-slate-300">
                {inspectModal.top_evidence || "Standard 400-feature ML model weights applied."}
              </div>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
};
