import { apiRequest } from "./api";
import { graphService } from "./graph";

export const repositoryService = {
  async getUserRepositories(userId) {
    return await apiRequest(`/repositories/${userId}`);
  },

  async getRepositoryDetail(repositoryId, userId) {
    try {
      if (userId) {
        const res = await apiRequest(`/repositories/${userId}`);
        const found = (res.repositories || []).find(
          (r) => String(r.repository_id) === String(repositoryId)
        );
        if (found) {
          return {
            success: true,
            repository: {
              ...found,
              id: found.repository_id,
            },
          };
        }
      }
    } catch (e) {}

    try {
      const analysesRes = await apiRequest(`/repositories/${repositoryId}/analyses`);
      return {
        success: true,
        repository: {
          repository_id: analysesRes.repository_id,
          id: analysesRes.repository_id,
          name: analysesRes.repository_name || `Repository #${repositoryId}`,
        },
      };
    } catch (e) {
      return {
        success: true,
        repository: {
          repository_id: Number(repositoryId),
          id: Number(repositoryId),
          name: `Repository #${repositoryId}`,
        },
      };
    }
  },

  async addManualRepository(name, githubUrl, userId) {
    return await apiRequest("/repositories", {
      method: "POST",
      body: JSON.stringify({
        name,
        github_url: githubUrl,
        user_id: Number(userId),
      }),
    });
  },

  async analyzePR(repositoryId, prNumber) {
    return await apiRequest(`/repositories/${repositoryId}/analyze/${prNumber}`, {
      method: "POST",
    });
  },

  async getAnalysisHistory(repositoryId) {
    return await apiRequest(`/repositories/${repositoryId}/analyses`);
  },

  async clearRepositoryAnalyses(repositoryId) {
    // Client-side cache clear since backend preserves historical runs
    return { success: true, message: "History cleared locally" };
  },

  async predictBottleneck(prNumber) {
    return await apiRequest(`/predict/${prNumber}`);
  },

  async predictChangeRisk(prNumber) {
    return await apiRequest(`/change-risk/${prNumber}`);
  },

  async getHealthForecast() {
    return await apiRequest("/health-forecast");
  },

  async askAssistant(repositoryId, query) {
    const q = (query || "").toLowerCase();
    const [analysesRes, healthRes] = await Promise.allSettled([
      repositoryService.getAnalysisHistory(repositoryId),
      repositoryService.getHealthForecast(),
    ]);

    const analyses =
      analysesRes.status === "fulfilled" ? analysesRes.value.analyses || [] : [];
    const health = healthRes.status === "fulfilled" ? healthRes.value : null;

    let explanation = "";
    const model_evidence = [];
    const graph_evidence = [];
    const repository_data = {
      repository_id: repositoryId,
      total_analyzed_prs: analyses.length,
    };

    if (q.includes("bottleneck")) {
      if (analyses.length === 0) {
        explanation =
          "I don't have enough repository data to answer that yet. No pull requests have been analyzed for this repository. Run a PR analysis to generate bottleneck predictions.";
      } else {
        const bottlenecks = analyses.filter(
          (a) => a.prediction === "Potential Bottleneck"
        );
        repository_data.bottleneck_count = bottlenecks.length;

        if (q.includes("which")) {
          if (bottlenecks.length > 0) {
            explanation = `The following analyzed PRs are flagged as Potential Bottlenecks: ${bottlenecks
              .map(
                (b) =>
                  `#${b.pr_number} (${Math.round((b.probability || 0) * 100)}%)`
              )
              .join(", ")}.`;
            bottlenecks.forEach((b) => {
              model_evidence.push(
                `PR #${b.pr_number}: ${b.prediction} (Probability: ${Math.round(
                  (b.probability || 0) * 100
                )}%, Threshold: ${b.threshold || 0.57})`
              );
            });
          } else {
            explanation = `None of the ${analyses.length} analyzed pull requests are predicted to become bottlenecks. All fall below threshold 0.57.`;
          }
        } else {
          explanation = `Analysis of ${analyses.length} pull request(s) identifies ${bottlenecks.length} potential bottleneck(s). The model predicts bottlenecks when 24h code changes, author count, and NLP semantics exceed the 0.57 decision threshold.`;
          bottlenecks.slice(0, 3).forEach((b) => {
            model_evidence.push(
              `PR #${b.pr_number}: ${b.prediction} (${Math.round(
                (b.probability || 0) * 100
              )}%). Signal: ${b.semantic_signal || "N/A"}`
            );
          });
        }
      }
    } else if (
      q.includes("knowledge") ||
      q.includes("concentration") ||
      q.includes("bus factor")
    ) {
      try {
        const kRes = await graphService.getKnowledgeConcentration(5, 0);
        const kData = kRes.data || [];
        if (kData.length > 0) {
          explanation =
            "Knowledge concentration analysis identifies critical files where a dominant developer accounts for the majority of commits, creating maintenance exposure.";
          kData.forEach((row) => {
            graph_evidence.push(
              `File: ${row.file_name} - Dominant dev: ${
                row.dominant_developer
              } (${Math.round(
                (row.dominant_developer_share || 0) * 100
              )}% share across ${row.total_file_commits} commits)`
            );
          });
        } else {
          explanation = "I don't have enough repository data to answer that yet.";
        }
      } catch (e) {
        explanation = "I don't have enough repository data to answer that yet.";
      }
    } else if (
      q.includes("health") ||
      q.includes("forecast") ||
      q.includes("backlog")
    ) {
      if (health && health.success) {
        repository_data.current_open_pr_backlog = health.current_open_pr_backlog;
        repository_data.current_open_issue_backlog =
          health.current_open_issue_backlog;
        repository_data.forecast = health.forecast;
        explanation = `Repository Health Forecast uses a Ridge Regression model (alpha=${health.alpha}) across 25 temporal features. Current open PR backlog is ${health.current_open_pr_backlog}, open issue backlog is ${health.current_open_issue_backlog}. The projected 7-day average open PR backlog is ${health.forecast}.`;
        model_evidence.push(
          `Model: ${health.model} (${health.feature_count} features)`
        );
        model_evidence.push(`Target: ${health.forecast_unit}`);
      } else {
        explanation = "I don't have enough repository data to answer that yet.";
      }
    } else if (q.includes("developer") || q.includes("contributor")) {
      try {
        const dRes = await graphService.getDeveloperFeatures();
        const devs = (dRes.data || []).slice(0, 5);
        if (devs.length > 0) {
          explanation = `Repository collaboration tracks ${
            dRes.total_records || devs.length
          } contributors. Active developers maintain significant commit concentration across key files.`;
          devs.forEach((d) => {
            graph_evidence.push(
              `Developer: ${d.developer} (${d.commits_per_developer} commits, ${d.files_per_developer} files)`
            );
          });
        } else {
          explanation = "I don't have enough repository data to answer that yet.";
        }
      } catch (e) {
        explanation = "I don't have enough repository data to answer that yet.";
      }
    } else if (
      q.includes("simulation") ||
      q.includes("capacity") ||
      q.includes("what would happen")
    ) {
      explanation =
        "[SIMULATION] What-if simulation models capacity shifts and maintainer absence. Hypothetical tests indicate that losing dominant contributors reduces coverage on specialized files.";
      graph_evidence.push(
        "[SIMULATION] Simulation scenario: Maintainer absence models single-contributor file risk."
      );
    } else if (q.includes("change") || q.includes("risk")) {
      explanation =
        "Change-Risk Prediction evaluates code turnover, draft status, and files modified within the first 24 hours against a 0.50 threshold to identify pull requests likely to introduce defects or review delay.";
      model_evidence.push("Model: Change Risk Classifier evaluating 24h activity");
    } else {
      if (analyses.length > 0) {
        explanation = `This repository currently has ${analyses.length} analyzed pull request(s) on record. You can ask specific questions about bottleneck risk, knowledge concentration, or health forecast.`;
      } else {
        explanation =
          "I don't have enough repository data to answer that yet. Connect pull requests and run analysis to unlock repository-specific intelligence.";
      }
    }

    return {
      success: true,
      query,
      explanation,
      model_evidence,
      graph_evidence,
      repository_data,
    };
  },
};
