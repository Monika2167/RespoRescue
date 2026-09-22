export const API_BASE =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8001";

export const getToken = () => localStorage.getItem("access_token");

export const setAuthSession = ({
  access_token,
  user_id,
  username,
  email,
}) => {
  if (access_token) localStorage.setItem("access_token", access_token);
  if (user_id !== undefined && user_id !== null) {
    localStorage.setItem("user_id", String(user_id));
  }
  if (username) localStorage.setItem("username", username);
  if (email) localStorage.setItem("email", email);
};

export const clearAuthSession = () => {
  localStorage.removeItem("access_token");
  localStorage.removeItem("user_id");
  localStorage.removeItem("username");
  localStorage.removeItem("email");
  localStorage.removeItem("selected_repo_id");
};

export const getStoredUser = () => {
  const token = getToken();

  if (!token) return null;

  return {
    user_id: localStorage.getItem("user_id")
      ? Number(localStorage.getItem("user_id"))
      : null,
    username: localStorage.getItem("username") || "",
    email: localStorage.getItem("email") || "",
  };
};

export const apiRequest = async (endpoint, options = {}) => {
  const token = getToken();

  const headers = {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(options.headers || {}),
  };

  const url = endpoint.startsWith("http")
    ? endpoint
    : `${API_BASE}${endpoint}`;

  let response;

  try {
    response = await fetch(url, {
      ...options,
      headers,
    });
  } catch (err) {
    throw new Error(
      `Unable to connect to RepoRescue API at ${API_BASE}. Make sure the backend is running.`
    );
  }

  let data = {};

  try {
    data = await response.json();
  } catch {
    data = {};
  }

  if (!response.ok) {
    const errorMsg =
      data.detail ||
      data.message ||
      `Request failed with status ${response.status}.`;

    const error = new Error(
      typeof errorMsg === "string"
        ? errorMsg
        : JSON.stringify(errorMsg)
    );

    error.status = response.status;
    error.data = data;

    throw error;
  }

  return data;
};