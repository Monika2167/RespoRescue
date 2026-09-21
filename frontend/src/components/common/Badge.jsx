import React from "react";

export const Badge = ({
  children,
  variant = "neutral",
  size = "sm",
  icon: Icon,
  className = "",
}) => {
  const variants = {
    success: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
    warning: "bg-amber-500/10 text-amber-300 border-amber-500/20",
    danger: "bg-rose-500/10 text-rose-400 border-rose-500/20",
    info: "bg-sky-500/10 text-sky-300 border-sky-500/20",
    purple: "bg-violet-500/10 text-violet-300 border-violet-500/20",
    neutral: "bg-slate-800 text-slate-300 border-slate-700",
  };

  const sizes = {
    xs: "text-[10px] px-1.5 py-0.5",
    sm: "text-xs px-2.5 py-0.5",
    md: "text-sm px-3 py-1",
  };

  return (
    <span
      className={`inline-flex items-center gap-1.5 font-medium border rounded-full ${
        variants[variant] || variants.neutral
      } ${sizes[size] || sizes.sm} ${className}`}
    >
      {Icon && <Icon className="w-3 h-3" />}
      <span>{children}</span>
    </span>
  );
};
