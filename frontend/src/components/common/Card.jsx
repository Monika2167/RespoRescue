import React from "react";

export const Card = ({
  title,
  subtitle,
  headerAction,
  children,
  footer,
  className = "",
  noPadding = false,
}) => {
  return (
    <div
      className={`bg-[#111726] border border-slate-800/80 rounded-xl shadow-xl shadow-black/40 backdrop-blur overflow-hidden ${className}`}
    >
      {(title || subtitle || headerAction) && (
        <div className="px-5 py-4 border-b border-slate-800/60 flex items-center justify-between gap-4">
          <div>
            {title && (
              <h3 className="text-base font-semibold text-slate-100 tracking-tight">
                {title}
              </h3>
            )}
            {subtitle && (
              <p className="text-xs text-slate-400 mt-0.5">{subtitle}</p>
            )}
          </div>
          {headerAction && <div>{headerAction}</div>}
        </div>
      )}
      <div className={noPadding ? "" : "p-5"}>{children}</div>
      {footer && (
        <div className="px-5 py-3 border-t border-slate-800/60 bg-slate-900/40 text-xs text-slate-400">
          {footer}
        </div>
      )}
    </div>
  );
};
