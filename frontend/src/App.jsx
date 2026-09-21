import { useEffect, useState } from "react";
import Login from "./login";
import Signup from "./signup";
import "./App.css";

const API_BASE = "http://127.0.0.1:8001";

function App() {
  const [page, setPage] = useState(
    localStorage.getItem("access_token") ? "dashboard" : "login"
  );

  const [userId, setUserId] = useState(
    localStorage.getItem("user_id") || ""
  );

  const [username, setUsername] = useState(
    localStorage.getItem("username") || ""
  );

  const [email, setEmail] = useState(
    localStorage.getItem("email") || ""
  );

  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const [repoName, setRepoName] = useState("");
  const [repoUrl, setRepoUrl] = useState("");
  const [repositoryId, setRepositoryId] = useState(null);

  const [githubRepos, setGithubRepos] = useState([]);
  const [githubConnected, setGithubConnected] = useState(false);
  const [selectedGithubRepo, setSelectedGithubRepo] = useState(null);
  const [githubLoading, setGithubLoading] = useState(false);

  const [prNumber, setPrNumber] = useState("");
  const [analysisResult, setAnalysisResult] = useState(null);
  const [history, setHistory] = useState([]);

  const [graphData, setGraphData] = useState({
    temporal: [],
    knowledge: [],
    impact: [],
    whatIf: [],
    developerFile: [],
    nodes: [],
    edges: [],
  });

  const [graphLoading, setGraphLoading] = useState(false);
  const [graphMessage, setGraphMessage] = useState("");

  const [settings, setSettings] = useState({
    notifications: true,
    compactMode: false,
  });

  const getToken = () => {
    return localStorage.getItem("access_token");
  };

  const authHeaders = () => {
    const token = getToken();

    return {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    };
  };

  const apiRequest = async (url, options = {}) => {
    const response = await fetch(url, {
      ...options,
      headers: {
        ...authHeaders(),
        ...(options.headers || {}),
      },
    });

    let data = {};

    try {
      data = await response.json();
    } catch {
      data = {};
    }

    if (!response.ok) {
      throw new Error(
        data.detail ||
          data.message ||
          "Request failed"
      );
    }

    return data;
  };

  // =========================
  // LOGIN
  // =========================

  const handleLoginSuccess = (data) => {
    localStorage.setItem(
      "access_token",
      data.access_token
    );

    localStorage.setItem(
      "user_id",
      String(data.user_id)
    );

    localStorage.setItem(
      "username",
      data.username || ""
    );

    localStorage.setItem(
      "email",
      data.email || ""
    );

    setUserId(String(data.user_id));
    setUsername(data.username || "");
    setEmail(data.email || "");

    setPage("dashboard");
    setMessage("");
  };

  // =========================
  // LOGOUT
  // =========================

  const logout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user_id");
    localStorage.removeItem("username");
    localStorage.removeItem("email");

    setUserId("");
    setUsername("");
    setEmail("");

    setRepositoryId(null);
    setRepoName("");
    setRepoUrl("");

    setGithubRepos([]);
    setGithubConnected(false);
    setSelectedGithubRepo(null);

    setAnalysisResult(null);
    setHistory([]);

    setPage("login");
    setMessage("");
  };

  // =========================
  // LOAD USER REPOSITORY
  // =========================

  const loadRepository = async () => {
    if (!userId || !getToken()) {
      return;
    }

    try {
      const data = await apiRequest(
        `${API_BASE}/repositories/${userId}`
      );

      if (
        data.repositories &&
        data.repositories.length > 0
      ) {
        const repo = data.repositories[0];

        setRepositoryId(repo.repository_id);
        setRepoName(repo.name || "");
        setRepoUrl(repo.github_url || "");
      }
    } catch (error) {
      console.error(
        "Repository loading error:",
        error
      );
    }
  };

  // =========================
  // MANUAL REPOSITORY
  // =========================

  const addRepository = async () => {
    if (!repoName || !repoUrl) {
      setMessage(
        "Please enter repository name and GitHub URL."
      );
      return;
    }

    if (!userId) {
      setMessage("Please login first.");
      return;
    }

    try {
      setLoading(true);
      setMessage("");

      const data = await apiRequest(
        `${API_BASE}/repositories`,
        {
          method: "POST",
          body: JSON.stringify({
            name: repoName,
            github_url: repoUrl,
            user_id: Number(userId),
          }),
        }
      );

      if (data.repository) {
        setRepositoryId(
          data.repository.repository_id ||
            data.repository.id
        );

        setRepoName(
          data.repository.name || repoName
        );

        setRepoUrl(
          data.repository.github_url || repoUrl
        );
      }

      setMessage(
        "Repository connected successfully."
      );
    } catch (error) {
      console.error(
        "Repository connection error:",
        error
      );

      setMessage(
        error.message ||
          "Unable to connect repository."
      );
    } finally {
      setLoading(false);
    }
  };

  // =========================
  // GITHUB CONNECT
  // =========================

  const connectGitHub = () => {
    const token = getToken();

    if (!token) {
      setMessage("Please login first.");
      return;
    }

    setGithubLoading(true);

    window.location.href =
      `${API_BASE}/auth/github/login?token=${encodeURIComponent(
        token
      )}`;
  };

  // =========================
  // LOAD GITHUB REPOSITORIES
  // =========================

  const loadGithubRepositories = async () => {
    try {
      setGithubLoading(true);
      setMessage("");

      const data = await apiRequest(
        `${API_BASE}/auth/github/repositories`
      );

      setGithubRepos(
        data.repositories || []
      );

      setGithubConnected(
        data.github_connected === true
      );
    } catch (error) {
      console.error(
        "GitHub repositories error:",
        error
      );

      setGithubConnected(false);

      setMessage(
        error.message ||
          "Unable to load GitHub repositories."
      );
    } finally {
      setGithubLoading(false);
    }
  };

  // =========================
  // SELECT GITHUB REPOSITORY
  // =========================

  const selectGithubRepository = async (
    githubRepoId
  ) => {
    if (!githubRepoId) {
      setMessage(
        "Please select a GitHub repository."
      );
      return;
    }

    try {
      setGithubLoading(true);
      setMessage("");

      const data = await apiRequest(
        `${API_BASE}/auth/github/select-repository?github_repo_id=${githubRepoId}`,
        {
          method: "POST",
        }
      );

      if (data.repository) {
        setRepositoryId(
          data.repository.id
        );

        setRepoName(
          data.repository.name || ""
        );

        setRepoUrl(
          data.repository.github_url || ""
        );

        setSelectedGithubRepo(
          data.repository
        );
      }

      setMessage(
        "GitHub repository selected successfully."
      );
    } catch (error) {
      console.error(
        "Repository selection error:",
        error
      );

      setMessage(
        error.message ||
          "Unable to select repository."
      );
    } finally {
      setGithubLoading(false);
    }
  };

  // =========================
  // PR ANALYSIS
  // =========================

  const analyzePR = async () => {
    if (!prNumber) {
      setMessage(
        "Please enter a PR number."
      );
      return;
    }

    try {
      setLoading(true);
      setMessage("");
      setAnalysisResult(null);

      if (!repositoryId) {
        setMessage("Please connect a repository first.");
        return;
      }

      const data = await apiRequest(
        `${API_BASE}/repositories/${repositoryId}/analyze/${prNumber}`,
        {
          method: "POST"
        }
      );

      setAnalysisResult(data);

      setMessage(
        "PR analysis completed successfully."
      );

      // Wait for state/repository to be available
      if (repositoryId) {
        await loadHistory();
      }
    } catch (error) {
      console.error(
        "Prediction error:",
        error
      );

      setMessage(
        error.message ||
          "Unable to analyze PR."
      );
    } finally {
      setLoading(false);
    }
  };

  // =========================
  // ANALYSIS HISTORY
  // =========================

  const loadHistory = async () => {
    if (!repositoryId) {
      console.log(
        "History skipped: repositoryId missing"
      );
      return;
    }

    try {
      console.log(
        "Loading analysis history for repository:",
        repositoryId
      );

      const data = await apiRequest(
        `${API_BASE}/repositories/${repositoryId}/analyses`
      );

      console.log(
        "Analysis history API response:",
        data
      );

      /*
        Backend may return:
        {
          history: [...]
        }

        OR

        {
          analyses: [...]
        }

        OR

        {
          data: [...]
        }
      */

      let historyData = [];

      if (Array.isArray(data)) {
        historyData = data;
      } else if (
        Array.isArray(data.history)
      ) {
        historyData = data.history;
      } else if (
        Array.isArray(data.analyses)
      ) {
        historyData = data.analyses;
      } else if (
        Array.isArray(data.data)
      ) {
        historyData = data.data;
      }

      console.log(
        "Processed history:",
        historyData
      );

      setHistory(historyData);
    } catch (error) {
      console.error(
        "History loading error:",
        error
      );

      setHistory([]);

      setMessage(
        error.message ||
          "Unable to load analysis history."
      );
    }
  };

  // =========================
  // GRAPH DATA
  // =========================

  const loadGraphData = async () => {
    try {
      setGraphLoading(true);
      setGraphMessage("");

      const endpoints = {
        temporal: "/graph/temporal",
        knowledge:
          "/graph/knowledge-concentration",
        impact: "/graph/impact",
        whatIf: "/graph/what-if",
        developerFile:
          "/graph/developer-file",
        nodes: "/graph/nodes",
        edges: "/graph/edges",
      };

      const results = {};

      for (
        const [key, endpoint] of Object.entries(
          endpoints
        )
      ) {
        try {
          const data = await apiRequest(
            `${API_BASE}${endpoint}`
          );

          results[key] =
            data.data ||
            data.results ||
            data.nodes ||
            data.edges ||
            data;
        } catch (error) {
          console.error(
            `${key} graph error:`,
            error
          );

          results[key] = [];
        }
      }

      setGraphData({
        temporal: results.temporal || [],
        knowledge: results.knowledge || [],
        impact: results.impact || [],
        whatIf: results.whatIf || [],
        developerFile:
          results.developerFile || [],
        nodes: results.nodes || [],
        edges: results.edges || [],
      });

      setGraphMessage(
        "Graph analysis loaded."
      );
    } catch (error) {
      console.error(
        "Graph loading error:",
        error
      );

      setGraphMessage(
        "Unable to load graph analysis."
      );
    } finally {
      setGraphLoading(false);
    }
  };

  // =========================
  // GITHUB CALLBACK
  // =========================

  useEffect(() => {
    const params =
      new URLSearchParams(
        window.location.search
      );

    const githubStatus =
      params.get("github");

    if (githubStatus === "connected") {
      setPage("dashboard");

      setMessage(
        "GitHub connected successfully."
      );

      window.history.replaceState(
        {},
        document.title,
        window.location.pathname
      );

      loadGithubRepositories();
    }
  }, []);

  // =========================
  // LOAD REPOSITORY
  // =========================

  useEffect(() => {
    if (
      page === "dashboard" &&
      userId
    ) {
      loadRepository();
    }
  }, [page, userId]);

  // =========================
  // LOAD HISTORY WHEN REPO ID CHANGES
  // =========================

  useEffect(() => {
    if (repositoryId) {
      loadHistory();
    }
  }, [repositoryId]);

  // =========================
  // SETTINGS
  // =========================

  const toggleNotifications = () => {
    setSettings(
      (previous) => ({
        ...previous,
        notifications:
          !previous.notifications,
      })
    );
  };

  const toggleCompactMode = () => {
    setSettings(
      (previous) => ({
        ...previous,
        compactMode:
          !previous.compactMode,
      })
    );
  };

  // =========================
  // LOGIN PAGE
  // =========================

  if (page === "login") {
    return (
      <Login
        onLoginSuccess={
          handleLoginSuccess
        }
        onSignup={() =>
          setPage("signup")
        }
      />
    );
  }

  // =========================
  // SIGNUP PAGE
  // =========================

  if (page === "signup") {
    return (
      <Signup
        onSignupSuccess={() =>
          setPage("login")
        }
        onLogin={() =>
          setPage("login")
        }
      />
    );
  }

  // =========================
  // SETTINGS PAGE
  // =========================

  if (page === "settings") {
    return (
      <div className="app-container">

        <header className="header">

          <div>
            <h1>
              ⚙️ RepoRescue Settings
            </h1>

            <p>
              Manage your RepoRescue
              preferences.
            </p>
          </div>

          <button
            className="button"
            onClick={() =>
              setPage("dashboard")
            }
          >
            ← Dashboard
          </button>

        </header>

        <section className="card">

          <h2>Account</h2>

          <p>
            <strong>
              Username:
            </strong>{" "}
            {username ||
              "Not available"}
          </p>

          <p>
            <strong>
              Email:
            </strong>{" "}
            {email ||
              "Not available"}
          </p>

          <p>
            <strong>
              User ID:
            </strong>{" "}
            {userId ||
              "Not available"}
          </p>

        </section>

        <section className="card">

          <h2>Preferences</h2>

          <label className="setting-row">

            <span>
              Enable notifications
            </span>

            <input
              type="checkbox"
              checked={
                settings.notifications
              }
              onChange={
                toggleNotifications
              }
            />

          </label>

          <label className="setting-row">

            <span>
              Compact dashboard
            </span>

            <input
              type="checkbox"
              checked={
                settings.compactMode
              }
              onChange={
                toggleCompactMode
              }
            />

          </label>

        </section>

        <section className="card">

          <h2>Privacy</h2>

          <p>
            Repository analysis is
            associated with your
            authenticated RepoRescue
            account.
          </p>

          <p>
            Repository access is
            controlled through your
            connected GitHub account.
          </p>

        </section>

        <section className="card">

          <h2>Session</h2>

          <button
            className="button danger"
            onClick={logout}
          >
            Logout
          </button>

        </section>

      </div>
    );
  }

  // =========================
  // DASHBOARD
  // =========================

  return (
    <div
      className={
        settings.compactMode
          ? "app-container compact-mode"
          : "app-container"
      }
    >

      <header className="header">

        <div>

          <h1>
            🚨 RepoRescue
          </h1>

          <p>
            Repository Risk &
            Developer Bottleneck
            Analysis
          </p>

        </div>

        <div className="header-actions">

          <span>
            Welcome,{" "}
            <strong>
              {username || "User"}
            </strong>
          </span>

          <button
            className="button"
            onClick={() =>
              setPage("settings")
            }
          >
            ⚙️ Settings
          </button>

          <button
            className="button danger"
            onClick={logout}
          >
            Logout
          </button>

        </div>

      </header>

      {message && (
        <div className="message">
          {message}
        </div>
      )}

      {/* =========================
          GITHUB
      ========================= */}

      <section className="card">

        <h2>
          🔗 Connect GitHub
        </h2>

        <p>
          Connect your GitHub account
          to view repositories you are
          authorized to access.
        </p>

        <button
          className="button"
          onClick={connectGitHub}
          disabled={githubLoading}
        >
          {githubLoading
            ? "Connecting..."
            : githubConnected
            ? "GitHub Connected"
            : "Connect GitHub"}
        </button>

        {githubConnected && (
          <button
            className="button secondary"
            onClick={
              loadGithubRepositories
            }
            disabled={githubLoading}
          >
            🔄 Load Repositories
          </button>
        )}

        {githubRepos.length > 0 && (
          <div className="repo-list">

            <h3>
              Authorized GitHub
              Repositories
            </h3>

            {githubRepos.map(
              (repo) => (
                <div
                  className="repo-item"
                  key={repo.id}
                >

                  <div>

                    <strong>
                      {repo.full_name ||
                        repo.name}
                    </strong>

                    <p>
                      {repo.private
                        ? "🔒 Private"
                        : "🌐 Public"}
                    </p>

                  </div>

                  <button
                    className="button"
                    onClick={() =>
                      selectGithubRepository(
                        repo.id
                      )
                    }
                    disabled={
                      githubLoading
                    }
                  >
                    Select
                  </button>

                </div>
              )
            )}

          </div>
        )}

      </section>

      {/* =========================
          REPOSITORY
      ========================= */}

      <section className="card">

        <h2>
          📁 Repository
        </h2>

        <input
          type="text"
          placeholder="Repository name"
          value={repoName}
          onChange={(e) =>
            setRepoName(
              e.target.value
            )
          }
        />

        <input
          type="text"
          placeholder="GitHub repository URL"
          value={repoUrl}
          onChange={(e) =>
            setRepoUrl(
              e.target.value
            )
          }
        />

        <button
          className="button"
          onClick={addRepository}
          disabled={loading}
        >
          {loading
            ? "Connecting..."
            : "Connect Repository"}
        </button>

        {repositoryId && (
          <div className="repo-info">

            <h3>
              ✅ Connected Repository
            </h3>

            <p>
              <strong>
                Name:
              </strong>{" "}
              {repoName}
            </p>

            <p>
              <strong>
                URL:
              </strong>{" "}
              {repoUrl}
            </p>

            <p>
              <strong>
                Repository ID:
              </strong>{" "}
              {repositoryId}
            </p>

          </div>
        )}

      </section>

      {/* =========================
          PR ANALYSIS
      ========================= */}

      <section className="card">

        <h2>
          🤖 Pull Request Analysis
        </h2>

        <input
          type="number"
          placeholder="Enter PR number"
          value={prNumber}
          onChange={(e) =>
            setPrNumber(
              e.target.value
            )
          }
        />

        <button
          className="button"
          onClick={analyzePR}
          disabled={loading}
        >
          {loading
            ? "Analyzing..."
            : "Analyze PR"}
        </button>

        {analysisResult && (
          <div className="analysis-result">

            <h3>
              📊 Prediction Result
            </h3>

            {analysisResult.probability !==
              undefined && (
              <p>
                <strong>
                  Probability:
                </strong>{" "}
                {(
                  Number(
                    analysisResult.probability
                  ) * 100
                ).toFixed(2)}
                %
              </p>
            )}

            {analysisResult.prediction && (
              <p>
                <strong>
                  Prediction:
                </strong>{" "}
                {
                  analysisResult.prediction
                }
              </p>
            )}

            {analysisResult.threshold !==
              undefined && (
              <p>
                <strong>
                  Threshold:
                </strong>{" "}
                {
                  analysisResult.threshold
                }
              </p>
            )}

            {analysisResult.semantic_signal && (
              <p>
                <strong>
                  Semantic Signal:
                </strong>{" "}
                {
                  analysisResult.semantic_signal
                }
              </p>
            )}

            {analysisResult.semantic_strength !==
              undefined && (
              <p>
                <strong>
                  Semantic Strength:
                </strong>{" "}
                {Number(
                  analysisResult.semantic_strength
                ).toFixed(4)}
              </p>
            )}

            {analysisResult.top_evidence && (
              <div>

                <strong>
                  Top Evidence:
                </strong>

                <pre>
                  {typeof analysisResult.top_evidence ===
                  "string"
                    ? analysisResult.top_evidence
                    : JSON.stringify(
                        analysisResult.top_evidence,
                        null,
                        2
                      )}
                </pre>

              </div>
            )}

          </div>
        )}

      </section>

      {/* =========================
          GRAPH ANALYSIS
      ========================= */}

      <section className="card">

        <h2>
          📈 Repository Intelligence
        </h2>

        <button
          className="button"
          onClick={
            loadGraphData
          }
          disabled={graphLoading}
        >
          {graphLoading
            ? "Loading Graph Analysis..."
            : "Load Graph Analysis"}
        </button>

        {graphMessage && (
          <p>
            {graphMessage}
          </p>
        )}

        <div className="analysis-grid">

          <div className="analysis-box">

            <h3>
              ⏱️ Temporal Analysis
            </h3>

            <p>
              Records:{" "}
              {Array.isArray(
                graphData.temporal
              )
                ? graphData.temporal.length
                : 0}
            </p>

          </div>

          <div className="analysis-box">

            <h3>
              🧠 Knowledge Concentration
            </h3>

            <p>
              Records:{" "}
              {Array.isArray(
                graphData.knowledge
              )
                ? graphData.knowledge.length
                : 0}
            </p>

          </div>

          <div className="analysis-box">

            <h3>
              💥 Impact Analysis
            </h3>

            <p>
              Records:{" "}
              {Array.isArray(
                graphData.impact
              )
                ? graphData.impact.length
                : 0}
            </p>

          </div>

          <div className="analysis-box">

            <h3>
              🔮 What-if Simulation
            </h3>

            <p>
              Records:{" "}
              {Array.isArray(
                graphData.whatIf
              )
                ? graphData.whatIf.length
                : 0}
            </p>

          </div>

          <div className="analysis-box">

            <h3>
              👨‍💻 Developer–File Analysis
            </h3>

            <p>
              Records:{" "}
              {Array.isArray(
                graphData.developerFile
              )
                ? graphData.developerFile.length
                : 0}
            </p>

          </div>

          <div className="analysis-box">

            <h3>
              🔗 Repository Graph
            </h3>

            <p>
              Nodes:{" "}
              {Array.isArray(
                graphData.nodes
              )
                ? graphData.nodes.length
                : 0}
            </p>

            <p>
              Edges:{" "}
              {Array.isArray(
                graphData.edges
              )
                ? graphData.edges.length
                : 0}
            </p>

          </div>

        </div>

      </section>

      {/* =========================
          ANALYSIS HISTORY
      ========================= */}

      <section className="card">

        <h2>
          🕘 Analysis History
        </h2>

        {history.length === 0 ? (

          <p>
            No analysis history
            available.
          </p>

        ) : (

          <div className="history-list">

            {history.map(
              (item, index) => (

                <div
                  className="history-item"
                  key={
                    item.id ||
                    item.analysis_id ||
                    index
                  }
                >

                  <p>
                    <strong>
                      PR:
                    </strong>{" "}
                    {item.pr_number ??
                      item.prNumber ??
                      "-"}
                  </p>

                  <p>
                    <strong>
                      Prediction:
                    </strong>{" "}
                    {item.prediction ||
                      "-"}
                  </p>

                  {item.probability !==
                    undefined && (
                    <p>
                      <strong>
                        Probability:
                      </strong>{" "}
                      {(
                        Number(
                          item.probability
                        ) * 100
                      ).toFixed(2)}
                      %
                    </p>
                  )}

                  {item.threshold !==
                    undefined && (
                    <p>
                      <strong>
                        Threshold:
                      </strong>{" "}
                      {item.threshold}
                    </p>
                  )}

                  {item.semantic_signal && (
                    <p>
                      <strong>
                        Semantic Signal:
                      </strong>{" "}
                      {
                        item.semantic_signal
                      }
                    </p>
                  )}

                  {item.created_at && (
                    <p>
                      <strong>
                        Date:
                      </strong>{" "}
                      {item.created_at}
                    </p>
                  )}

                </div>

              )
            )}

          </div>

        )}

      </section>

      <footer className="footer">

        <p>
          RepoRescue • AI-powered
          repository risk analysis
        </p>

      </footer>

    </div>
  );
}

export default App;