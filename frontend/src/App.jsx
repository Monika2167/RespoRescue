
import { useEffect, useState } from "react";
import Login from "./login";
import Signup from "./signup";
import "./App.css";

const API_BASE = "http://127.0.0.1:8000";

function App() {
  const [page, setPage] = useState("login");

  const [userId, setUserId] = useState(
    localStorage.getItem("user_id") || ""
  );
  const [username, setUsername] = useState(
    localStorage.getItem("username") || ""
  );

  const [repoName, setRepoName] = useState("");
  const [repoUrl, setRepoUrl] = useState("");
  const [repositoryId, setRepositoryId] = useState(null);

  const [prNumber, setPrNumber] = useState("");
  const [analysisResult, setAnalysisResult] = useState(null);
  const [history, setHistory] = useState([]);

  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  // Graph & Temporal states
  const [graphData, setGraphData] = useState({
    temporal: [],
    knowledge: [],
    impact: [],
    whatIf: [],
  });

  const [graphTotals, setGraphTotals] = useState({
    temporal: 0,
    knowledge: 0,
    impact: 0,
    whatIf: 0,
  });

  const [graphLoading, setGraphLoading] = useState(false);
  const [graphMessage, setGraphMessage] = useState("");

  const getToken = () => localStorage.getItem("access_token");

  const authHeaders = () => ({
    Authorization: `Bearer ${getToken()}`,
  });

  // Load user's first repository after dashboard opens
  useEffect(() => {
    if (page === "dashboard" && userId) {
      loadRepository();
    }
  }, [page, userId]);

  const loadRepository = async () => {
    try {
      const response = await fetch(
        `${API_BASE}/repositories/${userId}`,
        {
          headers: authHeaders(),
        }
      );

      if (!response.ok) return;

      const data = await response.json();

      if (data.repositories && data.repositories.length > 0) {
        const repo = data.repositories[0];

        setRepositoryId(repo.repository_id);
        setRepoName(repo.name);
        setRepoUrl(repo.github_url);
      }
    } catch (error) {
      console.error("Repository loading error:", error);
    }
  };

  const handleLoginSuccess = (data) => {
  
    localStorage.setItem("access_token", data.access_token);
    localStorage.setItem("user_id", data.user_id);
    localStorage.setItem("username", data.username);
    localStorage.setItem("email", data.email);

    setUserId(data.user_id);
    setUsername(data.username);
    setPage("dashboard");
    setMessage("");
  };

  const handleSignupSuccess = () => {
    setPage("login");
    setMessage("Signup successful! Please login.");
  };

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user_id");
    localStorage.removeItem("username");
    localStorage.removeItem("email");

    setUserId("");
    setUsername("");
    setRepositoryId(null);
    setRepoName("");
    setRepoUrl("");
    setAnalysisResult(null);
    setHistory([]);

    setGraphData({
      temporal: [],
      knowledge: [],
      impact: [],
      whatIf: [],
    });

    setPage("login");
  };

  const addRepository = async () => {
    if (!repoName || !repoUrl) {
      setMessage("Please enter repository name and GitHub URL.");
      return;
    }

    setLoading(true);
    setMessage("");

    try {
      const response = await fetch(`${API_BASE}/repositories`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...authHeaders(),
        },
        body: JSON.stringify({
          name: repoName,
          github_url: repoUrl,
          user_id: Number(userId),
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Failed to add repository");
      }

      setRepositoryId(data.repository_id);
      setRepoName(data.name);
      setRepoUrl(data.github_url);

      setMessage("Repository connected successfully.");
    } catch (error) {
      setMessage(error.message);
    } finally {
      setLoading(false);
    }
  };

  const analyzePR = async () => {
    if (!repositoryId) {
      setMessage("Please connect a repository first.");
      return;
    }

    if (!prNumber) {
      setMessage("Please enter a PR number.");
      return;
    }

    setLoading(true);
    setMessage("");
    setAnalysisResult(null);

    try {
      const response = await fetch(
        `${API_BASE}/repositories/${repositoryId}/analyze/${prNumber}`,
        {
          method: "POST",
          headers: authHeaders(),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Prediction failed");
      }

      setAnalysisResult(data);
      setMessage("PR analysis completed successfully.");

      loadHistory();
    } catch (error) {
      setMessage(error.message);
    } finally {
      setLoading(false);
    }
  };

  const loadHistory = async () => {
    if (!repositoryId) return;

    try {
      const response = await fetch(
        `${API_BASE}/repositories/${repositoryId}/analyses`,
        {
          headers: authHeaders(),
        }
      );

      if (!response.ok) return;

      const data = await response.json();
      setHistory(data.analyses || []);
    } catch (error) {
      console.error("History error:", error);
    }
  };

  // ============================
  // GRAPH & TEMPORAL INTEGRATION
  // ============================

  const loadGraphData = async () => {
    setGraphLoading(true);
    setGraphMessage("");

    try {
      const endpoints = [
        `${API_BASE}/graph/temporal`,
        `${API_BASE}/graph/knowledge-concentration?limit=50&offset=0`,
        `${API_BASE}/graph/impact?limit=50&offset=0`,
        `${API_BASE}/graph/what-if`,
      ];

      const responses = await Promise.all(
        endpoints.map((url) =>
          fetch(url, {
            headers: authHeaders(),
          })
        )
      );

      for (const response of responses) {
        if (!response.ok) {
          throw new Error("Failed to load graph analysis data.");
        }
      }

      const [
        temporalResponse,
        knowledgeResponse,
        impactResponse,
        whatIfResponse,
      ] = responses;

      const temporal = await temporalResponse.json();
      const knowledge = await knowledgeResponse.json();
      const impact = await impactResponse.json();
      const whatIf = await whatIfResponse.json();

      setGraphData({
        temporal: temporal.data || [],
        knowledge: knowledge.data || [],
        impact: impact.data || [],
        whatIf: whatIf.data || [],
      });

      setGraphTotals({
        temporal: temporal.total_records || 0,
        knowledge: knowledge.total_records || 0,
        impact: impact.total_records || 0,
        whatIf: whatIf.total_records || 0,
      });

      setGraphMessage(
        "Graph & Temporal analysis loaded successfully."
      );
    } catch (error) {
      setGraphMessage(error.message);
    } finally {
      setGraphLoading(false);
    }
  };

  const formatNumber = (value) => {
    const number = Number(value);

    if (Number.isFinite(number)) {
      return number.toLocaleString();
    }

    return value ?? "N/A";
  };

  const formatPercent = (value) => {
    const number = Number(value);

    if (Number.isFinite(number)) {
      return `${(number * 100).toFixed(2)}%`;
    }

    return "N/A";
  };

  const sortedKnowledge = [...graphData.knowledge]
    .sort(
      (a, b) =>
        Number(b.dominant_developer_share || 0) -
        Number(a.dominant_developer_share || 0)
    )
    .slice(0, 10);

  const sortedImpact = [...graphData.impact]
    .sort(
      (a, b) =>
        Number(b.impact_weight || 0) -
        Number(a.impact_weight || 0)
    )
    .slice(0, 10);

  const sortedWhatIf = [...graphData.whatIf]
    .sort(
      (a, b) =>
        Number(b.files_with_no_remaining_contributor || 0) -
        Number(a.files_with_no_remaining_contributor || 0)
    )
    .slice(0, 10);

  // ============================
  // LOGIN
  // ============================

  if (page === "login") {
    return (
      <Login
        onLoginSuccess={handleLoginSuccess}
        onSignup={() => setPage("signup")}
        message={message}
      />
    );
  }

  // ============================
  // SIGNUP
  // ============================

  if (page === "signup") {
    return (
      <Signup
        onSignupSuccess={handleSignupSuccess}
        onLogin={() => setPage("login")}
      />
    );
  }

  // ============================
  // DASHBOARD
  // ============================

  return (
    <div className="dashboard">

      {/* NAVBAR */}

      <nav className="navbar">
        <div className="logo">
          RepoRescue
        </div>

        <div className="nav-links">
          <button onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}>
            Dashboard
          </button>

          <button
            onClick={() =>
              document
                .getElementById("graph-analysis")
                ?.scrollIntoView({ behavior: "smooth" })
            }
          >
            Graph Analysis
          </button>

          <button
            onClick={() =>
              document
                .getElementById("history")
                ?.scrollIntoView({ behavior: "smooth" })
            }
          >
            History
          </button>

          <button onClick={handleLogout}>
            Logout
          </button>
        </div>
      </nav>

      {/* HEADER */}

      <div className="dashboard-header">
        <h1>Welcome, {username} 👋</h1>

        <p>
          AI-powered predictive software maintenance platform
        </p>
      </div>

      {/* MESSAGE */}

      {message && (
        <div className="message">
          {message}
        </div>
      )}

      {/* REPOSITORY */}

      <section className="card">
        <h2>🔗 Connect GitHub Repository</h2>

        <input
          type="text"
          placeholder="Repository name"
          value={repoName}
          onChange={(e) => setRepoName(e.target.value)}
        />

        <input
          type="text"
          placeholder="GitHub repository URL"
          value={repoUrl}
          onChange={(e) => setRepoUrl(e.target.value)}
        />

        <button
          className="button"
          onClick={addRepository}
          disabled={loading}
        >
          {loading ? "Connecting..." : "Connect Repository"}
        </button>

        {repositoryId && (
          <div className="repo-info">
            <h3>Connected Repository</h3>
            <p>
              <strong>Name:</strong> {repoName}
            </p>
            <p>
              <strong>URL:</strong> {repoUrl}
            </p>
            <p>
              <strong>Repository ID:</strong> {repositoryId}
            </p>
          </div>
        )}
      </section>

      {/* PR ANALYSIS */}

      <section className="card">
        <h2>🤖 Analyze Pull Request</h2>

        <input
          type="number"
          placeholder="Enter PR number"
          value={prNumber}
          onChange={(e) => setPrNumber(e.target.value)}
        />

        <button
          className="button"
          onClick={analyzePR}
          disabled={loading}
        >
          {loading ? "Analyzing..." : "Analyze PR"}
        </button>
      </section>

      {/* ANALYSIS RESULT */}

      {analysisResult && (
        <section className="card">
          <h2>📊 Prediction Result</h2>

          <div className="cards">

            <div className="small-card">
              <h3>PR Number</h3>
              <p>{analysisResult.pr_number}</p>
            </div>

            <div className="small-card">
              <h3>Probability</h3>
              <p>
                {(
                  Number(analysisResult.probability || 0) * 100
                ).toFixed(2)}
                %
              </p>
            </div>

            <div className="small-card">
              <h3>Prediction</h3>
              <p>{analysisResult.prediction}</p>
            </div>

            <div className="small-card">
              <h3>Threshold</h3>
              <p>{analysisResult.threshold}</p>
            </div>

          </div>

          <div className="repo-info">
            <p>
              <strong>Semantic Signal:</strong>{" "}
              {analysisResult.semantic_signal || "N/A"}
            </p>

            <p>
              <strong>Semantic Strength:</strong>{" "}
              {analysisResult.semantic_strength ?? "N/A"}
            </p>
          </div>

          {analysisResult.top_evidence &&
            analysisResult.top_evidence.length > 0 && (
              <div>
                <h3>Top Evidence</h3>

                <div style={{ overflowX: "auto" }}>
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th>Feature</th>
                        <th>Description</th>
                        <th>Contribution</th>
                        <th>Direction</th>
                        <th>Explanation</th>
                      </tr>
                    </thead>

                    <tbody>
                      {analysisResult.top_evidence.map(
                        (item, index) => (
                          <tr key={index}>
                            <td>{item.feature}</td>
                            <td>{item.description}</td>
                            <td>{item.contribution}</td>
                            <td>{item.direction}</td>
                            <td>{item.explanation}</td>
                          </tr>
                        )
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
        </section>
      )}

      {/* ============================
          GRAPH & TEMPORAL ANALYSIS
          ============================ */}

      <section
        className="card"
        id="graph-analysis"
      >
        <h2>🕸️ Graph & Temporal Analysis</h2>

        <p>
          Integrated outputs from Member 2's Graph and Temporal
          Analysis pipeline.
        </p>

        <button
          className="button"
          onClick={loadGraphData}
          disabled={graphLoading}
        >
          {graphLoading
            ? "Loading Analysis..."
            : "Load Graph & Temporal Analysis"}
        </button>

        {graphMessage && (
          <div className="message">
            {graphMessage}
          </div>
        )}

        {graphTotals.temporal > 0 && (
          <>
            {/* SUMMARY */}

            <div className="cards">

              <div className="small-card">
                <h3>Temporal Records</h3>
                <p>
                  {formatNumber(graphTotals.temporal)}
                </p>
              </div>

              <div className="small-card">
                <h3>Knowledge Files</h3>
                <p>
                  {formatNumber(graphTotals.knowledge)}
                </p>
              </div>

              <div className="small-card">
                <h3>Impact Relations</h3>
                <p>
                  {formatNumber(graphTotals.impact)}
                </p>
              </div>

              <div className="small-card">
                <h3>What-if Records</h3>
                <p>
                  {formatNumber(graphTotals.whatIf)}
                </p>
              </div>

            </div>

            {/* TEMPORAL */}

            <div className="graph-section">
              <h3>📈 Temporal Analysis</h3>

              <p>
                Weekly development activity from the historical
                dataset.
              </p>

              <div style={{ overflowX: "auto" }}>
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Week</th>
                      <th>Commits / Week</th>
                      <th>Active Developers</th>
                      <th>PRs / Week</th>
                      <th>PR Authors</th>
                      <th>Files Changed</th>
                    </tr>
                  </thead>

                  <tbody>
                    {graphData.temporal.map(
                      (row, index) => (
                        <tr key={index}>
                          <td>{row.week}</td>
                          <td>
                            {formatNumber(
                              row.commits_per_week
                            )}
                          </td>
                          <td>
                            {formatNumber(
                              row.active_developers
                            )}
                          </td>
                          <td>
                            {formatNumber(
                              row.prs_per_week
                            )}
                          </td>
                          <td>{row.pr_authors}</td>
                          <td>
                            {formatNumber(
                              row.files_changed_per_week
                            )}
                          </td>
                        </tr>
                      )
                    )}
                  </tbody>
                </table>
              </div>
            </div>

            {/* KNOWLEDGE CONCENTRATION */}

            <div className="graph-section">
              <h3>👥 Knowledge Concentration</h3>

              <p>
                Files with higher dominant developer share indicate
                stronger historical concentration of contribution.
              </p>

              <div style={{ overflowX: "auto" }}>
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>File</th>
                      <th>Dominant Developer</th>
                      <th>Developer Share</th>
                      <th>Total Commits</th>
                      <th>Unique Developers</th>
                      <th>Concentration</th>
                    </tr>
                  </thead>

                  <tbody>
                    {sortedKnowledge.map(
                      (row, index) => (
                        <tr key={index}>
                          <td>{row.file_name}</td>
                          <td>
                            {row.dominant_developer}
                          </td>
                          <td>
                            {formatPercent(
                              row.dominant_developer_share
                            )}
                          </td>
                          <td>
                            {formatNumber(
                              row.total_file_commits
                            )}
                          </td>
                          <td>
                            {formatNumber(
                              row.unique_developers_per_file
                            )}
                          </td>
                          <td>
                            {row.contributor_concentration ??
                              "N/A"}
                          </td>
                        </tr>
                      )
                    )}
                  </tbody>
                </table>
              </div>
            </div>

            {/* IMPACT ANALYSIS */}

            <div className="graph-section">
              <h3>🔗 Historical File Impact</h3>

              <p>
                These relationships represent historical file
                co-change frequency, not guaranteed source-code
                dependency.
              </p>

              <div style={{ overflowX: "auto" }}>
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Source File</th>
                      <th>Target File</th>
                      <th>Co-change Frequency</th>
                      <th>Impact Weight</th>
                    </tr>
                  </thead>

                  <tbody>
                    {sortedImpact.map(
                      (row, index) => (
                        <tr key={index}>
                          <td>{row.source_file}</td>
                          <td>{row.target_file}</td>
                          <td>
                            {formatNumber(
                              row.cochange_frequency
                            )}
                          </td>
                          <td>
                            {row.impact_weight}
                          </td>
                        </tr>
                      )
                    )}
                  </tbody>
                </table>
              </div>
            </div>

            {/* WHAT-IF */}

            <div className="graph-section">
              <h3>🔮 What-if Knowledge Loss Simulation</h3>

              <p>
                Simulation of the effect of removing the dominant
                contributor from a file. This is a what-if analysis,
                not a prediction that a developer will actually leave.
              </p>

              <div style={{ overflowX: "auto" }}>
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>File</th>
                      <th>Dominant Developer</th>
                      <th>Developer Share</th>
                      <th>Total Commits</th>
                      <th>Unique Developers</th>
                      <th>Files Losing Contributor</th>
                      <th>No Remaining Contributor</th>
                      <th>High Concentration</th>
                    </tr>
                  </thead>

                  <tbody>
                    {sortedWhatIf.map(
                      (row, index) => (
                        <tr key={index}>
                          <td>{row.file_name}</td>
                          <td>
                            {row.dominant_developer}
                          </td>
                          <td>
                            {formatPercent(
                              row.dominant_developer_share
                            )}
                          </td>
                          <td>
                            {formatNumber(row.total_commits)}
                          </td>
                          <td>
                            {formatNumber(
                              row.unique_developers
                            )}
                          </td>
                          <td>
                            {formatNumber(
                              row.files_losing_dominant_contributor
                            )}
                          </td>
                          <td>
                            {formatNumber(
                              row.files_with_no_remaining_contributor
                            )}
                          </td>
                          <td>
                            {String(
                              row.high_concentration_flag
                            )}
                          </td>
                        </tr>
                      )
                    )}
                  </tbody>
                </table>
              </div>
            </div>

            {/* DATA LIMITATION */}

            <div className="repo-info">
              <strong>Data limitation:</strong>

              <p>
                The current graph CSV outputs do not contain a
                repository identifier. Therefore these graph results
                are not independently filterable by repository.
              </p>
            </div>
          </>
        )}
      </section>

      {/* ============================
          ANALYSIS HISTORY
          ============================ */}

      <section
        className="card"
        id="history"
      >
        <h2>📚 Analysis History</h2>

        <button
          className="button"
          onClick={loadHistory}
          disabled={!repositoryId}
        >
          Refresh History
        </button>

        {history.length === 0 ? (
          <p>No analysis history available.</p>
        ) : (
          <div style={{ overflowX: "auto" }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>PR</th>
                  <th>Probability</th>
                  <th>Prediction</th>
                  <th>Threshold</th>
                  <th>Semantic Signal</th>
                  <th>Created At</th>
                </tr>
              </thead>

              <tbody>
                {history.map((item) => (
                  <tr key={item.analysis_id}>
                    <td>{item.pr_number}</td>

                    <td>
                      {(
                        Number(item.probability || 0) *
                        100
                      ).toFixed(2)}
                      %
                    </td>

                    <td>{item.prediction}</td>

                    <td>{item.threshold}</td>

                    <td>
                      {item.semantic_signal || "N/A"}
                    </td>

                    <td>{item.created_at}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {/* SETTINGS */}

      <section className="card">
        <h2>⚙️ Settings</h2>

        <p>
          Settings will be available soon.
        </p>
      </section>

    </div>
  );
}

export default App;

