import React, { createContext, useContext, useState, useEffect } from "react";
import { getToken, getStoredUser, clearAuthSession } from "../services/api";
import { authService } from "../services/auth";

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(getStoredUser());
  const [token, setToken] = useState(getToken());
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const currentToken = getToken();
    const stored = getStoredUser();
    setToken(currentToken);
    setUser(stored);
    setLoading(false);
  }, []);

  const login = async (email, password) => {
    const data = await authService.login(email, password);
    setToken(data.access_token);
    setUser({
      user_id: data.user_id,
      username: data.username,
      email: data.email,
    });
    return data;
  };

  const signup = async (username, email, password) => {
    return await authService.signup(username, email, password);
  };

  const logout = () => {
    authService.logout();
    setToken(null);
    setUser(null);
  };

  const isAuthenticated = Boolean(token && user);

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated,
        loading,
        login,
        signup,
        logout,
        setUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within an AuthProvider");
  return context;
};
