import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { Share2, RefreshCw, Filter, Layers, Database } from "lucide-react";
import { graphService } from "../services/graph";
import { useRepo } from "../context/RepoContext";
import { RepoWorkspaceHeader } from "../components/repository/RepoWorkspaceHeader";
import { RepoWorkspaceNav } from "../components/repository/RepoWorkspaceNav";
import { Card } from "../components/common/Card";
import { Button } from "../components/common/Button";
import { Badge } from "../components/common/Badge";
import { Skeleton } from "../components/common/Skeleton";
import { InteractiveGraph } from "../components/graph/InteractiveGraph";

export const GraphIntelligence = () => {
  const { repositoryId } = useParams();
  const { selectedRepo } = useRepo();

  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);
  const [selectedNode, setSelectedNode] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadGraph = async () => {
    try {
      setLoading(true);
      setError("");
      const [nRes, eRes] = await Promise.all([
        graphService.getNodes(50, 0),
        graphService.getEdges(50, 0),
      ]);
      setNodes(nRes.data || []);
      setEdges(eRes.data || []);
    } catch (err) {
      setError(err.message || "Failed to load graph data.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadGraph();
  }, []);

  return (
    <div className="space-y-6 animate-fade-in">
      <RepoWorkspaceHeader repository={selectedRepo} />
      <RepoWorkspaceNav />

      <div className="flex items-center justify-between border-b border-slate-800/80 pb-4">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
            <Share2 className="w-5 h-5 text-indigo-400" />
            Interactive Repository Graph
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Real relationship graph representing Developers, Files, Commits, PRs, and Issues.
          </p>
        </div>

        <Button
          variant="outline"
          size="sm"
          icon={RefreshCw}
          loading={loading}
          onClick={loadGraph}
        >
          Reload Graph
        </Button>
      </div>

      {loading ? (
        <Skeleton count={1} className="h-96" />
      ) : error ? (
        <div className="p-8 text-center border border-dashed border-slate-800 rounded-xl text-xs text-slate-400">
          {error}
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-5">
          {/* Main Visual Graph */}
          <div className="lg:col-span-3">
            <InteractiveGraph
              nodes={nodes}
              edges={edges}
              height={440}
              onSelectNode={(n) => setSelectedNode(n)}
            />
          </div>

          {/* Node Inspector Panel */}
          <div className="lg:col-span-1">
            <Card
              title="Node Inspector"
              subtitle={selectedNode ? "Inspecting entity details" : "Click a node to inspect"}
            >
              {selectedNode ? (
                <div className="space-y-3 text-xs">
                  <div>
                    <div className="text-[10px] text-slate-500 uppercase font-semibold">
                      Node Type
                    </div>
                    <Badge variant="purple" size="xs" className="mt-1">
                      {selectedNode.node_type}
                    </Badge>
                  </div>

                  {selectedNode.developer && (
                    <div>
                      <div className="text-[10px] text-slate-500 uppercase font-semibold">
                        Developer
                      </div>
                      <div className="font-mono text-slate-200 mt-0.5">
                        {selectedNode.developer}
                      </div>
                    </div>
                  )}

                  {selectedNode.file_name && (
                    <div>
                      <div className="text-[10px] text-slate-500 uppercase font-semibold">
                        File Path
                      </div>
                      <div className="font-mono text-slate-200 text-[11px] break-all mt-0.5">
                        {selectedNode.file_name}
                      </div>
                    </div>
                  )}

                  {selectedNode.pr_number && (
                    <div>
                      <div className="text-[10px] text-slate-500 uppercase font-semibold">
                        PR Number
                      </div>
                      <div className="font-mono text-slate-200 mt-0.5">
                        #{selectedNode.pr_number}
                      </div>
                    </div>
                  )}

                  {selectedNode.commit_sha && (
                    <div>
                      <div className="text-[10px] text-slate-500 uppercase font-semibold">
                        Commit SHA
                      </div>
                      <div className="font-mono text-slate-200 text-[11px] mt-0.5">
                        {selectedNode.commit_sha}
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-xs text-slate-500 py-8 text-center leading-relaxed">
                  Select any node on the graph canvas to inspect its real metadata and connections.
                </div>
              )}
            </Card>
          </div>
        </div>
      )}
    </div>
  );
};
