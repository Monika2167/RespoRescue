import React, { createContext, useContext, useState, useEffect, useCallback } from "react";
import { useAuth } from "./AuthContext";
import { repositoryService } from "../services/repository";
import { githubService } from "../services/github";

const RepoContext = createContext(null);

export const RepoProvider = ({ children }) => {
  const { user, isAuthenticated } = useAuth();
  const [repositories, setRepositories] = useState([]);
  const [selectedRepo, setSelectedRepo] = useState(null);
  const [githubStatus, setGithubStatus] = useState({ github_connected: false, username: null });
  const [githubRepos, setGithubRepos] = useState([]);
  const [loadingRepos, setLoadingRepos] = useState(false);
  const [loadingGithub, setLoadingGithub] = useState(false);

  const fetchGithubStatus = useCallback(async () => {
    if (!isAuthenticated) return;
    try {
      const status = await githubService.getStatus();
      setGithubStatus(status);
      if (status.github_connected) {
        fetchGithubRepos();
      }
    } catch (err) {
      setGithubStatus({ github_connected: false, username: null });
    }
  }, [isAuthenticated]);

  const fetchGithubRepos = useCallback(async () => {
    if (!isAuthenticated) return;
    try {
      setLoadingGithub(true);
      const res = await githubService.getAuthorizedRepositories();
      setGithubRepos(res.repositories || []);
    } catch (err) {
      setGithubRepos([]);
    } finally {
      setLoadingGithub(false);
    }
  }, [isAuthenticated]);

  const fetchUserRepositories = useCallback(async () => {
    if (!isAuthenticated || !user?.user_id) return;
    try {
      setLoadingRepos(true);
      const res = await repositoryService.getUserRepositories(user.user_id);
      const list = res.repositories || [];
      setRepositories(list);

      const storedId = localStorage.getItem("selected_repo_id");
      if (storedId) {
        const found = list.find((r) => String(r.repository_id) === String(storedId));
        if (found) setSelectedRepo(found);
      } else if (list.length > 0 && !selectedRepo) {
        setSelectedRepo(list[0]);
      }
    } catch (err) {
      setRepositories([]);
    } finally {
      setLoadingRepos(false);
    }
  }, [isAuthenticated, user?.user_id, selectedRepo]);

  useEffect(() => {
    if (isAuthenticated) {
      fetchGithubStatus();
      fetchUserRepositories();
    } else {
      setRepositories([]);
      setSelectedRepo(null);
      setGithubStatus({ github_connected: false, username: null });
      setGithubRepos([]);
    }
  }, [isAuthenticated, fetchGithubStatus, fetchUserRepositories]);

  const selectRepo = (repo) => {
    setSelectedRepo(repo);
    if (repo?.repository_id) {
      localStorage.setItem("selected_repo_id", String(repo.repository_id));
    }
  };

  return (
    <RepoContext.Provider
      value={{
        repositories,
        selectedRepo,
        selectRepo,
        githubStatus,
        githubRepos,
        loadingRepos,
        loadingGithub,
        refreshRepos: fetchUserRepositories,
        refreshGithub: fetchGithubStatus,
        fetchGithubRepos,
      }}
    >
      {children}
    </RepoContext.Provider>
  );
};

export const useRepo = () => {
  const context = useContext(RepoContext);
  if (!context) throw new Error("useRepo must be used within a RepoProvider");
  return context;
};
