import React from "react";
import { ExternalLink, Play, Clock, GitBranch } from "lucide-react";
import { Github } from "../common/GithubIcon";
import { Badge } from "../common/Badge";
import { Button } from "../common/Button";

export const RepoWorkspaceHeader = ({
  repository,
  onAnalyzeClick,
  loading = false,
}) => {
  if (!repository) return null;

  return (
    <div className="bg-[#0f1523] border border-slate-800 rounded-2xl p-6 mb-6 shadow-xl">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-start gap-4">
          <div className="w-12 h-12 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-center text-indigo-400 shrink-0 shadow-inner">
            <Github className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2.5 flex-wrap mb-1">
              <h1 className="text-xl font-bold text-slate-100 tracking-tight">
                {repository.name}
              </h1>
              <Badge variant="neutral" size="xs">
                {repository.private ? "Private" : "Public"}
              </Badge>
              {repository.last_analyzed && (
                <Badge variant="info" size="xs" icon={Clock}>
                  Analyzed {new Date(repository.last_analyzed).toLocaleDateString()}
                </Badge>
              )}
            </div>
            <div className="flex items-center gap-3 text-xs text-slate-400">
              {repository.github_url && (
                <a
                  href={repository.github_url}
                  target="_blank"
                  rel="noreferrer"
                  className="hover:text-indigo-400 flex items-center gap-1 transition"
                >
                  <span>{repository.github_url}</span>
                  <ExternalLink className="w-3 h-3" />
                </a>
              )}
            </div>
          </div>
        </div>

        {onAnalyzeClick && (
          <div className="flex items-center gap-3">
            <Button
              variant="primary"
              size="md"
              icon={Play}
              loading={loading}
              onClick={onAnalyzeClick}
            >
              Analyze Pull Request
            </Button>
          </div>
        )}
      </div>
    </div>
  );
};
