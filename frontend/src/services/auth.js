import { apiRequest, setAuthSession, clearAuthSession } from "./api";

export const authService = {
  async login(email, password) {
    const data = await apiRequest("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
    setAuthSession(data);
    return data;
  },

  async signup(username, email, password) {
    const data = await apiRequest("/auth/signup", {
      method: "POST",
      body: JSON.stringify({ username, email, password }),
    });
    return data;
  },

  async getProfile() {
    return await apiRequest("/auth/me");
  },

  async changePassword(current_password, new_password) {
    return await apiRequest("/auth/change-password", {
      method: "POST",
      body: JSON.stringify({ current_password, new_password }),
    });
  },

  async forgotPassword(email) {
    return await apiRequest("/auth/forgot-password", {
      method: "POST",
      body: JSON.stringify({ email }),
    });
  },

  async deleteAccount() {
    const data = await apiRequest("/auth/account", {
      method: "DELETE",
    });
    clearAuthSession();
    return data;
  },

  logout() {
    clearAuthSession();
  },
};
