import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Settings as SettingsIcon, Lock, User, Trash2, Key, CheckCircle2, AlertCircle } from "lucide-react";
import { Github } from "../components/common/GithubIcon";
import { useAuth } from "../context/AuthContext";
import { useRepo } from "../context/RepoContext";
import { authService } from "../services/auth";
import { githubService } from "../services/github";
import { Card } from "../components/common/Card";
import { Button } from "../components/common/Button";
import { Badge } from "../components/common/Badge";
import { Modal } from "../components/common/Modal";

export const Settings = () => {
  const { user, logout } = useAuth();
  const { githubStatus, refreshGithub, fetchGithubRepos } = useRepo();
  const navigate = useNavigate();

  // Password state
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [passLoading, setPassLoading] = useState(false);
  const [passMsg, setPassMsg] = useState("");
  const [passErr, setPassErr] = useState("");

  // Token Connect state
  const [patToken, setPatToken] = useState("");
  const [tokenLoading, setTokenLoading] = useState(false);
  const [tokenMsg, setTokenMsg] = useState("");
  const [tokenErr, setTokenErr] = useState("");

  // Delete modal
  const [deleteModal, setDeleteModal] = useState(false);
  const [deleteLoading, setDeleteLoading] = useState(false);

  const handlePasswordUpdate = async (e) => {
    e.preventDefault();
    setPassMsg("");
    setPassErr("");
    setPassLoading(true);

    try {
      await authService.changePassword(currentPassword, newPassword);
      setPassMsg("Password updated successfully.");
      setCurrentPassword("");
      setNewPassword("");
    } catch (err) {
      setPassErr(err.message || "Failed to update password.");
    } finally {
      setPassLoading(false);
    }
  };

  const handleTokenConnect = async (e) => {
    e.preventDefault();
    setTokenMsg("");
    setTokenErr("");
    setTokenLoading(true);

    try {
      const res = await githubService.connectWithToken(patToken);
      setTokenMsg(res.message || "GitHub account connected successfully!");
      setPatToken("");
      await refreshGithub();
      await fetchGithubRepos();
    } catch (err) {
      setTokenErr(err.message || "Invalid GitHub token.");
    } finally {
      setTokenLoading(false);
    }
  };

  const handleDisconnectGithub = async () => {
    if (window.confirm("Disconnect GitHub account from RepoRescue?")) {
      try {
        await githubService.disconnect();
        await refreshGithub();
      } catch (err) {
        alert(err.message || "Failed to disconnect.");
      }
    }
  };

  const handleDeleteAccount = async () => {
    setDeleteLoading(true);
    try {
      await authService.deleteAccount();
      logout();
      navigate("/login");
    } catch (err) {
      alert(err.message || "Failed to delete account.");
    } finally {
      setDeleteLoading(false);
    }
  };

  return (
    <div className="space-y-6 animate-fade-in max-w-4xl">
      <div className="border-b border-slate-800/80 pb-4">
        <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
          <SettingsIcon className="w-6 h-6 text-indigo-400" />
          Settings & Preferences
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Manage your account profile, GitHub connections, security, and repository data.
        </p>
      </div>

      {/* GitHub Connection Section */}
      <Card
        title="GitHub Account Integration"
        subtitle="Primary authorization channel for importing and analyzing repositories"
      >
        {githubStatus.github_connected ? (
          <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 flex items-center justify-center">
                <Github className="w-5 h-5" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-semibold text-white text-sm">
                    {githubStatus.username}
                  </span>
                  <Badge variant="success" size="xs">
                    Connected
                  </Badge>
                </div>
                <p className="text-xs text-slate-400 mt-0.5">
                  Authorized for repository access and synchronization.
                </p>
              </div>
            </div>

            <Button
              variant="danger"
              size="sm"
              onClick={handleDisconnectGithub}
            >
              Disconnect GitHub
            </Button>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <div className="font-semibold text-white text-sm">
                  Standard GitHub OAuth Flow
                </div>
                <p className="text-xs text-slate-400 mt-0.5">
                  Redirect to GitHub for standard OAuth authorization.
                </p>
              </div>
              <Button
                variant="github"
                size="sm"
                icon={Github}
                onClick={() => {
                  try {
                    window.location.href = githubService.getOAuthUrl();
                  } catch (e) {
                    alert(e.message);
                  }
                }}
              >
                Connect via OAuth
              </Button>
            </div>

            {/* Alternative Personal Access Token Option */}
            <form
              onSubmit={handleTokenConnect}
              className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-3"
            >
              <div className="flex items-center gap-2">
                <Key className="w-4 h-4 text-indigo-400" />
                <span className="font-semibold text-white text-sm">
                  Or Connect with GitHub Personal Access Token (PAT)
                </span>
              </div>
              <p className="text-xs text-slate-400">
                Securely send your personal access token directly to the RepoRescue backend. (Requires 'repo' scope).
              </p>

              {tokenMsg && (
                <div className="p-2.5 rounded bg-emerald-500/10 text-emerald-300 text-xs flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                  <span>{tokenMsg}</span>
                </div>
              )}
              {tokenErr && (
                <div className="p-2.5 rounded bg-rose-500/10 text-rose-300 text-xs flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
                  <span>{tokenErr}</span>
                </div>
              )}

              <div className="flex gap-2">
                <input
                  type="password"
                  required
                  value={patToken}
                  onChange={(e) => setPatToken(e.target.value)}
                  placeholder="ghp_xxxxxxxxxxxxxxxxxxxx"
                  className="flex-1 px-3 py-2 text-xs bg-slate-950 border border-slate-800 rounded-lg text-slate-100 font-mono focus:outline-none focus:border-indigo-500"
                />
                <Button
                  type="submit"
                  variant="primary"
                  size="sm"
                  loading={tokenLoading}
                >
                  Verify & Connect
                </Button>
              </div>
            </form>
          </div>
        )}
      </Card>

      {/* User Profile Info */}
      <Card title="Account Profile" subtitle="Your authenticated session details">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
          <div className="p-3 bg-slate-900/60 rounded-xl border border-slate-800">
            <div className="text-slate-500 text-[10px] uppercase font-semibold">Username</div>
            <div className="text-slate-100 font-medium mt-1">{user?.username}</div>
          </div>
          <div className="p-3 bg-slate-900/60 rounded-xl border border-slate-800">
            <div className="text-slate-500 text-[10px] uppercase font-semibold">Email Address</div>
            <div className="text-slate-100 font-medium mt-1">{user?.email}</div>
          </div>
        </div>
      </Card>

      {/* Security: Change Password */}
      <Card title="Security & Password" subtitle="Update your account password">
        <form onSubmit={handlePasswordUpdate} className="space-y-4 max-w-md">
          {passMsg && (
            <div className="p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-xs flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
              <span>{passMsg}</span>
            </div>
          )}
          {passErr && (
            <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
              <span>{passErr}</span>
            </div>
          )}

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">
              Current Password
            </label>
            <input
              type="password"
              required
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
              className="w-full px-3 py-2 text-xs bg-slate-900 border border-slate-800 rounded-lg text-slate-100 focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">
              New Password
            </label>
            <input
              type="password"
              required
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              className="w-full px-3 py-2 text-xs bg-slate-900 border border-slate-800 rounded-lg text-slate-100 focus:outline-none focus:border-indigo-500"
            />
          </div>

          <Button type="submit" variant="primary" size="sm" loading={passLoading}>
            Update Password
          </Button>
        </form>
      </Card>

      {/* Danger Zone: Account Deletion */}
      <Card title="Data Management & Account Deletion" subtitle="Destructive actions requiring explicit confirmation">
        <div className="flex items-center justify-between p-4 rounded-xl bg-rose-500/5 border border-rose-500/20">
          <div>
            <div className="font-semibold text-rose-400 text-xs">Delete Account</div>
            <div className="text-[11px] text-slate-400 mt-0.5">
              Permanently delete your account, saved repositories, and analysis history.
            </div>
          </div>
          <Button
            variant="danger"
            size="sm"
            onClick={() => setDeleteModal(true)}
          >
            Delete Account
          </Button>
        </div>
      </Card>

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={deleteModal}
        onClose={() => setDeleteModal(false)}
        title="Delete Account Confirmation"
        subtitle="This action cannot be undone."
      >
        <div className="space-y-4 text-xs text-slate-300">
          <p>
            Are you sure you want to permanently delete your account (
            <span className="font-semibold text-white">{user?.username}</span>)?
            All associated repositories, GitHub linkages, and analysis results will be deleted.
          </p>
          <div className="flex items-center justify-end gap-3 pt-4">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setDeleteModal(false)}
            >
              Cancel
            </Button>
            <Button
              variant="danger"
              size="sm"
              loading={deleteLoading}
              onClick={handleDeleteAccount}
            >
              Confirm Permanent Deletion
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
};
