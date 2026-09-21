import React from "react";
import { Star, GitFork, AlertCircle, Calendar, ArrowRight } from "lucide-react";
import { Github } from "../common/GithubIcon";
import { Badge } from "../common/Badge";
import { Button } from "../common/Button";

export const RepoCard = ({ repo, onSelect, isSelected = false }) => {
  return (
    <div className="bg-[#111726] border border-slate-800/90 hover:border-indigo-500/40 rounded-xl p-5 shadow-lg shadow-black/30 transition duration-200 flex flex-col justify-between group">
      <div>
        <div className="flex items-start justify-between gap-3 mb-2.5">
          <div className="flex items-center gap-2">
            <Github className="w-4 h-4 text-slate-400 group-hover:text-indigo-400 transition" />
            <h3 className="text-base font-semibold text-slate-100 group-hover:text-indigo-300 transition truncate">
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
          <p className="text-xs text-slate-400 line-clamp-2 mb-4 leading-relaxed">
            {repo.description}
          </p>
        )}
      </div>

      <div className="pt-4 border-t border-slate-800/60 mt-2">
        <div className="flex items-center justify-between text-xs text-slate-400 mb-4 flex-wrap gap-2">
          {repo.language && (
            <div className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-indigo-400" />
              <span>{repo.language}</span>
            </div>
          )}
          {repo.stargazers_count !== undefined && (
            <div className="flex items-center gap-1">
              <Star className="w-3.5 h-3.5 text-amber-400" />
              <span>{repo.stargazers_count}</span>
            </div>
          )}
          {repo.updated_at && (
            <div className="flex items-center gap-1 text-[11px] text-slate-500">
              <Calendar className="w-3 h-3" />
              <span>{new Date(repo.updated_at).toLocaleDateString()}</span>
            </div>
          )}
        </div>

        <Button
          variant={isSelected ? "secondary" : "primary"}
          size="sm"
          className="w-full justify-between"
          onClick={() => onSelect(repo)}
        >
          <span>{isSelected ? "Current Workspace" : "Open Workspace"}</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </Button>
      </div>
    </div>
  );
};
