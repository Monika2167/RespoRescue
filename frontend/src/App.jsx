import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import { RepoProvider } from "./context/RepoContext";
import { ProtectedRoute } from "./components/layout/ProtectedRoute";
import { AppLayout } from "./components/layout/AppLayout";

// Public Pages
import { Login } from "./pages/Login";
import { Signup } from "./pages/Signup";
import { ForgotPassword } from "./pages/ForgotPassword";

// Protected App Pages
import { Dashboard } from "./pages/Dashboard";
import { Repositories } from "./pages/Repositories";
import { RepositoryOverview } from "./pages/RepositoryOverview";
import { BottleneckRisk } from "./pages/BottleneckRisk";
import { ChangeRisk } from "./pages/ChangeRisk";
import { HealthForecast } from "./pages/HealthForecast";
import { IntelligenceHub } from "./pages/IntelligenceHub";
import { GraphIntelligence } from "./pages/GraphIntelligence";
import { TemporalAnalysis } from "./pages/TemporalAnalysis";
import { KnowledgeConcentration } from "./pages/KnowledgeConcentration";
import { ImpactPropagation } from "./pages/ImpactPropagation";
import { WhatIfSimulation } from "./pages/WhatIfSimulation";
import { DeveloperRelationships } from "./pages/DeveloperRelationships";
import { RepositoryAssistant } from "./pages/RepositoryAssistant";
import { AnalysisHistory } from "./pages/AnalysisHistory";
import { Alerts } from "./pages/Alerts";
import { Settings } from "./pages/Settings";
import { HelpAssistant } from "./pages/HelpAssistant";

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <RepoProvider>
          <Routes>
            {/* Public Authentication Routes */}
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />
            <Route path="/forgot-password" element={<ForgotPassword />} />

            {/* Protected SaaS Application Shell */}
            <Route
              element={
                <ProtectedRoute>
                  <AppLayout />
                </ProtectedRoute>
              }
            >
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/repositories" element={<Repositories />} />

              {/* Repository Scoped Workspace */}
              <Route path="/repositories/:repositoryId" element={<RepositoryOverview />} />
              <Route
                path="/repositories/:repositoryId/risk"
                element={<Navigate to="bottleneck" replace />}
              />
              <Route
                path="/repositories/:repositoryId/risk/bottleneck"
                element={<BottleneckRisk />}
              />
              <Route
                path="/repositories/:repositoryId/risk/change"
                element={<ChangeRisk />}
              />
              <Route
                path="/repositories/:repositoryId/health"
                element={<HealthForecast />}
              />
              <Route
                path="/repositories/:repositoryId/intelligence"
                element={<IntelligenceHub />}
              />
              <Route
                path="/repositories/:repositoryId/graph"
                element={<GraphIntelligence />}
              />
              <Route
                path="/repositories/:repositoryId/temporal"
                element={<TemporalAnalysis />}
              />
              <Route
                path="/repositories/:repositoryId/knowledge"
                element={<KnowledgeConcentration />}
              />
              <Route
                path="/repositories/:repositoryId/impact"
                element={<ImpactPropagation />}
              />
              <Route
                path="/repositories/:repositoryId/simulation"
                element={<WhatIfSimulation />}
              />
              <Route
                path="/repositories/:repositoryId/developers"
                element={<DeveloperRelationships />}
              />
              <Route
                path="/repositories/:repositoryId/assistant"
                element={<RepositoryAssistant />}
              />

              {/* Cross-Repository Tools */}
              <Route path="/history" element={<AnalysisHistory />} />
              <Route path="/alerts" element={<Alerts />} />
              <Route path="/settings" element={<Settings />} />
              <Route path="/help" element={<HelpAssistant />} />
            </Route>

            {/* Root & Catch-all Redirect */}
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </RepoProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}
