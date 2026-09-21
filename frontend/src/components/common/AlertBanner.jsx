import React from "react";
import { AlertCircle, AlertTriangle, CheckCircle2, Info, X } from "lucide-react";

export const AlertBanner = ({
  type = "info",
  title,
  children,
  onClose,
  className = "",
}) => {
  const styles = {
    info: {
      bg: "bg-sky-500/10 border-sky-500/20 text-sky-200",
      icon: <Info className="w-5 h-5 text-sky-400 shrink-0" />,
    },
    warning: {
      bg: "bg-amber-500/10 border-amber-500/20 text-amber-200",
      icon: <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0" />,
    },
    critical: {
      bg: "bg-rose-500/10 border-rose-500/20 text-rose-200",
      icon: <AlertCircle className="w-5 h-5 text-rose-400 shrink-0" />,
    },
    success: {
      bg: "bg-emerald-500/10 border-emerald-500/20 text-emerald-200",
      icon: <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />,
    },
  };

  const current = styles[type] || styles.info;

  return (
    <div
      className={`flex items-start gap-3 p-4 rounded-xl border text-sm ${current.bg} ${className}`}
    >
      {current.icon}
      <div className="flex-1">
        {title && <h4 className="font-semibold mb-0.5">{title}</h4>}
        <div className="text-xs md:text-sm opacity-90 leading-relaxed">{children}</div>
      </div>
      {onClose && (
        <button
          onClick={onClose}
          className="opacity-70 hover:opacity-100 p-0.5 rounded transition"
        >
          <X className="w-4 h-4" />
        </button>
      )}
    </div>
  );
};
