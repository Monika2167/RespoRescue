import { apiRequest, API_BASE, getToken } from "./api";

export const githubService = {
  async getStatus() {
    try {
      const res = await apiRequest("/auth/github/repositories");
      const repos = res.repositories || [];
      const username = repos.length > 0 ? (repos[0].owner || "Connected") : "Connected";
      return {
        github_connected: true,
        username: username,
        repositories: repos,
      };
    } catch (err) {
      return {
        github_connected: false,
        username: null,
        repositories: [],
      };
    }
  },

  getOAuthUrl() {
    const token = getToken();
    if (!token) throw new Error("Please log in first.");
    return `${API_BASE}/auth/github/login?token=${encodeURIComponent(token)}`;
  },

  async getAuthorizedRepositories() {
    return await apiRequest("/auth/github/repositories");
  },

  async selectRepository(githubRepoId) {
    return await apiRequest(`/auth/github/select-repository?github_repo_id=${githubRepoId}`, {
      method: "POST",
    });
  },
};
