import { apiRequest } from "./api";

export const graphService = {
  async getNodes(limit = 50, offset = 0) {
    return await apiRequest(`/graph/nodes?limit=${limit}&offset=${offset}`);
  },

  async getEdges(limit = 50, offset = 0) {
    return await apiRequest(`/graph/edges?limit=${limit}&offset=${offset}`);
  },

  async getImpact(limit = 50, offset = 0) {
    return await apiRequest(`/graph/impact?limit=${limit}&offset=${offset}`);
  },

  async getKnowledgeConcentration(limit = 50, offset = 0) {
    return await apiRequest(`/graph/knowledge-concentration?limit=${limit}&offset=${offset}`);
  },

  async getTemporalFeatures() {
    return await apiRequest("/graph/temporal");
  },

  async getWhatIfResults() {
    return await apiRequest("/graph/what-if");
  },

  async getDeveloperFeatures() {
    return await apiRequest("/graph/developers");
  },

  async getDeveloperFileRelationships(limit = 50, offset = 0) {
    return await apiRequest(`/graph/developer-file?limit=${limit}&offset=${offset}`);
  },

  async getFileFeatures() {
    return await apiRequest("/graph/file-features");
  },
};
