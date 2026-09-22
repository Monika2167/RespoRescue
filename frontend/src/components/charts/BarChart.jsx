import React from "react";

export const BarChart = ({
  data = [],
  labelKey = "label",
  valueKey = "value",
  maxVal = null,
  height = 180,
  barColor = "#6366f1",
}) => {
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

  const values = data.map((d) => Number(d[valueKey]) || 0);
  const ceiling = maxVal || Math.max(...values, 1);

  return (
    <div className="w-full flex items-end gap-2 pt-6 pb-2" style={{ height }}>
      {data.map((item, idx) => {
        const val = Number(item[valueKey]) || 0;
        const pct = Math.min(100, Math.max(8, (val / ceiling) * 100));

        return (
          <div
            key={idx}
            className="flex-1 flex flex-col items-center gap-1.5 group h-full justify-end"
          >
            <div className="text-[10px] text-slate-400 opacity-0 group-hover:opacity-100 transition whitespace-nowrap">
              {val}
            </div>
            <div
              className="w-full rounded-t-md transition-all duration-300 group-hover:brightness-125"
              style={{
                height: `${pct}%`,
                backgroundColor: barColor,
              }}
            />
            <div className="text-[10px] text-slate-400 truncate max-w-full text-center">
              {item[labelKey]}
            </div>
          </div>
        );
      })}
    </div>
  );
};
