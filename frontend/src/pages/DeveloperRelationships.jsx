import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { Users, Search, RefreshCw, FileCode, GitCommit } from "lucide-react";
import { graphService } from "../services/graph";
import { useRepo } from "../context/RepoContext";
import { RepoWorkspaceHeader } from "../components/repository/RepoWorkspaceHeader";
import { RepoWorkspaceNav } from "../components/repository/RepoWorkspaceNav";
import { Card } from "../components/common/Card";
import { Button } from "../components/common/Button";
import { Skeleton } from "../components/common/Skeleton";

export const DeveloperRelationships = () => {
  const { repositoryId } = useParams();
  const { selectedRepo } = useRepo();

  const [devFeatures, setDevFeatures] = useState([]);
  const [relationships, setRelationships] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");

  const loadData = async () => {
    try {
      setLoading(true);
      setError("");
      const [devRes, relRes] = await Promise.all([
        graphService.getDeveloperFeatures(),
        graphService.getDeveloperFileRelationships(50, 0),
      ]);
      setDevFeatures(devRes.data || []);
      setRelationships(relRes.data || []);
    } catch (err) {
      setError(err.message || "Failed to load developer relationship data.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const filteredDevs = devFeatures.filter((d) =>
    d.developer?.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6 animate-fade-in">
      <RepoWorkspaceHeader repository={selectedRepo} />
      <RepoWorkspaceNav />

      <div className="flex items-center justify-between border-b border-slate-800/80 pb-4">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
            <Users className="w-5 h-5 text-indigo-400" />
            Developer–File Relationships
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Real contributor activity matrix mapping commits and file ownership.
          </p>
        </div>

        <Button
          variant="outline"
          size="sm"
          icon={RefreshCw}
          loading={loading}
          onClick={loadData}
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
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
            {/* Top Developers Card */}
            <Card title="Contributing Developers" subtitle="Commit velocity and file breadth per author">
              <div className="relative mb-3">
                <Search className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  placeholder="Filter developer handle..."
                  className="w-full pl-9 pr-3 py-1.5 text-xs bg-slate-900 border border-slate-800 rounded-lg text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="overflow-x-auto max-h-80 overflow-y-auto">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr className="border-b border-slate-800 text-slate-400">
                      <th className="pb-2 font-semibold">Developer</th>
                      <th className="pb-2 font-semibold">Commits</th>
                      <th className="pb-2 font-semibold">Files Touched</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60 font-mono">
                    {filteredDevs.map((d, i) => (
                      <tr key={i} className="hover:bg-slate-800/30">
                        <td className="py-2 text-indigo-300 font-semibold">{d.developer}</td>
                        <td className="py-2 text-slate-200">{d.commits_per_developer}</td>
                        <td className="py-2 text-slate-400">{d.files_per_developer}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Card>

            {/* Developer File Touches */}
            <Card title="Developer-File Modifications" subtitle="Commit-level file touch mapping">
              <div className="overflow-x-auto max-h-80 overflow-y-auto">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr className="border-b border-slate-800 text-slate-400">
                      <th className="pb-2 font-semibold">Author</th>
                      <th className="pb-2 font-semibold">File Name</th>
                      <th className="pb-2 font-semibold">Commit</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60 font-mono text-[11px]">
                    {relationships.slice(0, 30).map((rel, i) => (
                      <tr key={i} className="hover:bg-slate-800/30">
                        <td className="py-2 text-indigo-300">{rel.author}</td>
                        <td className="py-2 text-slate-300 max-w-xs truncate">{rel.file_name}</td>
                        <td className="py-2 text-slate-500 truncate max-w-[100px]">{rel.commit_sha}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Card>
          </div>
        </div>
      )}
    </div>
  );
};
