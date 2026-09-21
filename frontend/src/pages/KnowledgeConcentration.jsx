import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { Users, Search, AlertTriangle, CheckCircle2, RefreshCw } from "lucide-react";
import { graphService } from "../services/graph";
import { useRepo } from "../context/RepoContext";
import { RepoWorkspaceHeader } from "../components/repository/RepoWorkspaceHeader";
import { RepoWorkspaceNav } from "../components/repository/RepoWorkspaceNav";
import { Card } from "../components/common/Card";
import { Button } from "../components/common/Button";
import { Badge } from "../components/common/Badge";
import { Skeleton } from "../components/common/Skeleton";

export const KnowledgeConcentration = () => {
  const { repositoryId } = useParams();
  const { selectedRepo } = useRepo();

  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [filterSingleOnly, setFilterSingleOnly] = useState(false);

  const loadKnowledge = async () => {
    try {
      setLoading(true);
      setError("");
      const res = await graphService.getKnowledgeConcentration(100, 0);
      setRecords(res.data || []);
    } catch (err) {
      setError(err.message || "Failed to load knowledge concentration data.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadKnowledge();
  }, []);

  const filtered = records.filter((r) => {
    const matchesSearch =
      r.file_name?.toLowerCase().includes(search.toLowerCase()) ||
      r.dominant_developer?.toLowerCase().includes(search.toLowerCase());
    if (filterSingleOnly) {
      return matchesSearch && r.single_contributor_flag === 1;
    }
    return matchesSearch;
  });

  const highConcentrationCount = records.filter(
    (r) => r.single_contributor_flag === 1 || r.dominant_developer_share > 0.8
  ).length;

  return (
    <div className="space-y-6 animate-fade-in">
      <RepoWorkspaceHeader repository={selectedRepo} />
      <RepoWorkspaceNav />

      <div className="flex items-center justify-between border-b border-slate-800/80 pb-4">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
            <Users className="w-5 h-5 text-indigo-400" />
            Knowledge Concentration Risk
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Calculated file ownership distribution and single-maintainer vulnerability detection.
          </p>
        </div>

        <Button
          variant="outline"
          size="sm"
          icon={RefreshCw}
          loading={loading}
          onClick={loadKnowledge}
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
          {highConcentrationCount > 0 && (
            <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-200 text-xs flex items-center gap-3">
              <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0" />
              <div>
                <span className="font-semibold text-white block">
                  High Knowledge Concentration Detected
                </span>
                Found {highConcentrationCount} files where a single contributor maintains &gt;80% of historical commits, representing a potential bus-factor bottleneck.
              </div>
            </div>
          )}

          {/* Search and Filters */}
          <div className="flex flex-col sm:flex-row items-center justify-between gap-3 bg-[#0d1322] p-3 rounded-xl border border-slate-800">
            <div className="relative w-full sm:w-80">
              <Search className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Filter by file or developer..."
                className="w-full pl-9 pr-3 py-1.5 text-xs bg-slate-900 border border-slate-800 rounded-lg text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
              />
            </div>

            <label className="flex items-center gap-2 text-xs text-slate-300 cursor-pointer select-none">
              <input
                type="checkbox"
                checked={filterSingleOnly}
                onChange={(e) => setFilterSingleOnly(e.target.checked)}
                className="rounded border-slate-700 text-indigo-600 focus:ring-indigo-500 bg-slate-900"
              />
              <span>Single Contributor Only</span>
            </label>
          </div>

          <Card title="File Ownership & Concentration Matrix" subtitle="Detailed records from repository commit graph">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400">
                    <th className="pb-3 font-semibold">File Name</th>
                    <th className="pb-3 font-semibold">Dominant Developer</th>
                    <th className="pb-3 font-semibold">Share</th>
                    <th className="pb-3 font-semibold">Unique Devs</th>
                    <th className="pb-3 font-semibold">Total Commits</th>
                    <th className="pb-3 font-semibold">Risk Flag</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {filtered.map((row, idx) => (
                    <tr key={idx} className="hover:bg-slate-800/30">
                      <td className="py-2.5 font-mono text-slate-200 max-w-xs truncate">
                        {row.file_name}
                      </td>
                      <td className="py-2.5 font-mono text-indigo-300">
                        {row.dominant_developer || "N/A"}
                      </td>
                      <td className="py-2.5 font-mono">
                        {row.dominant_developer_share !== null
                          ? `${Math.round(row.dominant_developer_share * 100)}%`
                          : "N/A"}
                      </td>
                      <td className="py-2.5 font-mono text-slate-400">
                        {row.unique_developers_per_file}
                      </td>
                      <td className="py-2.5 font-mono text-slate-400">
                        {row.total_file_commits}
                      </td>
                      <td className="py-2.5">
                        {row.single_contributor_flag === 1 ? (
                          <Badge variant="danger" size="xs">
                            Single Contributor
                          </Badge>
                        ) : row.dominant_developer_share > 0.8 ? (
                          <Badge variant="warning" size="xs">
                            High Concentration
                          </Badge>
                        ) : (
                          <Badge variant="success" size="xs">
                            Distributed
                          </Badge>
                        )}
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
