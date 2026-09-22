import React, { useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { FolderGit2, CheckCircle2, Plus } from "lucide-react";
import { Github } from "../components/common/GithubIcon";
import { useAuth } from "../context/AuthContext";
import { useRepo } from "../context/RepoContext";
import { Card } from "../components/common/Card";
import { Button } from "../components/common/Button";
import { EmptyState } from "../components/common/EmptyState";
import { Badge } from "../components/common/Badge";
import { RepoCard } from "../components/repository/RepoCard";

export const Dashboard = () => {
  const { user } = useAuth();
  const {
    repositories,
    selectedRepo,
    selectRepo,
    githubStatus,
    refreshGithub,
    refreshRepos,
  } = useRepo();
  const navigate = useNavigate();

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (params.get("github") === "connected") {
      refreshGithub();
      refreshRepos();
      window.history.replaceState({}, document.title, window.location.pathname);
    }
  }, [refreshGithub, refreshRepos]);

  const handleSelect = (repo) => {
    selectRepo(repo);
    navigate(`/repositories/${repo.repository_id || repo.id}`);
  };

  return (
    <div className="space-y-8 animate-fade-in">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800/80 pb-6">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold tracking-tight text-white">
            Welcome to RepoRescue, {user?.username || "Developer"} 👋
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Personalized software intelligence for your GitHub repositories.
          </p>
        </div>

        {githubStatus.github_connected ? (
          <div className="flex items-center gap-3">
            <Badge variant="success" size="md" icon={CheckCircle2}>
              GitHub Connected: {githubStatus.username}
            </Badge>
            <Link to="/repositories">
              <Button variant="outline" size="sm" icon={FolderGit2}>
                View My Repositories
              </Button>
            </Link>
          </div>
        ) : (
          <Link to="/settings">
            <Button variant="primary" size="md" icon={Github}>
              Connect GitHub Account
            </Button>
          </Link>
        )}
      </div>

      {!githubStatus.github_connected ? (
        <EmptyState
          icon={Github}
          title="Connect your GitHub account to start analyzing your repositories."
          description="RepoRescue derives all risk predictions, health forecasts, and graph intelligence from your real repository activity. No data has been connected yet."
          action={
            <Link to="/settings">
              <Button variant="primary" size="md" icon={Github}>
                Connect GitHub
              </Button>
            </Link>
          }
          secondaryAction={
            <Link to="/help">
              <Button variant="outline" size="md">
                Learn How It Works
              </Button>
            </Link>
          }
          className="my-8"
        />
      ) : repositories.length === 0 ? (
        <EmptyState
          icon={FolderGit2}
          title="GitHub is connected! Select a repository to begin."
          description={`Your GitHub account (@${githubStatus.username}) is connected. Choose a repository from your GitHub account to initialize its analysis workspace.`}
          action={
            <Link to="/repositories">
              <Button variant="primary" size="md" icon={FolderGit2}>
                Explore My Repositories
              </Button>
            </Link>
          }
        />
      ) : (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold text-slate-100">
                Active Repository Workspaces
              </h2>
              <p className="text-xs text-slate-400">
                Select a repository below to explore its machine learning risk predictions and graph intelligence.
              </p>
            </div>
            <Link to="/repositories">
              <Button variant="outline" size="sm" icon={Plus}>
                Add / Select More Repositories
              </Button>
            </Link>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {repositories.map((repo) => (
              <RepoCard
                key={repo.repository_id || repo.id}
                repo={repo}
                isSelected={
                  selectedRepo &&
                  (selectedRepo.repository_id || selectedRepo.id) ===
                    (repo.repository_id || repo.id)
                }
                onSelect={handleSelect}
              />
            ))}
          </div>

          {selectedRepo && (
            <Card
              title={`Quick Workspace: ${selectedRepo.name}`}
              subtitle="Direct shortcuts to repository intelligence tools"
              headerAction={
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() =>
                    navigate(`/repositories/${selectedRepo.repository_id || selectedRepo.id}`)
                  }
                >
                  Open Workspace
                </Button>
              }
            >
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-3 text-center">
                <Link
                  to={`/repositories/${selectedRepo.repository_id || selectedRepo.id}/risk/bottleneck`}
                  className="p-3 bg-slate-900/60 border border-slate-800 hover:border-indigo-500/40 rounded-xl transition group"
                >
                  <div className="text-xs font-semibold text-slate-200 group-hover:text-indigo-300">
                    Bottlenecks
                  </div>
                  <div className="text-[10px] text-slate-500 mt-1">PR Predictor</div>
                </Link>

                <Link
                  to={`/repositories/${selectedRepo.repository_id || selectedRepo.id}/risk/change`}
                  className="p-3 bg-slate-900/60 border border-slate-800 hover:border-indigo-500/40 rounded-xl transition group"
                >
                  <div className="text-xs font-semibold text-slate-200 group-hover:text-indigo-300">
                    Change Risk
                  </div>
                  <div className="text-[10px] text-slate-500 mt-1">24h ML Model</div>
                </Link>

                <Link
                  to={`/repositories/${selectedRepo.repository_id || selectedRepo.id}/health`}
                  className="p-3 bg-slate-900/60 border border-slate-800 hover:border-indigo-500/40 rounded-xl transition group"
                >
                  <div className="text-xs font-semibold text-slate-200 group-hover:text-indigo-300">
                    Health
                  </div>
                  <div className="text-[10px] text-slate-500 mt-1">Ridge Forecast</div>
                </Link>

                <Link
                  to={`/repositories/${selectedRepo.repository_id || selectedRepo.id}/graph`}
                  className="p-3 bg-slate-900/60 border border-slate-800 hover:border-indigo-500/40 rounded-xl transition group"
                >
                  <div className="text-xs font-semibold text-slate-200 group-hover:text-indigo-300">
                    Graph
                  </div>
                  <div className="text-[10px] text-slate-500 mt-1">Explorer</div>
                </Link>

                <Link
                  to={`/repositories/${selectedRepo.repository_id || selectedRepo.id}/simulation`}
                  className="p-3 bg-slate-900/60 border border-slate-800 hover:border-indigo-500/40 rounded-xl transition group"
                >
                  <div className="text-xs font-semibold text-slate-200 group-hover:text-indigo-300">
                    Simulation
                  </div>
                  <div className="text-[10px] text-slate-500 mt-1">What-If Models</div>
                </Link>

                <Link
                  to={`/repositories/${selectedRepo.repository_id || selectedRepo.id}/assistant`}
                  className="p-3 bg-indigo-950/40 border border-indigo-500/30 hover:border-indigo-400 rounded-xl transition group"
                >
                  <div className="text-xs font-semibold text-indigo-300 group-hover:text-white">
                    AI Assistant
                  </div>
                  <div className="text-[10px] text-indigo-400 mt-1">Repo Specific</div>
                </Link>
              </div>
            </Card>
          )}
        </div>
      )}
    </div>
  );
};
