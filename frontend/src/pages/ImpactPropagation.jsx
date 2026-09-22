import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { Share2, Search, ArrowRight, RefreshCw } from "lucide-react";
import { graphService } from "../services/graph";
import { useRepo } from "../context/RepoContext";
import { RepoWorkspaceHeader } from "../components/repository/RepoWorkspaceHeader";
import { RepoWorkspaceNav } from "../components/repository/RepoWorkspaceNav";
import { Card } from "../components/common/Card";
import { Button } from "../components/common/Button";
import { Skeleton } from "../components/common/Skeleton";

export const ImpactPropagation = () => {
  const { repositoryId } = useParams();
  const { selectedRepo } = useRepo();

  const [impactData, setImpactData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");

  const loadImpact = async () => {
    try {
      setLoading(true);
      setError("");
      const res = await graphService.getImpact(100, 0);
      setImpactData(res.data || []);
    } catch (err) {
      setError(err.message || "Failed to load impact propagation data.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadImpact();
  }, []);

  const filtered = impactData.filter(
    (row) =>
      row.source_file?.toLowerCase().includes(search.toLowerCase()) ||
      row.target_file?.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6 animate-fade-in">
      <RepoWorkspaceHeader repository={selectedRepo} />
      <RepoWorkspaceNav />

      <div className="flex items-center justify-between border-b border-slate-800/80 pb-4">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
            <Share2 className="w-5 h-5 text-indigo-400" />
            Impact Propagation Graph
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Shows how modifications to a source file propagate risk to associated target files via co-change frequency.
          </p>
        </div>

        <Button
          variant="outline"
          size="sm"
          icon={RefreshCw}
          loading={loading}
          onClick={loadImpact}
        >
          Refresh Data
        </Button>
      </div>

      {loading ? (
        <Skeleton count={3} className="h-28" />
      ) : error ? (
        <div className="p-8 text-center border border-dashed border-slate-800 rounded-xl text-xs text-slate-400">
          {error}
        </div>
      ) : (
        <div className="space-y-6">
          <div className="relative max-w-sm">
            <Search className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search source or target file..."
              className="w-full pl-9 pr-3 py-1.5 text-xs bg-slate-900 border border-slate-800 rounded-lg text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
            />
          </div>

          <Card title="File Co-change & Impact Weights" subtitle="Empirical coupling observed from historical commit graph">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400">
                    <th className="pb-3 font-semibold">Source File</th>
                    <th className="pb-3 font-semibold"></th>
                    <th className="pb-3 font-semibold">Target File</th>
                    <th className="pb-3 font-semibold">Co-change Frequency</th>
                    <th className="pb-3 font-semibold">Impact Weight</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 font-mono">
                  {filtered.map((row, idx) => (
                    <tr key={idx} className="hover:bg-slate-800/30">
                      <td className="py-2.5 text-slate-200 max-w-xs truncate">
                        {row.source_file}
                      </td>
                      <td className="py-2.5 text-indigo-400">
                        <ArrowRight className="w-3.5 h-3.5" />
                      </td>
                      <td className="py-2.5 text-slate-300 max-w-xs truncate">
                        {row.target_file}
                      </td>
                      <td className="py-2.5 text-slate-400">
                        {row.cochange_frequency} commits
                      </td>
                      <td className="py-2.5 text-indigo-400 font-semibold">
                        {row.impact_weight !== null ? row.impact_weight : "N/A"}
                      </td>
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
