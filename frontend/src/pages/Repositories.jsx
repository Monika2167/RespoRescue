import React, { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import { Search, Filter, Plus, ArrowRight, RefreshCw, AlertCircle } from "lucide-react";
import { Github } from "../components/common/GithubIcon";
import { useRepo } from "../context/RepoContext";
import { useAuth } from "../context/AuthContext";
import { githubService } from "../services/github";
import { repositoryService } from "../services/repository";
import { Button } from "../components/common/Button";
import { EmptyState } from "../components/common/EmptyState";
import { Badge } from "../components/common/Badge";
import { Skeleton } from "../components/common/Skeleton";
import { Modal } from "../components/common/Modal";

export const Repositories = () => {
  const {
    githubStatus,
    githubRepos,
    loadingGithub,
    fetchGithubRepos,
    refreshRepos,
    selectRepo,
  } = useRepo();
  const { user } = useAuth();
  const navigate = useNavigate();

  const [search, setSearch] = useState("");
  const [filterType, setFilterType] = useState("all");
  const [sortKey, setSortKey] = useState("updated");
  const [manualModalOpen, setManualModalOpen] = useState(false);
  const [manualName, setManualName] = useState("");
  const [manualUrl, setManualUrl] = useState("");
  const [manualLoading, setManualLoading] = useState(false);
  const [manualError, setManualError] = useState("");
  const [selectingId, setSelectingId] = useState(null);

  useEffect(() => {
    if (githubStatus.github_connected && githubRepos.length === 0) {
      fetchGithubRepos();
    }
  }, [githubStatus, githubRepos.length, fetchGithubRepos]);

  const handleSelectGithubRepo = async (repo) => {
    try {
      setSelectingId(repo.id);
      const data = await githubService.selectRepository(repo.id);
      await refreshRepos();
      if (data.workspace?.repository_id) {
        selectRepo({
          repository_id: data.workspace.repository_id,
          name: data.workspace.repository_name,
          github_url: repo.html_url,
        });
        navigate(`/repositories/${data.workspace.repository_id}`);
      }
    } catch (err) {
      alert(err.message || "Failed to initialize workspace for this repository.");
    } finally {
      setSelectingId(null);
    }
  };

  const handleManualAdd = async (e) => {
    e.preventDefault();
    setManualError("");
    setManualLoading(true);

    try {
      const data = await repositoryService.addManualRepository(
        manualName,
        manualUrl,
        user.user_id
      );
      await refreshRepos();
      setManualModalOpen(false);
      if (data.repository_id) {
        selectRepo({
          repository_id: data.repository_id,
          name: data.name,
          github_url: data.github_url,
        });
        navigate(`/repositories/${data.repository_id}`);
      }
    } catch (err) {
      setManualError(err.message || "Failed to add repository.");
    } finally {
      setManualLoading(false);
    }
  };

  const filtered = githubRepos
    .filter((r) => {
      const matchesSearch =
        r.name?.toLowerCase().includes(search.toLowerCase()) ||
        r.full_name?.toLowerCase().includes(search.toLowerCase());
      if (filterType === "public") return matchesSearch && !r.private;
      if (filterType === "private") return matchesSearch && r.private;
      return matchesSearch;
    })
    .sort((a, b) => {
      if (sortKey === "name") return a.name.localeCompare(b.name);
      return new Date(b.updated_at || 0) - new Date(a.updated_at || 0);
    });

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800/80 pb-5">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">
            My Repositories
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Select a repository to explore its intelligence.
          </p>
        </div>

        <div className="flex items-center gap-3">
          {githubStatus.github_connected ? (
            <Button
              variant="outline"
              size="sm"
              icon={RefreshCw}
              loading={loadingGithub}
              onClick={fetchGithubRepos}
            >
              Sync Repositories
            </Button>
          ) : (
            <Link to="/settings">
              <Button variant="primary" size="sm" icon={Github}>
                Connect GitHub
              </Button>
            </Link>
          )}

          <Button
            variant="secondary"
            size="sm"
            icon={Plus}
            onClick={() => setManualModalOpen(true)}
          >
            Manual URL Entry
          </Button>
        </div>
      </div>

      {!githubStatus.github_connected && (
        <div className="p-4 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <Github className="w-5 h-5 text-indigo-400 shrink-0" />
            <div className="text-xs text-indigo-200">
              <span className="font-semibold text-white block">
                Connect your GitHub account
              </span>
              Authenticate your GitHub account to automatically list and inspect your private and public repositories.
            </div>
          </div>
          <Link to="/settings" className="shrink-0">
            <Button variant="primary" size="sm">
              Connect GitHub
            </Button>
          </Link>
        </div>
      )}

      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 bg-[#0d1322] p-3 rounded-xl border border-slate-800/80">
        <div className="relative w-full sm:w-72">
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search repositories..."
            className="w-full pl-9 pr-3 py-1.5 text-xs bg-slate-900 border border-slate-800 rounded-lg text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
          />
        </div>

        <div className="flex items-center gap-3 w-full sm:w-auto justify-end">
          <div className="flex items-center gap-1 text-xs text-slate-400">
            <Filter className="w-3.5 h-3.5" />
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="bg-slate-900 border border-slate-800 text-slate-300 text-xs rounded-lg px-2.5 py-1 focus:outline-none cursor-pointer"
            >
              <option value="all">All Visibility</option>
              <option value="public">Public Only</option>
              <option value="private">Private Only</option>
            </select>
          </div>

          <select
            value={sortKey}
            onChange={(e) => setSortKey(e.target.value)}
            className="bg-slate-900 border border-slate-800 text-slate-300 text-xs rounded-lg px-2.5 py-1 focus:outline-none cursor-pointer"
          >
            <option value="updated">Recently Updated</option>
            <option value="name">Repository Name</option>
          </select>
        </div>
      </div>

      {loadingGithub ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          <Skeleton count={6} className="h-44" />
        </div>
      ) : filtered.length === 0 ? (
        <EmptyState
          icon={Github}
          title="No repositories found."
          description={
            githubStatus.github_connected
              ? "We couldn't find any repositories matching your search filters."
              : "Please connect your GitHub account or use manual URL entry to start analyzing."
          }
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {filtered.map((repo) => (
            <div
              key={repo.id}
              className="bg-[#111726] border border-slate-800 hover:border-indigo-500/40 rounded-xl p-5 shadow-lg flex flex-col justify-between transition group"
            >
              <div>
                <div className="flex items-start justify-between gap-3 mb-2">
                  <div className="flex items-center gap-2 overflow-hidden">
                    <Github className="w-4 h-4 text-slate-400 group-hover:text-indigo-400 transition shrink-0" />
                    <h3 className="text-sm font-semibold text-slate-100 group-hover:text-indigo-300 truncate">
                      {repo.name}
                    </h3>
                  </div>
                  <Badge variant={repo.private ? "neutral" : "info"} size="xs">
                    {repo.private ? "Private" : "Public"}
                  </Badge>
                </div>

                {repo.owner && (
                  <p className="text-xs text-slate-500 mb-2 font-mono">{repo.owner}</p>
                )}

                {repo.description && (
                  <p className="text-xs text-slate-400 line-clamp-2 mb-3 leading-relaxed">
                    {repo.description}
                  </p>
                )}
              </div>

              <div className="pt-3 border-t border-slate-800/60 mt-2">
                <div className="flex items-center justify-between text-[11px] text-slate-400 mb-4">
                  {repo.language ? (
                    <span className="flex items-center gap-1">
                      <span className="w-2 h-2 rounded-full bg-indigo-400" />
                      {repo.language}
                    </span>
                  ) : (
                    <span>General</span>
                  )}
                  {repo.updated_at && (
                    <span>Updated {new Date(repo.updated_at).toLocaleDateString()}</span>
                  )}
                </div>

                <Button
                  variant="primary"
                  size="sm"
                  className="w-full justify-between"
                  loading={selectingId === repo.id}
                  onClick={() => handleSelectGithubRepo(repo)}
                >
                  <span>Open Workspace</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Button>
              </div>
            </div>
          ))}
        </div>
      )}

      <Modal
        isOpen={manualModalOpen}
        onClose={() => setManualModalOpen(false)}
        title="Connect Repository Manually"
        subtitle="Provide a GitHub repository name and repository URL"
      >
        <form onSubmit={handleManualAdd} className="space-y-4">
          {manualError && (
            <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
              <span>{manualError}</span>
            </div>
          )}

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Repository Name</label>
            <input
              type="text"
              required
              value={manualName}
              onChange={(e) => setManualName(e.target.value)}
              placeholder="e.g. reporescue-core"
              className="w-full px-3 py-2 text-xs bg-slate-900 border border-slate-800 rounded-lg text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">GitHub URL</label>
            <input
              type="url"
              required
              value={manualUrl}
              onChange={(e) => setManualUrl(e.target.value)}
              placeholder="https://github.com/owner/repo"
              className="w-full px-3 py-2 text-xs bg-slate-900 border border-slate-800 rounded-lg text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div className="flex items-center justify-end gap-3 pt-3">
            <Button variant="outline" size="sm" onClick={() => setManualModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" variant="primary" size="sm" loading={manualLoading}>
              Connect Repository
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
