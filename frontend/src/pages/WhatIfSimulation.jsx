import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { Sliders, RefreshCw, AlertTriangle, ShieldAlert } from "lucide-react";
import { graphService } from "../services/graph";
import { useRepo } from "../context/RepoContext";
import { RepoWorkspaceHeader } from "../components/repository/RepoWorkspaceHeader";
import { RepoWorkspaceNav } from "../components/repository/RepoWorkspaceNav";
import { Card } from "../components/common/Card";
import { Button } from "../components/common/Button";
import { Badge } from "../components/common/Badge";
import { Skeleton } from "../components/common/Skeleton";

export const WhatIfSimulation = () => {
  const { repositoryId } = useParams();
  const { selectedRepo } = useRepo();

  const [rawSimulation, setRawSimulation] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Interactive hypothetical sliders
  const [contributorCapacity, setContributorCapacity] = useState(100);
  const [backlogPressure, setBacklogPressure] = useState(0);
  const [simulateDominantDeparture, setSimulateDominantDeparture] = useState(false);

  const loadSimulation = async () => {
    try {
      setLoading(true);
      setError("");
      const res = await graphService.getWhatIfResults();
      setRawSimulation(res.data || []);
    } catch (err) {
      setError(err.message || "Failed to load simulation baseline.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSimulation();
  }, []);

  const atRiskCount = rawSimulation.filter((r) => r.high_concentration_flag === 1).length;
  const simulatedVulnerableFiles = Math.round(
    atRiskCount * (simulateDominantDeparture ? 1.4 : 1.0) * (200 - contributorCapacity) / 100
  );

  return (
    <div className="space-y-6 animate-fade-in">
      <RepoWorkspaceHeader repository={selectedRepo} />
      <RepoWorkspaceNav />

      <div className="border-b border-slate-800/80 pb-4">
        <div className="flex items-center gap-2 mb-1">
          <h2 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
            <Sliders className="w-5 h-5 text-indigo-400" />
            What-If Simulation
          </h2>
          <Badge variant="warning" size="xs">
            SIMULATION ONLY
          </Badge>
        </div>
        <p className="text-xs text-slate-400">
          Model hypothetical scenarios (maintainer departure, reviewer capacity shifts, backlog spikes). All values are simulated outputs.
        </p>
      </div>

      {/* Prominent Simulation Disclaimer */}
      <div className="p-3.5 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-300 text-xs flex items-center gap-2.5">
        <AlertTriangle className="w-4 h-4 shrink-0 text-amber-400" />
        <span>
          <strong>SIMULATION NOTICE:</strong> All predictions and values generated on this screen are hypothetical scenarios for capacity planning. They are never presented as real historical measurements.
        </span>
      </div>

      {/* Interactive Simulation Controls */}
      <Card title="Hypothetical Input Parameters" subtitle="Adjust parameters to simulate repository risk response">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 py-2">
          <div>
            <div className="flex justify-between text-xs text-slate-300 mb-1.5">
              <span>Maintainer Capacity</span>
              <span className="font-mono text-indigo-400">{contributorCapacity}%</span>
            </div>
            <input
              type="range"
              min="20"
              max="180"
              value={contributorCapacity}
              onChange={(e) => setContributorCapacity(Number(e.target.value))}
              className="w-full accent-indigo-500 cursor-pointer"
            />
            <div className="text-[10px] text-slate-500 mt-1">Simulate team capacity expansion or shrinkage</div>
          </div>

          <div>
            <div className="flex justify-between text-xs text-slate-300 mb-1.5">
              <span>PR Backlog Surge</span>
              <span className="font-mono text-amber-400">+{backlogPressure}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="150"
              value={backlogPressure}
              onChange={(e) => setBacklogPressure(Number(e.target.value))}
              className="w-full accent-amber-500 cursor-pointer"
            />
            <div className="text-[10px] text-slate-500 mt-1">Simulate sudden influx of incoming pull requests</div>
          </div>

          <div className="flex flex-col justify-center">
            <label className="flex items-center gap-2 text-xs text-slate-200 cursor-pointer select-none">
              <input
                type="checkbox"
                checked={simulateDominantDeparture}
                onChange={(e) => setSimulateDominantDeparture(e.target.checked)}
                className="rounded border-slate-700 text-indigo-600 focus:ring-indigo-500 bg-slate-900"
              />
              <span className="font-medium">Simulate Dominant Maintainer Departure</span>
            </label>
            <div className="text-[10px] text-slate-500 mt-1 pl-5">
              Models instant loss of primary code authors across high-concentration files
            </div>
          </div>
        </div>
      </Card>

      {/* Simulated Output Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <Card title="Simulated Vulnerable Files" subtitle="[SIMULATION]">
          <div className="text-3xl font-bold text-rose-400 font-mono tracking-tight">
            {simulatedVulnerableFiles}
          </div>
          <p className="text-[11px] text-slate-400 mt-2">
            Files projected to lose primary maintenance coverage under current hypothetical configuration.
          </p>
        </Card>

        <Card title="Simulated Review Delay" subtitle="[SIMULATION]">
          <div className="text-3xl font-bold text-amber-400 font-mono tracking-tight">
            +{Math.round((200 - contributorCapacity + backlogPressure) / 10)}%
          </div>
          <p className="text-[11px] text-slate-400 mt-2">
            Projected increase in time-to-first-review based on simulated maintainer throughput.
          </p>
        </Card>

        <Card title="Simulated Health Stress" subtitle="[SIMULATION]">
          <div className="text-3xl font-bold text-indigo-400 font-mono tracking-tight">
            {Math.min(100, Math.round(50 + backlogPressure * 0.3 + (200 - contributorCapacity) * 0.2))}/100
          </div>
          <p className="text-[11px] text-slate-400 mt-2">
            Composite simulation stress index reflecting capacity and queue growth.
          </p>
        </Card>
      </div>

      {/* Baseline Scenario Table */}
      <Card title="Hypothetical Dominant Contributor Exposure" subtitle="Files evaluated under maintainer departure simulation">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400">
                <th className="pb-3 font-semibold">File Name</th>
                <th className="pb-3 font-semibold">Dominant Developer</th>
                <th className="pb-3 font-semibold">Dominant Share</th>
                <th className="pb-3 font-semibold">Remaining Share</th>
                <th className="pb-3 font-semibold">Simulated Impact</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono">
              {rawSimulation.slice(0, 15).map((row, idx) => (
                <tr key={idx} className="hover:bg-slate-800/30">
                  <td className="py-2.5 text-slate-200 max-w-xs truncate">{row.file_name}</td>
                  <td className="py-2.5 text-indigo-300">{row.dominant_developer}</td>
                  <td className="py-2.5 text-slate-300">
                    {row.dominant_developer_share !== null
                      ? `${Math.round(row.dominant_developer_share * 100)}%`
                      : "N/A"}
                  </td>
                  <td className="py-2.5 text-slate-400">
                    {row.remaining_contributor_share !== null
                      ? `${Math.round(row.remaining_contributor_share * 100)}%`
                      : "0%"}
                  </td>
                  <td className="py-2.5">
                    {row.files_with_no_remaining_contributor === 1 ? (
                      <span className="text-rose-400 font-semibold">[SIMULATION] Zero Maintainers</span>
                    ) : (
                      <span className="text-amber-400">[SIMULATION] Reduced Coverage</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
};
