import React, { useState } from "react";
import { ZoomIn, ZoomOut, RotateCcw, Filter } from "lucide-react";

export const InteractiveGraph = ({
  nodes = [],
  edges = [],
  onSelectNode,
  height = 420,
}) => {
  const [zoom, setZoom] = useState(1);
  const [filterType, setFilterType] = useState("all");
  const [selectedNodeId, setSelectedNodeId] = useState(null);

  if (!nodes || nodes.length === 0) {
    return (
      <div
        style={{ height }}
        className="flex items-center justify-center text-xs text-slate-500 border border-dashed border-slate-800 rounded-xl"
      >
        No graph data available yet.
      </div>
    );
  }

  const nodeColors = {
    developer: "#38bdf8",
    file: "#818cf8",
    pr: "#34d399",
    commit: "#fbbf24",
    issue: "#f87171",
  };

  const filteredNodes =
    filterType === "all"
      ? nodes.slice(0, 35)
      : nodes.filter((n) => n.node_type === filterType).slice(0, 35);

  const nodeMap = new Map();
  const width = 800;
  const svgHeight = height;
  const centerX = width / 2;
  const centerY = svgHeight / 2;
  const radius = Math.min(centerX, centerY) - 70;

  filteredNodes.forEach((node, i) => {
    const angle = (i / (filteredNodes.length || 1)) * 2 * Math.PI;
    const x = centerX + radius * Math.cos(angle);
    const y = centerY + radius * Math.sin(angle);
    nodeMap.set(node.node_id || String(i), { ...node, x, y });
  });

  const handleNodeClick = (node) => {
    setSelectedNodeId(node.node_id);
    if (onSelectNode) onSelectNode(node);
  };

  return (
    <div className="relative border border-slate-800 rounded-xl bg-[#0b0f19] overflow-hidden">
      {/* Graph Toolbar */}
      <div className="absolute top-3 right-3 z-10 flex items-center gap-1.5 bg-slate-900/90 border border-slate-800 p-1 rounded-lg backdrop-blur">
        <select
          value={filterType}
          onChange={(e) => setFilterType(e.target.value)}
          className="text-xs bg-transparent border-none text-slate-300 focus:outline-none px-2 py-1 cursor-pointer"
        >
          <option value="all" className="bg-slate-900">All Nodes</option>
          <option value="developer" className="bg-slate-900">Developers</option>
          <option value="file" className="bg-slate-900">Files</option>
          <option value="pr" className="bg-slate-900">Pull Requests</option>
          <option value="commit" className="bg-slate-900">Commits</option>
        </select>
        <div className="w-[1px] h-4 bg-slate-800" />
        <button
          onClick={() => setZoom((z) => Math.min(2, z + 0.15))}
          className="p-1 text-slate-400 hover:text-white rounded"
        >
          <ZoomIn className="w-3.5 h-3.5" />
        </button>
        <button
          onClick={() => setZoom((z) => Math.max(0.6, z - 0.15))}
          className="p-1 text-slate-400 hover:text-white rounded"
        >
          <ZoomOut className="w-3.5 h-3.5" />
        </button>
        <button
          onClick={() => setZoom(1)}
          className="p-1 text-slate-400 hover:text-white rounded"
        >
          <RotateCcw className="w-3.5 h-3.5" />
        </button>
      </div>

      <svg
        viewBox={`0 0 ${width} ${svgHeight}`}
        className="w-full select-none"
        style={{ height, transform: `scale(${zoom})`, transformOrigin: "center" }}
      >
        {/* Render connections */}
        {edges.slice(0, 50).map((edge, idx) => {
          const src = nodeMap.get(String(edge.source));
          const tgt = nodeMap.get(String(edge.target));
          if (!src || !tgt) return null;
          return (
            <line
              key={idx}
              x1={src.x}
              y1={src.y}
              x2={tgt.x}
              y2={tgt.y}
              stroke="#1e293b"
              strokeWidth="1.2"
              strokeDasharray="2 2"
            />
          );
        })}

        {/* Central hub indicator */}
        <circle cx={centerX} cy={centerY} r="18" fill="#1e1b4b" stroke="#6366f1" strokeWidth="2" opacity="0.4" />

        {/* Render nodes */}
        {Array.from(nodeMap.values()).map((node, idx) => {
          const color = nodeColors[node.node_type] || "#94a3b8";
          const isSelected = selectedNodeId === node.node_id;

          return (
            <g
              key={idx}
              className="cursor-pointer transition-transform duration-150"
              onClick={() => handleNodeClick(node)}
            >
              <circle
                cx={node.x}
                cy={node.y}
                r={isSelected ? 10 : 7}
                fill={color}
                stroke="#0f172a"
                strokeWidth={isSelected ? 3 : 2}
              />
              <text
                x={node.x}
                y={node.y + 16}
                fontSize="9"
                fill="#94a3b8"
                textAnchor="middle"
                className="pointer-events-none select-none font-mono"
              >
                {node.developer || node.file_name || node.pr_number || node.node_id}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
};
