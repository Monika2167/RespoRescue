import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Lock, Mail, AlertCircle } from "lucide-react";
import { Github } from "../components/common/GithubIcon";
import { useAuth } from "../context/AuthContext";
import { githubService } from "../services/github";
import { Button } from "../components/common/Button";

export const Login = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(email, password);
      navigate("/dashboard");
    } catch (err) {
      setError(err.message || "Invalid email or password");
    } finally {
      setLoading(false);
    }
  };

  const handleGitHubSSO = () => {
    try {
      window.location.href = githubService.getOAuthUrl();
    } catch (err) {
      setError("Please sign in with your email first, then connect GitHub.");
    }
  };

  return (
    <div className="min-h-screen bg-[#070b14] text-slate-100 flex flex-col justify-center items-center p-4 relative overflow-hidden">
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-indigo-600/10 rounded-full blur-3xl pointer-events-none" />
      <div className="text-center mb-8 relative z-10">
        <div className="inline-flex items-center justify-center w-12 h-12 rounded-2xl bg-gradient-to-br from-indigo-500 to-violet-600 shadow-xl shadow-indigo-500/25 mb-4 text-white font-black text-xl">
          R
        </div>
        <h1 className="text-2xl md:text-3xl font-bold tracking-tight text-white mb-1.5">
          RepoRescue
        </h1>
        <h2 className="text-sm text-indigo-400 font-medium mb-1">
          Intelligent Repository Maintenance
        </h2>
        <p className="text-xs text-slate-400 max-w-sm mx-auto">
          Predict risks. Understand changes. Maintain healthier repositories.
        </p>
      </div>

      <div className="w-full max-w-md bg-[#0e1424] border border-slate-800/90 rounded-2xl p-6 md:p-8 shadow-2xl shadow-black/80 relative z-10 backdrop-blur-xl">
        <h3 className="text-lg font-semibold text-slate-100 mb-1">Welcome back</h3>
        <p className="text-xs text-slate-400 mb-6">Sign in to access your repository intelligence workspace.</p>

        {error && (
          <div className="mb-5 p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs flex items-center gap-2.5">
            <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1.5">Email Address</label>
            <div className="relative">
              <Mail className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="developer@company.com"
                className="w-full pl-9 pr-3 py-2 text-sm bg-slate-900/80 border border-slate-700/80 rounded-lg text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
              />
            </div>
          </div>

          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label className="text-xs font-medium text-slate-300">Password</label>
              <Link to="/forgot-password" className="text-xs text-indigo-400 hover:text-indigo-300 transition">
                Forgot password?
              </Link>
            </div>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full pl-9 pr-3 py-2 text-sm bg-slate-900/80 border border-slate-700/80 rounded-lg text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
              />
            </div>
          </div>

          <Button type="submit" variant="primary" loading={loading} className="w-full py-2.5 mt-2">
            Sign In
          </Button>
        </form>

        <div className="relative my-6">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-slate-800" />
          </div>
          <div className="relative flex justify-center text-xs uppercase">
            <span className="bg-[#0e1424] px-3 text-slate-500 font-medium">OR</span>
          </div>
        </div>

        <Button variant="github" className="w-full py-2.5" icon={Github} onClick={handleGitHubSSO}>
          Continue with GitHub
        </Button>

        <div className="text-center mt-6 text-xs text-slate-400">
          Don't have an account?{" "}
          <Link to="/signup" className="text-indigo-400 hover:text-indigo-300 font-medium ml-1 transition">
            Create one
          </Link>
        </div>
      </div>
    </div>
  );
};
