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

  // =========================
  // HEALTH FORECAST
  // =========================

  const [healthForecast, setHealthForecast] = useState(null);
  const [healthForecastLoading, setHealthForecastLoading] =
    useState(false);
  const [healthForecastError, setHealthForecastError] = useState("");

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

<<<<<<< HEAD
    setGraphData({
      temporal: [],
      knowledge: [],
      impact: [],
      whatIf: [],
      developerFile: [],
      nodes: [],
      edges: [],
    });
=======
    setHealthForecast(null);
    setHealthForecastError("");
>>>>>>> origin/master

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
        setMessage(
          "Please connect a repository first."
        );
        return;
      }

      const data = await apiRequest(
        `${API_BASE}/repositories/${repositoryId}/analyze/${prNumber}`,
        {
          method: "POST",
        }
      );

      setAnalysisResult(data);

      setMessage(
        "PR analysis completed successfully."
      );

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
    if (!repositoryId) {
      setGraphMessage(
        "Please select a repository before loading graph analysis."
      );
      return;
    }

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
            `${API_BASE}${endpoint}?repository_id=${encodeURIComponent(
              repositoryId
            )}`
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
        error.message ||
          "Unable to load graph analysis."
      );
    } finally {
      setGraphLoading(false);
    }
  };

  // =========================
  // HEALTH FORECAST
  // =========================

  const loadHealthForecast = async () => {
    try {
      setHealthForecastLoading(true);
      setHealthForecastError("");

      const data = await apiRequest(
        `${API_BASE}/health-forecast`
      );

      if (!data.success) {
        throw new Error(
          data.error ||
            "Health forecast is unavailable."
        );
      }

      setHealthForecast(data);
    } catch (error) {
      console.error(
        "Health forecast error:",
        error
      );

      setHealthForecast(null);

      setHealthForecastError(
        error.message ||
          "Unable to load repository health forecast."
      );
    } finally {
      setHealthForecastLoading(false);
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
  // LOAD HEALTH FORECAST
  // =========================

  useEffect(() => {
    if (
      page === "dashboard" &&
      userId
    ) {
      loadHealthForecast();
    }
  }, [page, userId]);

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
          REPOSITORY HEALTH FORECAST
      ========================= */}

      <section className="card">

        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            gap: "16px",
            flexWrap: "wrap",
          }}
        >

          <div>
            <h2>
              📈 Repository Health Forecast
            </h2>

            <p>
              ML-based prediction of the
              future 7-day average open
              pull request backlog.
            </p>
          </div>

          <button
            className="button"
            onClick={loadHealthForecast}
            disabled={healthForecastLoading}
          >
            {healthForecastLoading
              ? "Loading Forecast..."
              : "🔄 Refresh Forecast"}
          </button>

        </div>

        {healthForecastLoading && (
          <div className="analysis-result">
            <p>
              Loading real health forecast
              from the backend model...
            </p>
          </div>
        )}

        {!healthForecastLoading &&
          healthForecastError && (
            <div className="analysis-result">

              <h3>
                ⚠️ Forecast Unavailable
              </h3>

              <p>
                {healthForecastError}
              </p>

              <button
                className="button secondary"
                onClick={
                  loadHealthForecast
                }
              >
                Retry
              </button>

            </div>
          )}

        {!healthForecastLoading &&
          !healthForecastError &&
          healthForecast && (

            <div>

              {/* Forecast summary */}

              <div className="analysis-grid">

                <div className="analysis-box">

                  <h3>
                    📅 Forecast Date
                  </h3>

                  <p>
                    {new Date(
                      healthForecast.date
                    ).toLocaleDateString(
                      "en-IN",
                      {
                        day: "2-digit",
                        month: "short",
                        year: "numeric",
                      }
                    )}
                  </p>

                </div>

                <div className="analysis-box">

                  <h3>
                    🔮 Predicted 7-Day PR Backlog
                  </h3>

                  <p
                    style={{
                      fontSize: "28px",
                      fontWeight: "700",
                    }}
                  >
                    {Number(
                      healthForecast.forecast
                    ).toFixed(2)}
                  </p>

                  <small>
                    Average open PR backlog
                    over next 7 days
                  </small>

                </div>

                <div className="analysis-box">

                  <h3>
                    📂 Current Open PRs
                  </h3>

                  <p
                    style={{
                      fontSize: "28px",
                      fontWeight: "700",
                    }}
                  >
                    {Number(
                      healthForecast.current_open_pr_backlog
                    ).toFixed(0)}
                  </p>

                </div>

                <div className="analysis-box">

                  <h3>
                    🐛 Current Open Issues
                  </h3>

                  <p
                    style={{
                      fontSize: "28px",
                      fontWeight: "700",
                    }}
                  >
                    {Number(
                      healthForecast.current_open_issue_backlog
                    ).toFixed(0)}
                  </p>

                </div>

              </div>

              {/* Simple actual-value visualization */}

              <div
                style={{
                  marginTop: "24px",
                  padding: "20px",
                  borderRadius: "12px",
                  border: "1px solid rgba(128,128,128,0.25)",
                }}
              >

                <h3>
                  Current vs Forecast PR Backlog
                </h3>

                <p>
                  The forecast is compared
                  directly with the current
                  open PR backlog returned by
                  the backend.
                </p>

                <div
                  style={{
                    display: "grid",
                    gap: "18px",
                    marginTop: "20px",
                  }}
                >

                  <div>

                    <div
                      style={{
                        display: "flex",
                        justifyContent:
                          "space-between",
                        marginBottom: "6px",
                      }}
                    >
                      <strong>
                        Current Open PR Backlog
                      </strong>

                      <span>
                        {Number(
                          healthForecast.current_open_pr_backlog
                        ).toFixed(0)}
                      </span>
                    </div>

                    <div
                      style={{
                        width: "100%",
                        height: "16px",
                        background:
                          "rgba(128,128,128,0.18)",
                        borderRadius: "10px",
                        overflow: "hidden",
                      }}
                    >

                      <div
                        style={{
                          width: `${Math.min(
                            100,
                            (
                              Number(
                                healthForecast.current_open_pr_backlog
                              ) /
                              Math.max(
                                Number(
                                  healthForecast.current_open_pr_backlog
                                ),
                                Number(
                                  healthForecast.forecast
                                )
                              )
                            ) * 100
                          )}%`,
                          height: "100%",
                          background:
                            "linear-gradient(90deg, #2563eb, #06b6d4)",
                          borderRadius: "10px",
                        }}
                      />

                    </div>

                  </div>

                  <div>

                    <div
                      style={{
                        display: "flex",
                        justifyContent:
                          "space-between",
                        marginBottom: "6px",
                      }}
                    >
                      <strong>
                        Forecast 7-Day Average
                      </strong>

                      <span>
                        {Number(
                          healthForecast.forecast
                        ).toFixed(2)}
                      </span>
                    </div>

                    <div
                      style={{
                        width: "100%",
                        height: "16px",
                        background:
                          "rgba(128,128,128,0.18)",
                        borderRadius: "10px",
                        overflow: "hidden",
                      }}
                    >

                      <div
                        style={{
                          width: `${Math.min(
                            100,
                            (
                              Number(
                                healthForecast.forecast
                              ) /
                              Math.max(
                                Number(
                                  healthForecast.current_open_pr_backlog
                                ),
                                Number(
                                  healthForecast.forecast
                                )
                              )
                            ) * 100
                          )}%`,
                          height: "100%",
                          background:
                            "linear-gradient(90deg, #7c3aed, #ec4899)",
                          borderRadius: "10px",
                        }}
                      />

                    </div>

                  </div>

                </div>

              </div>

              {/* Explanation */}

              <div
                className="analysis-result"
                style={{
                  marginTop: "20px",
                }}
              >

                <h3>
                  🧠 What does this forecast mean?
                </h3>

                <p>
                  The current repository snapshot
                  has{" "}
                  <strong>
                    {Number(
                      healthForecast.current_open_pr_backlog
                    ).toFixed(0)}
                  </strong>{" "}
                  open pull requests. The trained
                  Ridge Regression model predicts a
                  future 7-day average backlog of{" "}
                  <strong>
                    {Number(
                      healthForecast.forecast
                    ).toFixed(2)}
                  </strong>.
                </p>

                <p>
                  The model also considers the
                  current open issue backlog of{" "}
                  <strong>
                    {Number(
                      healthForecast.current_open_issue_backlog
                    ).toFixed(0)}
                  </strong>{" "}
                  along with{" "}
                  <strong>
                    {healthForecast.feature_count}
                  </strong>{" "}
                  engineered temporal and backlog
                  features.
                </p>

                <p>
                  Model:{" "}
                  <strong>
                    {healthForecast.model}
                  </strong>
                  {" | "}
                  Alpha:{" "}
                  <strong>
                    {healthForecast.alpha}
                  </strong>
                </p>

              </div>

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
          disabled={graphLoading || !repositoryId}
        >
          {graphLoading
            ? "Loading Graph Analysis..."
            : !repositoryId
            ? "Select Repository First"
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