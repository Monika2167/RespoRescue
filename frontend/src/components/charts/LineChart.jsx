import React, { useState } from "react";

export const LineChart = ({
  data = [],
  xKey = "x",
  yKey = "y",
  label = "Value",
  height = 200,
  strokeColor = "#6366f1",
  fillColor = "rgba(99, 102, 241, 0.12)",
}) => {
  const [hoveredPoint, setHoveredPoint] = useState(null);

  if (!data || data.length === 0) {
    return (
      <div
        style={{ height }}
        className="flex items-center justify-center text-xs text-slate-500 border border-dashed border-slate-800 rounded-lg"
      >
        No chart data available
      </div>
    );
  }

  const values = data.map((d) => Number(d[yKey]) || 0);
  const minVal = Math.min(...values);
  const maxVal = Math.max(...values);
  const range = maxVal - minVal === 0 ? 1 : maxVal - minVal;

  const paddingX = 40;
  const paddingY = 24;
  const chartWidth = 600;
  const chartHeight = height;

  const points = data.map((d, index) => {
    const x =
      paddingX +
      (index / (data.length - 1 || 1)) * (chartWidth - paddingX * 2);
    const y =
      chartHeight -
      paddingY -
      ((Number(d[yKey]) - minVal) / range) * (chartHeight - paddingY * 2);
    return { x, y, raw: d };
  });

  const pathD = points.reduce((acc, p, idx) => {
    return idx === 0 ? `M ${p.x} ${p.y}` : `${acc} L ${p.x} ${p.y}`;
  }, "");

  const areaD = `${pathD} L ${points[points.length - 1].x} ${chartHeight - paddingY} L ${points[0].x} ${chartHeight - paddingY} Z`;

  return (
    <div className="relative w-full overflow-hidden">
      <svg
        viewBox={`0 0 ${chartWidth} ${chartHeight}`}
        className="w-full h-auto overflow-visible"
        style={{ maxHeight: height }}
      >
        <defs>
          <linearGradient id={`grad-${label}`} x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor={strokeColor} stopOpacity={0.25} />
            <stop offset="100%" stopColor={strokeColor} stopOpacity={0.0} />
          </linearGradient>
        </defs>

        {/* Horizontal grid lines */}
        {[0, 0.25, 0.5, 0.75, 1].map((ratio, idx) => {
          const yPos =
            chartHeight - paddingY - ratio * (chartHeight - paddingY * 2);
          const valAtGrid = (minVal + ratio * range).toFixed(1);
          return (
            <g key={idx}>
              <line
                x1={paddingX}
                y1={yPos}
                x2={chartWidth - paddingX}
                y2={yPos}
                stroke="#1e293b"
                strokeDasharray="3 3"
              />
              <text
                x={paddingX - 8}
                y={yPos + 3}
                fill="#64748b"
                fontSize="10"
                textAnchor="end"
              >
                {valAtGrid}
              </text>
            </g>
          );
        })}

        {/* Filled Area */}
        <path d={areaD} fill={`url(#grad-${label})`} />

        {/* Line */}
        <path
          d={pathD}
          fill="none"
          stroke={strokeColor}
          strokeWidth="2.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        />

        {/* Data points */}
        {points.map((p, i) => (
          <circle
            key={i}
            cx={p.x}
            cy={p.y}
            r={hoveredPoint === i ? 5 : 3}
            fill={strokeColor}
            stroke="#0f172a"
            strokeWidth="2"
            className="cursor-pointer transition-all duration-150"
            onMouseEnter={() => setHoveredPoint(i)}
            onMouseLeave={() => setHoveredPoint(null)}
          />
        ))}
      </svg>

      {hoveredPoint !== null && points[hoveredPoint] && (
        <div
          className="absolute z-10 px-2.5 py-1.5 bg-slate-900 border border-slate-700 text-xs rounded-lg shadow-xl pointer-events-none text-slate-100"
          style={{
            left: `${(points[hoveredPoint].x / chartWidth) * 100}%`,
            top: `${(points[hoveredPoint].y / chartHeight) * 100}%`,
            transform: "translate(-50%, -120%)",
          }}
        >
          <div className="font-semibold">
            {points[hoveredPoint].raw[xKey]}
          </div>
          <div className="text-indigo-400">
            {label}: {points[hoveredPoint].raw[yKey]}
          </div>
        </div>
      )}
    </div>
  );
};
